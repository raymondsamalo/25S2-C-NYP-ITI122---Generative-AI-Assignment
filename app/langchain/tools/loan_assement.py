from langchain_core.tools import tool
from app.dependencies import policy_service, customer_credit_score_service, customer_account_status_service

import logging
logger = logging.getLogger(__name__)

from .utils import is_valid_credit_score, is_valid_account_status, format_tool_error

@tool
def loan_assement(name: str, residency: str, account_status: str, credit_score: str) -> str:
    """ 
    Perform loan assesment given user information like name, residency, account_status, credit score
    """
    logger.info("loan_assement tool called %s %s %s %s",
                name, residency, account_status, credit_score)
    if not is_valid_credit_score(credit_score):
        credit_score_value=customer_credit_score_service.find_by_name(name=name)
    else:
        credit_score_value=int(credit_score)
    if not is_valid_account_status(account_status):
        account_status_value=customer_account_status_service.find_by_name(name=name)
        if account_status_value is not None:
            account_status = str(account_status_value)
        else:
            return format_tool_error("failed to get account status")
        
    risk = policy_service.get_risk(credit_score=credit_score_value, account_status=account_status)
    interest_rate = policy_service.get_interest_rate(risk=risk)
    logger.info("loan_assement tool result risk %s interest %s", risk, interest_rate)
    report = f"""
        Name            : {name}
        Residency       : {residency}
        Account Status  : {account_status}
        Credit Score    : {credit_score}
        Risk            : {risk}
    """
    if residency == "non-resident":
        report += f"\n Loan is not recommended given {name} is a non-resident."
        report += f"\n If the customer managed to obtain residency, the interest rate recommended is {interest_rate} %"
    else:
        report += "\n Loan is recommended for {name} with interest rate {interest_rate} %"
    return report
