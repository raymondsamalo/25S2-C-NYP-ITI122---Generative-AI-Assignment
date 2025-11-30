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
    is_valid_credit_score,
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

@tool
def interest_rate_policy_lookup(risk: Optional[str]) -> str:
    """ Lookup interest rate policy information with optional risk level string.
        return a formatted table of interest rate policy information containing overall risk and interest rate percentage.
        or if risk level is provided, return the interest rate percentage for the given risk level.
    """
    if risk is None or risk.strip() == "":
        policy_dict = policy_service.get_interest_rate_policy_data()
        result = format_policy_data("Interest Rate Policy Information", policy_dict)
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
def overall_risk_policy_lookup(credit_score: Optional[str]=None, account_status: Optional[str]=None, customer_info:Optional[dict]=None ) -> str:
    """ Lookup overall risk with optional credit score string, optional account status string or optional customer_info dictionary.
        return a formatted table of overall risk policy information containing credit score range, account status, and overall risk level.
        If both credit score and account status are provided, return the overall risk level.
        If any of the parameters is missing or invalid but customer_info is provided,
         use the customer_info dictionary to get the credit score and account status.
        If both parameters are missing or invalid, return the full overall risk policy information.
        if one of the parameters is missing or invalid, return an error message.
    """
    if customer_info is not None:
        credit_score = customer_info.get("credit_score", None)
        account_status = customer_info.get("account_status", None)
    if credit_score is None or credit_score.strip() == "" or account_status is None or account_status.strip() == "":
        policy_dict = policy_service.get_overall_risk_policy_data()
        return format_policy_data("Overall Risk Policy Information", policy_dict)
    credit_score = credit_score.strip()
    account_status = account_status.strip().capitalize()
    if not is_valid_credit_score(credit_score):
        return format_tool_error("Invalid credit score. It should be an integer between 300 and 850.")
    if not is_valid_account_status(account_status):
        return format_tool_error("Invalid account status. It should be one of Good-standing, Delinquent, Closed.")
    policy_dict = policy_service.get_risk_policy(int(credit_score), account_status)
    if "error" in policy_dict:
        return format_tool_error(policy_dict["error"])
    return format_policy_data("Overall Risk Policy Information", policy_dict)
