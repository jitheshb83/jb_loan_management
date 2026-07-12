"""Report builder for custom reports."""

from typing import Dict, Any, List
from datetime import datetime


class ReportBuilder:
    """Build custom reports from loan data."""

    @staticmethod
    def build_loan_summary(loan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build summary report for a loan."""
        return {
            "report_type": "loan_summary",
            "generated_on": datetime.now(),
            "loan_name": loan_data.get("name"),
            "bank_name": loan_data.get("bank_name"),
            "principal": loan_data.get("principal_amount"),
            "annual_rate": loan_data.get("annual_rate"),
            "tenure_months": loan_data.get("tenure_months"),
            "emi": loan_data.get("emi"),
        }

    @staticmethod
    def build_amortization_summary(
        schedule: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Build summary from amortization schedule."""
        if not schedule:
            return {}

        total_interest = sum(entry.get("interest", 0) for entry in schedule)
        total_principal = sum(entry.get("principal", 0) for entry in schedule)
        total_emi = sum(entry.get("emi", 0) for entry in schedule)

        return {
            "report_type": "amortization_summary",
            "total_payments": len(schedule),
            "total_principal": round(total_principal, 2),
            "total_interest": round(total_interest, 2),
            "total_amount": round(total_emi, 2),
            "first_payment_date": schedule[0].get("due_date"),
            "last_payment_date": schedule[-1].get("due_date"),
        }

    @staticmethod
    def build_prepayment_analysis(
        analysis_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build analysis report for extra payments."""
        return {
            "report_type": "prepayment_analysis",
            "generated_on": datetime.now(),
            **analysis_data
        }

    @staticmethod
    def build_dashboard_snapshot(
        loan: Dict[str, Any],
        current_payment_number: int,
        outstanding_balance: float,
        total_interest_paid: float,
        total_interest_savings: float,
        projected_closure_date: datetime
    ) -> Dict[str, Any]:
        """Build dashboard snapshot for loan overview."""
        return {
            "report_type": "dashboard",
            "loan_name": loan.get("name"),
            "current_payment_number": current_payment_number,
            "outstanding_balance": round(outstanding_balance, 2),
            "total_interest_paid": round(total_interest_paid, 2),
            "total_interest_savings": round(total_interest_savings, 2),
            "projected_closure_date": projected_closure_date,
            "generated_on": datetime.now(),
        }
