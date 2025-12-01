
from typing import Optional
from sqlalchemy import BinaryExpression
from sqlmodel import select
from app.db import DB, CustomerCreditScore
from app.db.db import Customer

class CustomerCreditScoreService:
    """
    Find customer information 
    """
    def __init__(self, db: DB) -> None:
        self.db = db

    def _find_from_query(self, condition: BinaryExpression) -> Optional[int]:
        r = None
        with self.db.session() as session:
            results = session.exec(select(CustomerCreditScore).join(Customer).where(condition)) # type: ignore
            r = results.one_or_none()
        if r is None:
            return None
        return r.credit_score

    def find_by_id(self, customer_id: int) -> Optional[int]:
        """_summary_

        Args:
            customer_id (int, optional): customer id. 

        Returns:
            Optional[Customer]: _description_
        """
        return self._find_from_query(Customer.ID == customer_id)  # type: ignore

    def find_by_name(self, name: str) -> Optional[int]:
        """_summary_

        Args:
            name (str): _description_

        Returns:
            Optional[Customer]: _description_
        """
        return self._find_from_query(Customer.name == name)  # type: ignore

    def find_by_email(self,  email: str) -> Optional[int]:
        """_summary_

        Args:
            email (str): _description_

        Returns:
            Optional[Customer]: _description_
        """
        return self._find_from_query(Customer.email == email)  # type: ignore
