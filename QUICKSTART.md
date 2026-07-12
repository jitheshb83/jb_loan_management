# Quick Start Guide

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python -m src.main
```

Or use the run script:
```bash
python run.py
```

## Features Built

### ✅ Dashboard Module
- **KPI Cards**: Outstanding Balance, Total Interest Paid, Interest Saved, Projected Closure Date
- **Balance Chart**: Interactive line chart showing loan balance reduction over time
- **Payment Distribution Chart**: Bar chart comparing principal vs interest

### ✅ Loan Management Module
- **Add Loans**: Form with automatic EMI calculation
- **Edit Loans**: Modify existing loan details
- **Delete Loans**: Remove loans from the list
- **Loan Table**: View all loans with key metrics
- **Live EMI Calculator**: See EMI update as you enter values

### ✅ Calculation Engines
- **EMI Calculator**: Calculate monthly installments with exact math
- **Amortization Engine**: Generate complete payment schedules
- **Extra Payment Engine**: Analyze prepayment impact (interest saved, tenure reduction)
- **Loan Simulator**: What-if scenarios for rate changes and tenure changes

### 🔄 Integration
- **Loan Selection**: Click a loan in Loan Management to view it on Dashboard
- **Auto-refresh**: Dashboard updates instantly when you select a loan
- **Live Charts**: Charts update with selected loan data

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_emi_calculator.py -v

# Run demo
python demo.py
```

## Project Structure

```
src/
  ├── models/          # Database entities
  ├── database/        # Repository pattern
  ├── calculations/    # Financial engines
  ├── ui/              # PySide6 UI components
  │   ├── dashboard.py        # Dashboard with KPIs
  │   ├── loan_management.py  # Loan CRUD
  │   └── main_window.py      # Main application
  ├── reporting/       # Excel export
  └── utils/           # Validators & helpers
```

## Next Steps

1. **Amortization Viewer** - Display schedule in a table
2. **Extra Payments UI** - Configure prepayments
3. **What-If Simulator UI** - Run scenario analysis
4. **Reporting Module** - Excel export
5. **Database Integration** - Save loans to SQLite

## Sample Loan

To quickly test the app, use these values in Loan Management:
- **Loan Name**: Home Loan - HDFC
- **Bank Name**: HDFC Bank
- **Principal**: 2500000 (₹25 Lakh)
- **Annual Rate**: 7.5%
- **Tenure**: 240 months (20 years)
- **Start Date**: Today's date

Then click the loan to see the Dashboard with full amortization schedule!

## Architecture

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed design documentation.

## Development Notes

- All calculations are unit tested
- UI uses PySide6 (Qt for Python)
- Charts use PyQtGraph for performance
- Database ready with SQLAlchemy ORM
- Modular design for easy extension

## Troubleshooting

**"ModuleNotFoundError: No module named 'PySide6'"**
```bash
pip install -r requirements.txt
```

**Charts not showing**
Make sure PyQtGraph is installed:
```bash
pip install PyQtGraph==0.13.3
```

**Database errors**
Database is auto-created at: `~/.loan_manager/loans.db`

## License

Private Project
