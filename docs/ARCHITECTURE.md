# Housing Loan Manager - Architecture Guide

## Project Overview

Housing Loan Manager is a desktop application for managing housing loans, analyzing amortization schedules, simulating extra payments, and optimizing prepayment strategies.

## Directory Structure

```
jb_loan_management/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration settings
│   │
│   ├── models/                 # Data models (SQLAlchemy ORM)
│   │   ├── __init__.py
│   │   ├── base.py            # SQLAlchemy declarative base
│   │   ├── loan.py            # Loan entity
│   │   ├── payment.py         # Payment schedule
│   │   ├── extra_payment.py   # Extra/prepayment
│   │   ├── rate_history.py    # Interest rate changes
│   │   └── simulation.py      # What-if scenarios
│   │
│   ├── database/               # Data access layer
│   │   ├── __init__.py
│   │   ├── session.py         # Database connection & session management
│   │   └── repositories.py    # Repository pattern for data access
│   │
│   ├── calculations/           # Business logic engines
│   │   ├── __init__.py
│   │   ├── emi_calculator.py           # EMI calculations
│   │   ├── amortization_engine.py      # Amortization schedule generation
│   │   ├── extra_payment_engine.py     # Extra payment analysis
│   │   └── simulator.py                # What-if scenarios
│   │
│   ├── ui/                     # User interface (PySide6)
│   │   ├── __init__.py
│   │   └── main_window.py     # Main application window (skeleton)
│   │
│   ├── reporting/              # Export & reporting
│   │   ├── __init__.py
│   │   ├── excel_exporter.py          # Excel export
│   │   ├── pdf_generator.py           # PDF generation (TODO)
│   │   └── report_builder.py          # Report building
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── validators.py       # Input validation
│       └── helpers.py          # Formatting & helpers
│
├── tests/
│   ├── __init__.py
│   ├── test_emi_calculator.py
│   └── test_amortization_engine.py
│
├── docs/
│   └── ARCHITECTURE.md         # This file
│
├── requirements.txt            # Python dependencies
├── setup.py                    # Package setup
├── README.md                   # Project README
└── .gitignore                  # Git ignore rules
```

## Architecture Layers

### 1. **Persistence Layer** (`models/`, `database/`)
- **Models**: SQLAlchemy ORM models defining database schema
  - `Loan`: Core loan entity
  - `Payment`: Monthly payment schedule
  - `ExtraPayment`: One-time or recurring prepayments
  - `RateHistory`: Interest rate changes
  - `Simulation`: What-if scenario results

- **Database Access**: Repository pattern for clean data access
  - `SessionLocal`: SQLite database connection (stored in `~/.loan_manager/loans.db`)
  - Repositories: `LoanRepository`, `PaymentRepository`, etc.

### 2. **Business Logic Layer** (`calculations/`)
Core financial calculations:

- **EMICalculator**: 
  - Calculate EMI (Equated Monthly Installment)
  - Principal-interest split for any payment
  - Remaining balance calculation
  - Total interest payable

- **AmortizationEngine**:
  - Generate complete amortization schedule
  - Track month-by-month breakdown
  - Calculate running balance and cumulative interest

- **ExtraPaymentEngine**:
  - Analyze impact of one-time prepayments
  - Calculate tenure reduction and interest savings
  - Support multiple payment frequencies

- **LoanSimulator**:
  - What-if scenarios (rate changes, tenure changes, extra payments)
  - Compare multiple scenarios
  - Project closure dates

### 3. **User Interface Layer** (`ui/`)
Built with PySide6 (Qt for Python):

- **MainWindow**: Tab-based interface for different modules
- Planned tabs:
  - Dashboard: KPIs and quick overview
  - Loan Management: Add/edit loans
  - Amortization: View schedules
  - Extra Payments: Configure prepayments
  - What-If Simulator: Run scenarios
  - Reporting: Export and analysis

### 4. **Reporting Layer** (`reporting/`)
Export and generate reports:

- **ExcelExporter**: Export schedules to Excel with formatting
- **PDFGenerator**: Generate PDF reports (to implement)
- **ReportBuilder**: Build custom reports and summaries

### 5. **Utility Layer** (`utils/`)
- **Validators**: Input validation for loans, dates, amounts
- **Helpers**: Currency/date formatting, duration calculations

## Data Flow

```
User Input (UI)
    ↓
Validators (utils/)
    ↓
Repositories (database/) → Database (SQLite)
    ↓
Calculation Engines (calculations/)
    ↓
Report Builders (reporting/)
    ↓
UI Display / Export
```

## Key Design Patterns

1. **Repository Pattern**: Clean separation between data access and business logic
2. **Layered Architecture**: Clear separation of concerns
3. **Immutable Calculations**: Calculation engines produce new results without side effects
4. **Data Classes**: Simple data transfer objects for results

## Database Schema

**Loans**
- id, name, bank_name, principal_amount, annual_rate, tenure_months
- start_date, emi, is_active, created_at, updated_at

**Payments** (auto-generated from amortization)
- id, loan_id, payment_number, due_date
- beginning_balance, emi, principal, interest, ending_balance
- is_paid, paid_date, paid_amount

**ExtraPayments** (user-configured)
- id, loan_id, amount, frequency (one_time/monthly/quarterly/yearly)
- start_date, end_date, interest_saved, tenure_reduction_months

**RateHistories** (rate changes)
- id, loan_id, old_rate, new_rate, effective_date, reason

**Simulations** (what-if results)
- id, loan_id, name, scenario_type
- original/simulated_tenure, original/simulated_interest, interest_saved

## Testing Strategy

- Unit tests for calculation engines (test_emi_calculator.py, test_amortization_engine.py)
- Integration tests for database operations
- UI tests for user workflows (planned)

## Next Steps (MVP Phase)

1. Implement Dashboard UI module
2. Implement Loan Management module (CRUD operations)
3. Implement Amortization viewer
4. Implement Extra Payments configuration
5. Implement What-If Simulator UI
6. Wire up all calculation engines to UI
7. Implement Excel export functionality
8. Add comprehensive error handling
9. Performance optimization for large datasets
10. PDF report generation

## Future Enhancements

- Multi-loan portfolio management
- Refinance analysis module
- AI advisor for prepayment optimization
- Analytics and visualization
- Mobile companion app
- Cloud sync for multiple devices
