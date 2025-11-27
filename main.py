from typing import Optional
from app.db import data_path, create_and_populate_db, Customer
from app.dependencies import customer_info_service, db, customer_residency_status_service, customer_credit_score_service, policy_service, customer_account_status_service
if __name__ == "__main__":
    print(data_path)
    create_and_populate_db(db)
    c: Optional[Customer] = customer_info_service.find_by_name("Hilda")
    if c:
        residency = customer_residency_status_service.find_by_id(c.ID)  # type: ignore
        credit_score = customer_credit_score_service.find_by_id(c.ID) # type: ignore
        account_status = customer_account_status_service.find_by_id(c.ID) # type: ignore
        risk=policy_service.get_risk(credit_score, account_status)
        interest=policy_service.get_interest_rate(risk)
        print(c)
        print(risk)
        print(interest)
        print(account_status)
        print(credit_score)
        print(residency)
        
