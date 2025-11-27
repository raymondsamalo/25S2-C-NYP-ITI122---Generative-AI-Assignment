from .db import SqliteDB
from .services import CustomerInfoService, CustomerAccountStatusService, CustomerCreditScoreService, ResidencyStatusService
db = SqliteDB()
customer_info_service = CustomerInfoService(db)
customer_account_status_service = CustomerAccountStatusService(db)
customer_credit_score_service = CustomerCreditScoreService(db)
customer_residency_status_service = ResidencyStatusService(db)
