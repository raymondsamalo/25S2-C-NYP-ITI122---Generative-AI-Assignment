
from typing import Optional
from sqlalchemy import BinaryExpression
from sqlmodel import select
from app.db import DB, CustomerAccountStatus, AccountStatus
from app.db.db import Customer

class CustomerAccountStatusService:
    """
    CustomerAccountStatusService is a service class responsible 
    for retrieving customer account status information from the database. 
    
    It provides methods to query customer account status by various 
    criteria such as customer ID, name, or email.

    Methods:
        __init__(db: DB) -> None:
            Initializes the service with a database instance.

        _find_from_query(condition: BinaryExpression) -> Optional[AccountStatus]:
            A private method that executes a database query based on the given condition 
            and retrieves the associated account status.

        find_by_id(customer_id: int) -> Optional[AccountStatus]:
            Retrieves the account status of a customer based on their unique customer ID.

        find_by_name(name: str) -> Optional[int]:
            Retrieves the account status of a customer based on their name.

        find_by_email(email: str) -> Optional[AccountStatus]:
            Retrieves the account status of a customer based on their email address.
    """
    def __init__(self, db: DB) -> None: # pragma: no cover
        self.db = db

    def _find_from_query(self, condition: BinaryExpression) -> Optional[AccountStatus]: # pragma: no cover
        r = None
        with self.db.session() as session:
            results = session.exec(select(CustomerAccountStatus).join(Customer).where(condition)) # type: ignore
            r = results.one_or_none()
        if r is None:
            return None
        return r.account_status

    def find_by_id(self, customer_id: int) -> Optional[AccountStatus]:
        """_summary_

        Args:
            customer_id (int, optional): customer id. 

        Returns:
            Optional[Customer]: _description_
        """
        return self._find_from_query(Customer.ID == customer_id)  # type: ignore

    def find_by_name(self, name: str) -> Optional[AccountStatus]:
        """_summary_

        Args:
            name (str): _description_

        Returns:
            Optional[Customer]: _description_
        """
        return self._find_from_query(Customer.name == name)  # type: ignore

    def find_by_email(self,  email: str) -> Optional[AccountStatus]:
        """_summary_

        Args:
            email (str): _description_

        Returns:
            Optional[Customer]: _description_
        """
        return self._find_from_query(Customer.email == email)  # type: ignore
