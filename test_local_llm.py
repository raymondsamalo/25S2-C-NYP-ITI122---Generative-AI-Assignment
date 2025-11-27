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
# response = ollama.generate(model=model, prompt='Why is the sky blue?')
# print(response['response'])

@tool
def check_loan_recommendation(residency:str) -> bool:
    """
    given residency status determine whether to recommend loan or not
    """
    if residency is None:
        return False
    residency=residency.strip().lower() 
    return residency in ["citizen","permanent-resident"]

@tool
def get_customer_interest_rate_percentage(risk: str) -> Optional[float]:
    """ Get customer interest rate for risk 
    """
    risk = risk.strip().capitalize()
    value = policy_service.get_interest_rate(risk)
    if value is None:
        return 0
    return value


@tool
def get_customer_risk(credit_score: int, account_status: str) -> Optional[str]:
    """ Get customer risk for credit score and account status
    """
    return policy_service.get_risk(credit_score, account_status)


@tool
def get_customer_residency_status(ID: int) -> Optional[str]:
    """ Get customer residency status for a customer ID
    """
    return customer_residency_status_service.find_by_id(ID)


@tool
def get_customer_account_status(ID: int) -> Optional[str]:
    """ Get customer account status for a customer ID
    """
    status = customer_account_status_service.find_by_id(ID)
    if status is None:
        return None
    return str(status)


@tool
def get_customer_credit_score(ID: int) -> Optional[int]:
    """ Get customer credit score for a customer ID
    """
    return customer_credit_score_service.find_by_id(ID)


@tool
def get_customer_info_by_id(ID: int) -> dict:
    """
    Get customer credit score, account status, residency 
    """
    residency = customer_residency_status_service.find_by_id(ID)
    status = customer_account_status_service.find_by_id(ID)
    credit_score = customer_credit_score_service.find_by_id(ID)
    status = str(status)
    residency = str(residency)
    return {
        "credit_score": credit_score,
        "status": status,
        "residency": str(residency)
    }


@tool
def get_customer_id_by_name(name: str) -> Optional[str]:
    """ Get the customer ID for a customer name
    """
    customer = customer_info_service.find_by_name(name)
    if customer is None:
        return None
    return str(customer.ID)


@tool
def get_customer_name_by_id(ID: int) -> Optional[str]:
    """ Get the customer name for a customer id
    Args:
        ID (int): customer id

    Returns:
    """
    customer = customer_info_service.find_by_id(ID)
    if customer is None:
        return None
    return str(customer.name)


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
    # Initialize your Ollama model
    llm = ChatGroq(model=CONFIG.model.groq_model, temperature=0.2)
    # llm = ChatOllama(model=model)
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    response = agent_executor.invoke(
        {"input": "provide information on Kit to make loan recommendation including credit score, account status, risk, interest rate."})
    print(response)
    # Example interaction where the model doesn't need the tool
