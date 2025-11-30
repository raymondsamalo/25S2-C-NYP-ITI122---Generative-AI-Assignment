"""
Tool to lookup customer information by identifier which can be customer ID, email, or name. 
After multiple experiments, we found that having a single comprehensive tool 
improves the model's ability to retrieve and present customer information effectively.
It is also easier to maintain and extend in the future.
"""
from langchain_core.tools import tool
from app.dependencies import (customer_account_status_service,
                              customer_credit_score_service,
                              customer_info_service,
                              customer_residency_status_service)
from .utils import (
    format_tool_error, format_tool_output,
    if_none,
    is_valid_customer_id, is_valid_email
)

import logging

import logging
logger = logging.getLogger(__name__)

@tool
def customer_lookup(identifier: str) -> str:
    """ Lookup customer information by identifier which can be customer ID, email, or name.
    return customer information including customer ID, name, email, residency status, account status, and credit score.
    """
    logger.info("Customer lookup tool called with identifier: %s", identifier)
    if identifier is None:
        error = format_tool_error("Identifier is required.")
        logger.info("Customer lookup error: %s", error)
        return error
    identifier = identifier.strip()
    if is_valid_customer_id(identifier):
        customer_id = int(identifier)
        customer = customer_info_service.find_by_id(customer_id)
    elif is_valid_email(identifier):
        customer = customer_info_service.find_by_email(identifier)
        logger.info("Customer lookup  %s return %s", identifier, customer)
        if customer is None:
            return format_tool_error(f"Customer with email '{identifier}' not found.")
        customer_id = customer.ID
    else:
        identifier = identifier.capitalize()
        customer = customer_info_service.find_by_name(identifier)
        logger.info("Customer lookup  %s return %s", identifier, customer)
        if customer is None:
            return format_tool_error(f"Customer '{identifier}' not found.")
        customer_id = customer.ID
    credit_score = if_none(
        customer_credit_score_service.find_by_id(customer_id), "N/A")
    residency = str(
        if_none(customer_residency_status_service.find_by_id(customer_id), "N/A"))
    account_status = str(
        if_none(customer_account_status_service.find_by_id(customer_id), "N/A"))
    customer_dict = {
        "customer_id": customer_id,
        "name": customer.name,
        "email": customer.email,
        "residency": residency,
        "account_status": account_status,
        "credit_score": credit_score
    }
    logger.info("Customer lookup  %s return %s", identifier, customer_dict)
    return format_tool_output("Customer Information", customer_dict)
