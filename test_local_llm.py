from typing import Optional
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from app.dependencies import (CONFIG, customer_account_status_service,
                              customer_credit_score_service,
                              customer_info_service,
                              customer_residency_status_service, db,
                              policy_service)

model = CONFIG.model.version
#response = ollama.generate(model=model, prompt='Why is the sky blue?')
#print(response['response'])

@tool
def get_customer_id_by_name(name:str)->Optional[str]:
    """ Get the customer ID for a customer name

    Args:
        name (str): customer name

    Returns:
    """
    customer=customer_info_service.find_by_name(name)
    if customer is None:
        return None
    return str(customer.ID)

@tool
def get_customer_name_by_id(ID:int)->Optional[str]:
    """ Get the customer name for a customer id
    Args:
        ID (int): customer id

    Returns:
    """
    customer=customer_info_service.find_by_id(ID)
    if customer is None:
        return None
    return str(customer.name)

@tool
def add(a: int, b: int) -> int:
    """Adds two numbers together""" # this docstring gets used as the description
    return a + b # the actions our tool performs
prompt = ChatPromptTemplate.from_messages([
    ("system", "you're a helpful assistant"), 
    ("human", "{input}"), 
    ("placeholder", "{agent_scratchpad}"),
])
if __name__ == "__main__":
    tools=[add, get_customer_id_by_name, get_customer_name_by_id]
    # Initialize your Ollama model
    llm = ChatGroq(model=CONFIG.model.groq_model)
    # llm = ChatOllama(model=model)
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
    response=agent_executor.invoke({"input": "who has customer id 2222", })
    print(response)
    # Example interaction where the model doesn't need the tool
    