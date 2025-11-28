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

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.dependencies import llm
from app.langchain.tools import (check_loan_recommendation, get_customer_id_by_name,
                       get_customer_info_by_id,
                       get_customer_interest_rate_percentage,
                       get_customer_name_by_id, get_customer_risk)

prompt = ChatPromptTemplate.from_messages([
    ("system", "you're a helpful assistant"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
if __name__ == "__main__":
    tools = [
        check_loan_recommendation,
        get_customer_info_by_id,
        get_customer_id_by_name,
        get_customer_risk,
        get_customer_interest_rate_percentage,
        get_customer_name_by_id]
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
    done = False
    retry = 0
    while not done:
        try:
            response = agent_executor.invoke(
                {"input": "provide information on Matt and check whether to provide loan recommendation including credit score, account status, risk, interest rate."})
            print(response["output"])
            done = True
        except APIError:
            # print(f"A general API Error occurred: {e}")
            retry += 1
            if retry > 3:
                time.sleep(0.5)
                done = True

    # Example interaction where the model doesn't need the tool
