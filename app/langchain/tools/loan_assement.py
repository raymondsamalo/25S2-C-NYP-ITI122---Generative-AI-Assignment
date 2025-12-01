from langchain_core.tools import tool
from app.dependencies import policy_service

import logging
logger = logging.getLogger(__name__)


@tool
def loan_assement(name: str, residency: str, account_status: str, credit_score: str) -> str:
    """ 
    Perform loan assesment given user information like name, residency, account_status, credit score
    """
    logger.info("loan_assement tool called %s %s %s %s",
                name, residency, account_status, credit_score)
    risk = policy_service.get_risk(
        credit_score=int(credit_score), account_status=account_status)
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
