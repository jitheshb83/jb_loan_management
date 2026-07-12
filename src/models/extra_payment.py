"""Extra payment (prepayment) model."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .base import Base


class PaymentFrequency(enum.Enum):
    """Frequency of extra payments."""
    ONE_TIME = "one_time"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ExtraPayment(Base):
    """Extra payment (prepayment) entry for a loan."""

    __tablename__ = "extra_payments"

    id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    amount = Column(Float, nullable=False)
    frequency = Column(Enum(PaymentFrequency), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    description = Column(String(255), nullable=True)
    interest_saved = Column(Float, default=0.0)
    tenure_reduction_months = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationships
    loan = relationship("Loan", back_populates="extra_payments")

    def __repr__(self):
        return f"<ExtraPayment(loan_id={self.loan_id}, amount={self.amount}, frequency={self.frequency.value})>"
