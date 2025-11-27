
from typing import Optional
from sqlalchemy import BinaryExpression
from sqlmodel import select
from app.db import DB, Customer
from app.foundation.design_patterns import singleton


@singleton
class CustomerInfoService:
    """
    Find customer information 
    """
    def __init__(self, db: DB) -> None:
        self.db = db

    def _find_customer_from_query(self, condition: BinaryExpression) -> Optional[Customer]:
        r = []
        with self.db.session() as session:
            results = session.exec(select(Customer).where(condition))
            r = results.one_or_none()
        return r

    def find_customer_with_id(self, customer_id: int) -> Optional[Customer]:
        """_summary_

        Args:
            customer_id (int, optional): customer id. 

        Returns:
            Optional[Customer]: _description_
        """
        return self._find_customer_from_query(Customer.id == customer_id)  # type: ignore

    def find_customer_with_name(self, name: str) -> Optional[Customer]:
        """_summary_

        Args:
            name (str): _description_

        Returns:
            Optional[Customer]: _description_
        """
        return self._find_customer_from_query(Customer.name == name)  # type: ignore

    def find_customer_with_email(self,  email: str) -> Optional[Customer]:
        """_summary_

        Args:
            email (str): _description_

        Returns:
            Optional[Customer]: _description_
        """
        return self._find_customer_from_query(Customer.email == email)  # type: ignore
