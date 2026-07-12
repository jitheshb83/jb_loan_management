"""Loan model."""

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean
from sqlalchemy.orm import relationship
from .base import Base


class Loan(Base):
    """Loan entity with core loan details."""

    __tablename__ = "loans"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    bank_name = Column(String(255), nullable=False)
    principal_amount = Column(Float, nullable=False)
    annual_rate = Column(Float, nullable=False)
    tenure_months = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False, default=datetime.now)
    emi = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    # Relationships
    payments = relationship("Payment", back_populates="loan", cascade="all, delete-orphan")
    extra_payments = relationship("ExtraPayment", back_populates="loan", cascade="all, delete-orphan")
    rate_histories = relationship("RateHistory", back_populates="loan", cascade="all, delete-orphan")
    simulations = relationship("Simulation", back_populates="loan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Loan(id={self.id}, name='{self.name}', principal={self.principal_amount}, rate={self.annual_rate}%)>"
