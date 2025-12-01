""" 
Experiment using local LLM
"""
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

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.langchain.tools import (
    customer_lookup, interest_rate_policy_lookup, overall_risk_policy_lookup)
from app.dependencies import llm, CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

prompt =  """
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

if __name__ == "__main__":
    MAX_RETRIES = 3
    if CONFIG.model.choice == "groq":
        print("Experiment with remote groq LLM and single customer lookup tool")
        print(f"Using {CONFIG.model.choice} model {CONFIG.model.groq_model}")
    else:
        print("Experiment with local LLM and single customer lookup tool")
        print(f"Using {CONFIG.model.choice} model {CONFIG.model.ollama_model}")
    tools = [customer_lookup, interest_rate_policy_lookup, overall_risk_policy_lookup]
    agent = create_agent(llm, tools=tools, system_prompt=prompt, checkpointer=InMemorySaver())
    thread_id = threading.get_ident()
    while True:
        user_input = input("Enter your question (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        try:
            for retry in range(MAX_RETRIES):
                try:
                    result = agent.invoke({"messages": [{"role": "user", "content": user_input}]},
                                          {"configurable": {"thread_id": str(thread_id)}})
                    for message in result["messages"]:
                        if isinstance(message, AIMessage):
                            print(f"Agent response: {message.content}")
                    break
                except APIError as e:
                    print(
                        f"A general API Error occurred: {e.message} on attempt {retry+1}/{MAX_RETRIES}. Retrying...")
                    time.sleep(2)  # wait before retrying
        except ValidationError as ve:
            print(f"Validation Error: {str(ve)}")
            print("Please rephrase the prompt and try again.")
