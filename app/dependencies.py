from .db import SqliteDB
from .services import CustomerInfoService
db = SqliteDB()
customer_info_service = CustomerInfoService(db)