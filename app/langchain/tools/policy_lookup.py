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
    """ provide a formatted table of interest rate policy information containing overall risk and interest rate percentage.
    """
    logger.info("interest_rate_policy called")
    policy_dict = policy_service.get_interest_rate_policy_data()
    result = format_policy_data("Interest Rate Policy Information", policy_dict)
    return result

@tool
def interest_rate_policy_lookup(risk: str) -> str:
    """ Lookup interest rate policy information with optional risk level string.
        return the interest rate percentage for the given risk level.
    """
    logger.info("interest_rate_policy_lookup called")
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
def overall_risk_policy_lookup(credit_score: Optional[int]=None, account_status: Optional[str]=None, customer_info:Optional[dict]=None ) -> str:
    """ Lookup overall risk with optional credit score string, optional account status string or optional customer_info dictionary.
        return a formatted table of overall risk policy information containing credit score range, account status, and overall risk level.
        If both credit score and account status are provided, return the overall risk level.
        If any of the parameters is missing or invalid but customer_info is provided,
         use the customer_info dictionary to get the credit score and account status.
        If both parameters are missing or invalid, return the full overall risk policy information.
        if one of the parameters is missing or invalid, return an error message.
    """
    logger.info("overall_risk_policy_lookup called")
    if customer_info is not None:
        credit_score = customer_info.get("credit_score", None)
        account_status = customer_info.get("account_status", None)
    if credit_score is None  or account_status is None or account_status.strip() == "":
        policy_dict = policy_service.get_overall_risk_policy_data()
        return format_policy_data("Overall Risk Policy Information", policy_dict)
    account_status = account_status.strip().capitalize()
    if not is_valid_account_status(account_status):
        return format_tool_error("Invalid account status. It should be one of Good-standing, Delinquent, Closed.")
    policy_dict = policy_service.get_risk_policy(credit_score, account_status)
    if policy_dict is None:
        return format_tool_error("Unexpected error unable to find risk policy")
    if "error" in policy_dict.keys():
        return format_tool_error(policy_dict["error"])
    return format_policy_data("Overall Risk Policy Information", policy_dict)
