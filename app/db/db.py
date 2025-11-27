from abc import ABC, abstractmethod
import pathlib
from enum import StrEnum
from sqlalchemy import Engine
from sqlalchemy.dialects import postgresql  # Works for SQLite too
from sqlmodel import Column, Field, Session, SQLModel, create_engine, Enum

from app.foundation.design_patterns import singleton

script_directory = pathlib.Path(__file__).parent
data_path = script_directory.parent.parent / 'data' / 'database.sqlite'


class AccountStatus(StrEnum):
    GOOD_STANDING = "Good-standing"
    CLOSED = "Closed"
    DELIQUENT = "Delinquent"


class ResidencyStatus(StrEnum):
    PERMANENT_RESIDENT = "permanent-resident"
    CITIZEN = "citizen"
    NON_RESIDENT = "non-resident"


class Customer(SQLModel, table=True):
    ID: int | None = Field(default=None, primary_key=True)
    name: str
    email: str


class CustomerCreditScore(SQLModel, table=True):
    ID: int | None = Field(default=None, primary_key=True,
                           foreign_key='customer.ID')
    credit_score: int | None = None


class CustomerAccountStatus(SQLModel, table=True):
    ID: int | None = Field(default=None, primary_key=True,
                           foreign_key='customer.ID')
    account_status:  AccountStatus = Field(
        default=None, sa_column=Column(Enum(AccountStatus)))


class CustomerPRStatus(SQLModel, table=True):
    ID: int | None = Field(default=None, primary_key=True,
                           foreign_key='customer.ID')
    pr_status: bool


class DB(ABC):
    def __init__(self) -> None:
        self._engine = None

    @property
    def engine(self):
        """
        create database engine and ensure only 1 engine per object instance
        """
        if self._engine is None:
            self._engine = self.create_engine()
        return self._engine

    @abstractmethod
    def create_engine(self) -> Engine:
        """
        actual engine creation, override this to customise
        """

    def session(self) -> Session:
        """
            return database session
        """
        return Session(self.engine)

    def add_if_not_exist(self, session, record):
        pass


@singleton
class SqliteDB(DB):
    """
    Database wrapper
    """

    def __init__(self) -> None:
        super().__init__()
        self.path = "sqlite:///"+data_path.resolve().as_posix()

    def create_engine(self):
        return create_engine(self.path)

    def session(self):
        """
            return database session
        """
        return Session(self.engine)

    def add_if_not_exist(self, session, record):
        """
        insert into database but ignore on conflict 
        """
        statement = (
            postgresql.insert(record.__class__)
            .values(**record.model_dump(exclude_unset=True))
            .on_conflict_do_nothing()
        )
        session.exec(statement)


def create_and_populate_db(db):
    """
    populate database with initial data
    """
    SQLModel.metadata.create_all(db.engine)
    records = [
        Customer(ID=1111, name="Loren", email="loren@gmail.com"),
        Customer(ID=2222, name="Matt", email="matt@yahoo.com"),
        Customer(ID=3333, name="Hilda", email="halida@gmail.com"),
        Customer(ID=4444, name="Andy", email="andy@gmail.com"),
        Customer(ID=5555, name="Kit", email="kit@yahho.com"),
        CustomerAccountStatus(
            ID=1111, account_status=AccountStatus.GOOD_STANDING),
        CustomerAccountStatus(
            ID=2222, account_status=AccountStatus.CLOSED),
        CustomerAccountStatus(
            ID=3333, account_status=AccountStatus.DELIQUENT),
        CustomerAccountStatus(
            ID=4444, account_status=AccountStatus.GOOD_STANDING),
        CustomerAccountStatus(
            ID=5555, account_status=AccountStatus.DELIQUENT),
        CustomerCreditScore(ID=1111, credit_score=455),
        CustomerCreditScore(ID=2222, credit_score=685),
        CustomerCreditScore(ID=3333, credit_score=825),
        CustomerCreditScore(ID=4444, credit_score=840),
        CustomerCreditScore(ID=5555, credit_score=350),
        CustomerPRStatus(ID=2222, pr_status=True),
        CustomerPRStatus(ID=4444, pr_status=False),
    ]
    with db.session() as session:
        for record in records:
            db.add_if_not_exist(session, record)
        session.commit()


"""
The officer logs into several separate banking systems to collect required 
data: 
-  Credit Score System → to fetch the applicant’s credit score and 
history. 
-  Account Status System → to check the customer’s existing 
accounts, outstanding liabilities, repayment records, etc. 
-  Government PR Status System → to check the Permanent 
Resident (PR) status of non-Singaporean. 
"""
