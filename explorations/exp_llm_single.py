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
from app.dependencies import llm, CONFIG
from app.langchain.tools import (overall_risk_policy,
                                 customer_lookup, interest_rate_for_risk, overall_risk_policy_lookup, interest_rate_policy)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

prompt = """
   you are a helpful assistant for a loan officer in a bank. 
     You have access to the following tools:
     - customer_lookup: to lookup customer information by identifier which can be customer ID, email, or name.
     - overall_risk_policy_lookup: to lookup overall risk level based on customer's credit score and account status.
     - interest_rate_for_risk: to lookup interest rate percentage based on the customer's overall risk level.
     - overall_risk_policy: show the bank risk policy
     - interest_rate_policy: show the bank interest rate policy

    You are able to provide customer information. 
    You are able to show bank policies.

     When a user asks for a loan recommendation for a customer, you should:
     - use the customer_lookup tool to get customer information including credit score, residency status, account status.
     - use the overall_risk_policy_lookup tool to get the overall risk level based on the customer's credit score and account status.
     - use the interest_rate_for_risk tool to get the interest rate percentage based on the customer's overall risk level.
     - provide a final recommendation on whether to approve the loan or not, and the interest rate percentage if approved.
     - do not recommend loan to a non-resident but still show the interest rate and other information

     Do not make up any customer information or bank policy information.
     Do not guess the overall risk level or interest rate percentage.
     Always provide interest rate percentage from interest_rate_policy_lookup only.
     
     If the user provides incomplete or invalid customer identifier,
     inform the user to provide a valid customer ID, email, or name.
    
     Always provide information obtained from the tools only.
     Always cite the source of your information from the tools.
     Always explain your reasoning step by step.
     Always summarize your final recommendation clearly.
     Be concise, professional and polite in your response.
     Do not assume that user is asking for loan recommendation for a customer unless explicitly asked.
     Provide all numerical results using exactly 3 decimal places.
     
    """

if __name__ == "__main__":
    MAX_RETRIES = 3
    if CONFIG.model.choice == "groq":
        print("Experiment with remote groq LLM and single customer lookup tool")
        print(f"Using {CONFIG.model.choice} model {CONFIG.model.groq_model}")
    else:
        print("Experiment with local LLM and single customer lookup tool")
        print(f"Using {CONFIG.model.choice} model {CONFIG.model.ollama_model}")
    tools = [customer_lookup, overall_risk_policy, interest_rate_for_risk,
             overall_risk_policy_lookup, interest_rate_policy]
    agent = create_agent(llm, tools=tools, system_prompt=prompt)
    # agent = create_agent(llm, tools=tools, system_prompt=prompt)
    thread_id = threading.get_ident()
    while True:
        user_input = input("Enter your question (or 'exit' to quit): ")
        if user_input.strip().lower() == 'exit':
            break
        try:
            for retry in range(MAX_RETRIES):
                try:
                    result = agent.invoke({"messages": [{"role": "user", "content": user_input}]},
                                          {"configurable": {
                                              "thread_id": str(thread_id)}},
                                          )
                    print(f"User  : {user_input}")
                    print(result)
                    messages = result["messages"]
                    # Find the last assistant message (the graph may end on a ToolMessage otherwise)
                    for m in messages:
                        if getattr(m, "type", None) == "ai":
                            print("Agent :", m.text)
                    break
                except APIError as e:
                    print(
                        f"A general API Error occurred: {e.message} on attempt {retry+1}/{MAX_RETRIES}. Retrying...")
                    time.sleep(2)  # wait before retrying
        except ValidationError as ve:
            print(f"Validation Error: {str(ve)}")
            print("Please rephrase the prompt and try again.")
