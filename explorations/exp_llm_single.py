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
    customer_lookup, interest_rate_policy_lookup, overall_risk_policy_lookup, interest_rate_policy)
from app.dependencies import llm, CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

prompt =  """
     you are a helpful assistant for a loan officer in a bank. 
     Only present information from tools.
     if user ask for customer name or customer email or customer credit score, call customer_lookup. 
     if user ask for customer risk, call customer_lookup, using its output call overall_risk_policy_lookup
     if user ask for bank risk policy, call overall_risk_policy_lookup and show its output.
     if user ask for interest rate policy, call interest_rate_policy and show its output.
     if user ask for customer interest rate, call interest_rate_policy_lookup.
     be concise. 
     only answer what is asked by user. 
     """

if __name__ == "__main__":
    MAX_RETRIES = 3
    if CONFIG.model.choice == "groq":
        print("Experiment with remote groq LLM and single customer lookup tool")
        print(f"Using {CONFIG.model.choice} model {CONFIG.model.groq_model}")
    else:
        print("Experiment with local LLM and single customer lookup tool")
        print(f"Using {CONFIG.model.choice} model {CONFIG.model.ollama_model}")
    tools = [customer_lookup, interest_rate_policy_lookup, overall_risk_policy_lookup, interest_rate_policy]
    agent = create_agent(llm, tools=tools, system_prompt=prompt, checkpointer=InMemorySaver())
    #agent = create_agent(llm, tools=tools, system_prompt=prompt)
    thread_id = threading.get_ident()
    while True:
        user_input = input("Enter your question (or 'exit' to quit): ")
        if user_input.strip().lower() == 'exit':
            break
        try:
            for retry in range(MAX_RETRIES):
                try:
                    result = agent.invoke({"messages": [{"role": "user", "content": user_input}]},
                                          {"configurable": {"thread_id": str(thread_id)}},
                                          )
                    print(f"User  : {user_input}")
                    messages = result["messages"]
                    # Find the last assistant message (the graph may end on a ToolMessage otherwise)
                    last_ai = next(m for m in reversed(messages) if getattr(m, "type", None) == "ai")
                    # Safely extract human-readable text
                    final_text = last_ai.text
                    print(f"Agent : {final_text}")
                    break
                except APIError as e:
                    print(
                        f"A general API Error occurred: {e.message} on attempt {retry+1}/{MAX_RETRIES}. Retrying...")
                    time.sleep(2)  # wait before retrying
        except ValidationError as ve:
            print(f"Validation Error: {str(ve)}")
            print("Please rephrase the prompt and try again.")
