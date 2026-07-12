"""Simulation/what-if scenario model."""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from .base import Base


class Simulation(Base):
    """What-if simulation scenario for a loan."""

    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scenario_type = Column(String(50), nullable=False)  # "extra_payment", "rate_change", "refinance", etc.
    parameters = Column(Text, nullable=True)  # JSON serialized parameters
    original_tenure_months = Column(Integer, nullable=False)
    simulated_tenure_months = Column(Integer, nullable=False)
    original_total_interest = Column(Float, nullable=False)
    simulated_total_interest = Column(Float, nullable=False)
    interest_saved = Column(Float, nullable=False)
    closure_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationships
    loan = relationship("Loan", back_populates="simulations")

    def __repr__(self):
        return f"<Simulation(loan_id={self.loan_id}, type='{self.scenario_type}', saved={self.interest_saved})>"
