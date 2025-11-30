

from typing import Any, Generator, Iterator
from app.agents.agent import Agent
import time
# in subfolder/my_script.py
import sys
import os
import threading
import logging
from groq import APIError
from langgraph.checkpoint.memory import InMemorySaver
from langchain.messages import AIMessage
from pydantic import ValidationError
from langchain.agents import create_agent
from app.langchain.tools import (
    customer_lookup, interest_rate_policy_lookup, overall_risk_policy_lookup)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MAX_RETRIES = 3
SYSTEM_PROMPT = """
     you are a helpful assistant for a loan officer in a bank. 
     You are able to provide customer information and bank policy information.
     You have access to the following tools:
     - customer_lookup: to lookup customer information by identifier which can be customer ID, email, or name.
     - overall_risk_policy_lookup: to lookup overall risk level based on customer's credit score and account status.
     - interest_rate_policy_lookup: to lookup interest rate percentage based on the customer's overall risk level.
     
     When a user asks for a loan recommendation for a customer, you should:
     - use the customer_lookup tool to get customer information including credit score, residency status, account status.
     - use the overall_risk_policy_lookup tool to get the overall risk level based on the customer's credit score and account status.
     - use the interest_rate_policy_lookup tool to get the interest rate percentage based on the customer's overall risk level.
     - provide a final recommendation on whether to approve the loan or not, and the interest rate percentage if approved.
        Always use the tools to get the information you need.

     Do not make up any customer information or bank policy information.
     Do not guess the overall risk level or interest rate percentage.
     Always use the tools to get the information.
     If the user provides incomplete or invalid customer identifier,
     inform the user to provide a valid customer ID, email, or name.
    
     Always provide information obtained from the tools only.
     Always cite the source of your information from the tools.
     Always explain your reasoning step by step.
     Always summarize your final recommendation clearly.
     Be concise, professional and polite in your response.
     """


class LoanAgent(Agent):
    """ An agent specialized for loan recommendations using customer lookup and policy lookup tools.
    """

    def __init__(self, model: BaseChatModel):
        super().__init__(model)
        tools = [customer_lookup, interest_rate_policy_lookup,
                 overall_risk_policy_lookup]
        self.agent = create_agent(
            model, tools=tools, system_prompt=SYSTEM_PROMPT, checkpointer=InMemorySaver())
        self.thread_id = str(threading.get_ident())

    def get_response(self, query: str) -> str:
        try:
            for retry in range(MAX_RETRIES):
                try:
                    result = self.agent.invoke({"messages": [{"role": "user", "content": query}]},
                                               {"configurable": {"thread_id": self.thread_id}})
                    responses = []
                    for message in result["messages"]:
                        if isinstance(message, AIMessage):
                            responses.append(message.content)
                    return "\n".join(responses)
                except APIError as e:
                    logger.error(
                        "A general API Error occurred: %s on attempt %d/%d. Retrying...", str(e), retry+1, MAX_RETRIES)
                    time.sleep(0.2)  # wait before retrying
        except ValidationError as ve:
            logger.error(f"Validation Error: {str(ve)}")
            return "Please rephrase the prompt and try again."
        except Exception as e:
            logger.error(f"Unexpected Error: {str(e)}")
            return f"Unexpected error kindly {str(e)}, feel free to try again."

    def stream_response(self, query: str) -> Iterator[dict[str, Any] | Any]:
        try:
            for retry in range(MAX_RETRIES):
                try:
                    result = self.agent.stream({"messages": [{"role": "user", "content": query}]},
                                               {"configurable": {"thread_id": self.thread_id}}, stream_mode="messages")
                    for message in result["messages"]:
                        if isinstance(message, AIMessage):
                             yield message.content
                except APIError as e:
                    logger.error(
                        "A general API Error occurred: %s on attempt %d/%d. Retrying...", str(e), retry+1, MAX_RETRIES)
                    time.sleep(0.2)  # wait before retrying
        except ValidationError as ve:
            logger.error(f"Validation Error: {str(ve)}")
            yield "Please rephrase the prompt and try again."
        except Exception as e:
            logger.error(f"Unexpected Error: {str(e)}")
            yield f"Unexpected error kindly {str(e)}, feel free to try again."