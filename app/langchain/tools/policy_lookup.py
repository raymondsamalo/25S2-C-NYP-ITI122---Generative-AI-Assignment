"""
Tool to lookup for bank policy information
"""
from typing import Optional
from langchain_core.tools import tool
from app.dependencies import policy_service
from .utils import (
    format_tool_error,
    format_tool_key_value_table,
    format_policy_data,
    if_none,
    is_valid_account_status,
)


# Instead of feeding to llm using vector store, we define a tool to lookup for policy information
# This allows us to keep the policy data up-to-date without re-indexinging the vector store
# Each time llm needs policy information, it can call this tool with optional parameters
# this tool will then query the policy service.
# The policy service reads the policy data from pdf files and caches the data in memory for fast access.
# In production, the policy service may cache the data in a database and even maintain versioning of the policy data.
#
# This may works better than vector store given that :
# - the policy pdf files may be updated frequently plus
# - there are not that many policy documents to begin with
# - the data is mostly structured even though it is in unstructured file format.
import logging
logger = logging.getLogger(__name__)

@tool
def interest_rate_policy() -> str:
    """ provide a formatted table of interest rate policy information.
    """
    logger.info("interest_rate_policy called")
    policy_dict = policy_service.get_interest_rate_policy_data()
    result = format_policy_data("Interest Rate Policy Information", policy_dict)
    return result

@tool
def overall_risk_policy() -> str:
    """ provide a formatted table of risk  policy information.
    """
    logger.info("overall_risk_policy called")
    policy_dict = policy_service.get_overall_risk_policy_data()
    return format_policy_data("Overall Risk Policy Information", policy_dict)

@tool
def interest_rate_for_risk(risk: str) -> str:
    """ show interest rate the given risk level.
    """
    logger.info("interest_rate_for_risk called")
    if risk is None or risk.strip() == "":
        result = format_tool_error(f"invalid risk {risk}")
    else:
        risk = risk.strip().capitalize()
        interest_rate = policy_service.get_interest_rate(risk)
        interest_rate = str(if_none(interest_rate, "N/A"))
        policy_dict = {risk: interest_rate}
        result = format_tool_key_value_table("Interest Rate Policy Information",
                                         "overall risk", "interest_rate_percentage",
                                         policy_dict)
    return result


@tool
def overall_risk_policy_lookup(credit_score: int, account_status: str ) -> str:
    """ Lookup overall risk with  credit score string,  account status string
    """
    logger.info("overall_risk_policy_lookup called")
    if credit_score is None  or account_status is None or account_status.strip() == "":
        policy_dict = policy_service.get_overall_risk_policy_data()
        return format_policy_data("Overall Risk Policy Information", policy_dict)
    account_status = account_status.strip().capitalize()
    if not is_valid_account_status(account_status):
        return format_tool_error("Invalid account status. It should be one of Good-standing, Delinquent, Closed.")
    policy_dict = policy_service.get_risk_policy(credit_score, account_status)
    if policy_dict is None:
        return format_tool_error("Unexpected error unable to find risk policy")
    error = policy_dict.get("error",None)
    if error:
        return format_tool_error(error)
    return format_policy_data("Overall Risk Policy Information", policy_dict)
