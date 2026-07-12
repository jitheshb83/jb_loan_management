"""Payment schedule model."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base


class Payment(Base):
    """Payment schedule entry for a loan."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    payment_number = Column(Integer, nullable=False)
    due_date = Column(DateTime, nullable=False)
    beginning_balance = Column(Float, nullable=False)
    emi = Column(Float, nullable=False)
    principal = Column(Float, nullable=False)
    interest = Column(Float, nullable=False)
    ending_balance = Column(Float, nullable=False)
    is_paid = Column(Boolean, default=False)
    paid_date = Column(DateTime, nullable=True)
    paid_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    # Relationships
    loan = relationship("Loan", back_populates="payments")

    def __repr__(self):
        return f"<Payment(loan_id={self.loan_id}, payment_num={self.payment_number}, emi={self.emi})>"
