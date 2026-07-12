"""Interest rate history model."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class RateHistory(Base):
    """Interest rate change history for a loan."""

    __tablename__ = "rate_histories"

    id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    old_rate = Column(Float, nullable=False)
    new_rate = Column(Float, nullable=False)
    effective_date = Column(DateTime, nullable=False)
    reason = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

    # Relationships
    loan = relationship("Loan", back_populates="rate_histories")

    def __repr__(self):
        return f"<RateHistory(loan_id={self.loan_id}, {self.old_rate}% -> {self.new_rate}%)>"
