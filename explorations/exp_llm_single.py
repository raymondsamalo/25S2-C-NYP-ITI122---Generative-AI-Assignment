""" 
Experiment using local LLM
"""
import time
# in subfolder/my_script.py
import sys
import os

from groq import APIError
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from pydantic import ValidationError
from langchain_core.agents import 

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.langchain.tools import (
    customer_lookup, interest_rate_policy_lookup, overall_risk_policy_lookup)
from app.dependencies import llm, CONFIG

prompt = ChatPromptTemplate.from_messages([
    ("system", """
you're a helpful assistant for a loan officer in a bank, providing customer and bank policy information to help the loan officer make loan recommendations.
     Use the provided tools to lookup customer information and bank policy information as needed.
  
     Do not make up any information - if you don't know the answer, just say you don't know.
     
     Do not recommend a loan if the customer is non-resident.
     
     To recommend a loan follow these steps:
     - use the customer_lookup tool to get customer information including credit score, residency status, account status.
     - use the overall_risk_policy_lookup tool to get the overall risk level based on the customer's credit score and account status.
     - use the interest_rate_policy_lookup tool to get the interest rate percentage based on the customer's 
    
     Always provide information obtained from the tools only.
     Always cite the source of your information from the tools.
     Always explain your reasoning step by step.
     Always summarize your final recommendation clearly.
     Be concise, professional and polite in your response.
     """),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
if __name__ == "__main__":
    MAX_RETRIES = 3
    if CONFIG.model.choice == "groq":
        print("Experiment with remote groq LLM and single customer lookup tool")
        print(f"Using {CONFIG.model.choice} model {CONFIG.model.groq_model}")
    else:
        print("Experiment with local LLM and single customer lookup tool")
        print(f"Using {CONFIG.model.choice} model {CONFIG.model.ollama_model}")
    tools = [customer_lookup, interest_rate_policy_lookup, overall_risk_policy_lookup]
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
    while True:
        user_input = input("Enter your question (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        try:
            for retry in range(MAX_RETRIES):
                try:
                    response = agent_executor.invoke(
                        {"input": user_input})
                    print(response["output"])
                    break
                except APIError as e:
                    print(
                        f"A general API Error occurred: {e.message} on attempt {retry+1}/{max_retries}. Retrying...")
                    time.sleep(2)  # wait before retrying
        except ValidationError as ve:
            print(f"Validation Error: {str(ve)}")
    # Example interaction where the model doesn't need the tool
