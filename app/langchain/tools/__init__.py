from .tools import (
    check_loan_recommendation,
    get_customer_info_by_id,
    get_customer_id_by_name,
    get_customer_risk,
    get_customer_interest_rate_percentage,
    get_customer_name_by_id
)
from .customer_lookup import customer_lookup
from .policy_lookup import interest_rate_for_risk, overall_risk_policy_lookup, interest_rate_policy, overall_risk_policy
from .loan_assement import loan_assement