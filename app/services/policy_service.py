from typing import Optional
from app.policies import OverallRiskPolicy, InterestRatePolicy


class PolicyService:
    def __init__(self, overall_risk_doc_path, interest_rate_doc_path) -> None:
        self.overall_risk = OverallRiskPolicy(overall_risk_doc_path)
        self.interest_rate = InterestRatePolicy(interest_rate_doc_path)

    def get_risk(self, credit_score, account_status) -> Optional[str]:
        """ Get overall risk level based on credit score and account status. """
        return self.overall_risk.get_risk(credit_score, account_status)

    def get_risk_policy(self, credit_score, account_status) -> Optional[dict]:
        """ Get overall risk policy details based on credit score and account status. """
        return self.overall_risk.get_risk_policy(credit_score, account_status)
    
    def get_interest_rate(self, risk: Optional[str]) -> Optional[float]:
        """ Get interest rate percentage for the given risk level. """
        if risk is None:
            return None
        return self.interest_rate.get_interest_rate_percent_for_risk(risk)

    def get_overall_risk_policy_data(self):
        """ Get overall risk policy data as dict with header and data. """
        return self.overall_risk.policy_data()

    def get_interest_rate_policy_data(self):
        """ Get interest rate policy data as dict with header and data. """
        return self.interest_rate.policy_data()
