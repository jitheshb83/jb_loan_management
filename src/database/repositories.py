"""Repository classes for data access."""

from typing import List, Optional
from sqlalchemy.orm import Session
from src.models import Loan, Payment, ExtraPayment, RateHistory, Simulation


class BaseRepository:
    """Base repository class."""

    def __init__(self, session: Session, model):
        self.session = session
        self.model = model

    def create(self, **kwargs):
        """Create a new record."""
        instance = self.model(**kwargs)
        self.session.add(instance)
        self.session.commit()
        return instance

    def get(self, id: int) -> Optional[object]:
        """Get a record by ID."""
        return self.session.query(self.model).filter(self.model.id == id).first()

    def get_all(self) -> List[object]:
        """Get all records."""
        return self.session.query(self.model).all()

    def update(self, id: int, **kwargs):
        """Update a record."""
        instance = self.get(id)
        if instance:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            self.session.commit()
        return instance

    def delete(self, id: int) -> bool:
        """Delete a record."""
        instance = self.get(id)
        if instance:
            self.session.delete(instance)
            self.session.commit()
            return True
        return False


class LoanRepository(BaseRepository):
    """Loan repository."""

    def __init__(self, session: Session):
        super().__init__(session, Loan)

    def get_active_loans(self) -> List[Loan]:
        """Get all active loans."""
        return self.session.query(Loan).filter(Loan.is_active == True).all()

    def get_by_name(self, name: str) -> Optional[Loan]:
        """Get loan by name."""
        return self.session.query(Loan).filter(Loan.name == name).first()


class PaymentRepository(BaseRepository):
    """Payment schedule repository."""

    def __init__(self, session: Session):
        super().__init__(session, Payment)

    def get_by_loan(self, loan_id: int) -> List[Payment]:
        """Get all payments for a loan."""
        return self.session.query(Payment).filter(Payment.loan_id == loan_id).order_by(Payment.payment_number).all()

    def get_pending_payments(self, loan_id: int) -> List[Payment]:
        """Get unpaid payments for a loan."""
        return self.session.query(Payment).filter(
            Payment.loan_id == loan_id,
            Payment.is_paid == False
        ).order_by(Payment.payment_number).all()


class ExtraPaymentRepository(BaseRepository):
    """Extra payment repository."""

    def __init__(self, session: Session):
        super().__init__(session, ExtraPayment)

    def get_by_loan(self, loan_id: int) -> List[ExtraPayment]:
        """Get all extra payments for a loan."""
        return self.session.query(ExtraPayment).filter(ExtraPayment.loan_id == loan_id).all()


class RateHistoryRepository(BaseRepository):
    """Rate history repository."""

    def __init__(self, session: Session):
        super().__init__(session, RateHistory)

    def get_by_loan(self, loan_id: int) -> List[RateHistory]:
        """Get rate history for a loan."""
        return self.session.query(RateHistory).filter(
            RateHistory.loan_id == loan_id
        ).order_by(RateHistory.effective_date).all()


class SimulationRepository(BaseRepository):
    """Simulation repository."""

    def __init__(self, session: Session):
        super().__init__(session, Simulation)

    def get_by_loan(self, loan_id: int) -> List[Simulation]:
        """Get all simulations for a loan."""
        return self.session.query(Simulation).filter(Simulation.loan_id == loan_id).all()

    def get_by_type(self, scenario_type: str) -> List[Simulation]:
        """Get simulations by type."""
        return self.session.query(Simulation).filter(Simulation.scenario_type == scenario_type).all()
