from typing import Optional
from app.policies import OverallRiskPolicy, InterestRatePolicy

class PolicyService:
    def __init__(self, overall_risk_doc_path, interest_rate_doc_path) -> None:
        self.overall_risk = OverallRiskPolicy(overall_risk_doc_path)
        self.interest_rate = InterestRatePolicy(interest_rate_doc_path)

    def get_risk(self, credit_score, account_status)->Optional[str]:
        return self.overall_risk.get_risk(credit_score, account_status)
    
    def get_interest_rate(self, risk:Optional[str])->Optional[float]:
        if risk is None:
            return None
        return self.interest_rate.get_interest_rate_percent_for_risk(risk)