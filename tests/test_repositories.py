"""Tests for the database repositories (isolated temp SQLite database)."""

import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.base import Base
from src.models.extra_payment import PaymentFrequency
from src.database.repositories import LoanRepository, ExtraPaymentRepository


@pytest.fixture
def session(tmp_path):
    """A session bound to a fresh temp-file SQLite database."""
    engine = create_engine(f"sqlite:///{tmp_path}/test_loans.db")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()


LOAN_KWARGS = dict(
    name="Home Loan",
    bank_name="HDFC",
    principal_amount=2500000.0,
    annual_rate=7.5,
    tenure_months=240,
    start_date=datetime(2024, 1, 1),
    emi=20139.83,
)


class TestLoanRepository:

    def test_create_and_reload(self, session):
        """A created loan survives a fresh query (i.e. is committed)."""
        repo = LoanRepository(session)
        created = repo.create(**LOAN_KWARGS)
        assert created.id is not None

        loans = repo.get_active_loans()
        assert len(loans) == 1
        assert loans[0].name == "Home Loan"
        assert loans[0].start_date == datetime(2024, 1, 1)

    def test_update(self, session):
        repo = LoanRepository(session)
        created = repo.create(**LOAN_KWARGS)
        repo.update(created.id, annual_rate=8.5)
        assert repo.get(created.id).annual_rate == 8.5

    def test_delete_cascades_extra_payments(self, session):
        """Deleting a loan removes its extra payments too."""
        loan_repo = LoanRepository(session)
        ep_repo = ExtraPaymentRepository(session)
        loan = loan_repo.create(**LOAN_KWARGS)
        ep_repo.create(
            loan_id=loan.id, amount=100000.0,
            frequency=PaymentFrequency.ONE_TIME, start_date=datetime(2027, 1, 1),
        )
        assert len(ep_repo.get_by_loan(loan.id)) == 1

        loan_repo.delete(loan.id)
        assert loan_repo.get_all() == []
        assert ep_repo.get_by_loan(loan.id) == []


class TestExtraPaymentRepository:

    def test_create_and_reload_per_loan(self, session):
        """Extra payments round-trip with their frequency enum intact."""
        loan_repo = LoanRepository(session)
        ep_repo = ExtraPaymentRepository(session)
        loan = loan_repo.create(**LOAN_KWARGS)

        ep_repo.create(loan_id=loan.id, amount=50000.0,
                       frequency=PaymentFrequency.MONTHLY, start_date=datetime(2026, 1, 1))
        ep_repo.create(loan_id=loan.id, amount=200000.0,
                       frequency=PaymentFrequency.ONE_TIME, start_date=datetime(2028, 6, 1))

        records = ep_repo.get_by_loan(loan.id)
        assert len(records) == 2
        assert {r.frequency for r in records} == {PaymentFrequency.MONTHLY, PaymentFrequency.ONE_TIME}

    def test_delete_single_plan(self, session):
        loan_repo = LoanRepository(session)
        ep_repo = ExtraPaymentRepository(session)
        loan = loan_repo.create(**LOAN_KWARGS)
        record = ep_repo.create(loan_id=loan.id, amount=50000.0,
                                frequency=PaymentFrequency.YEARLY, start_date=datetime(2026, 1, 1))
        assert ep_repo.delete(record.id) is True
        assert ep_repo.get_by_loan(loan.id) == []
