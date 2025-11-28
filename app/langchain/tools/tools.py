"""
LangChain Tools Definition
"""
from typing import Optional
from langchain_core.tools import tool
from app.dependencies import (customer_account_status_service,
                              customer_credit_score_service,
                              customer_info_service,
                              customer_residency_status_service,
                              policy_service)


@tool
def check_loan_recommendation(residency: str, risk: str) -> bool:
    """
     check whether to recommend loan based on residency and overall risk
    """
    if risk is None or residency is None:
        return False
    risk = risk.strip().lower()
    residency = residency.strip().lower()
    return residency in ["citizen", "permanent-resident"] and risk in ['medium', 'low']


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
def get_customer_residency_status(customer_id: int) -> Optional[str]:
    """ Get customer residency status for a customer customer_id
    """
    return customer_residency_status_service.find_by_id(customer_id)


@tool
def get_customer_account_status(customer_id: int) -> Optional[str]:
    """ Get customer account status for a customer customer_id
    """
    status = customer_account_status_service.find_by_id(customer_id)
    if status is None:
        return None
    return str(status)


@tool
def get_customer_credit_score(customer_id: int) -> Optional[int]:
    """ Get customer credit score for a customer customer_id
    """
    return customer_credit_score_service.find_by_id(customer_id)


@tool
def get_customer_info_by_id(customer_id: int) -> dict:
    """
    Get customer credit score, account status, residency,email , name given an integer customer_id
    """
    info = customer_info_service.find_by_id(customer_id)
    if info is None:
        return {}
    residency = customer_residency_status_service.find_by_id(customer_id)
    status = customer_account_status_service.find_by_id(customer_id)
    credit_score = customer_credit_score_service.find_by_id(customer_id)
    status = str(status)
    residency = str(residency)
    return {
        "email": info.email,
        "name" : info.name,
        "credit_score": credit_score,
        "status": status,
        "residency": str(residency)
    }


@tool
def get_customer_id_by_name(name: str) -> Optional[str]:
    """ Get the integer customer_id for a customer name string
    """
    customer = customer_info_service.find_by_name(name)
    if customer is None:
        return None
    return str(customer.ID)


@tool
def get_customer_name_by_id(customer_id: int) -> Optional[str]:
    """ Get the customer name for a customer id
    Args:
        customer_id (int): customer id

    Returns:
    """
    customer = customer_info_service.find_by_id(customer_id)
    if customer is None:
        return None
    return str(customer.name)
