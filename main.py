from typing import Optional
from app.db import data_path, create_and_populate_db, Customer
from app.dependencies import customer_info_service,db, customer_residency_status_service
if __name__ == "__main__":
    print(data_path)
    create_and_populate_db(db)
    c:Optional[Customer]=customer_info_service.find_by_name("Loren")
    if c:
        print(c.email)
        residency=customer_residency_status_service.find_by_id(c.ID)  # type: ignore
        print(residency)