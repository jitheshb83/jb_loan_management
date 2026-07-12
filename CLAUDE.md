# Housing Loan Manager - Claude Code Guide

## Project Summary

Desktop application for housing loan management, amortization analysis, and prepayment optimization built with Python, PySide6, and SQLite.

## Quick Start

```bash
pip install -r requirements.txt
python -m src.main
```

Tests:
```bash
pytest tests/ -v
```

## Project Structure

- **src/**: Main application code
  - `models/`: SQLAlchemy ORM models (Loan, Payment, ExtraPayment, RateHistory, Simulation)
  - `database/`: Repository pattern for data access
  - `calculations/`: Financial calculation engines (EMI, Amortization, ExtraPayment, Simulator)
  - `ui/`: PySide6 UI components (currently main_window.py skeleton)
  - `reporting/`: Excel export and report generation
  - `utils/`: Validators and formatting helpers
  - `config.py`: Application configuration
  - `main.py`: Entry point

- **tests/**: Unit tests for calculations and models
- **docs/ARCHITECTURE.md**: Detailed architecture guide
- **requirements.txt**: Python dependencies

## Key Modules

### Calculations (Core Logic) ✅
- **EMICalculator**: Calculate EMI, principal-interest split, remaining balance
- **AmortizationEngine**: Generate full amortization schedules
- **ExtraPaymentEngine**: Analyze prepayment impact (tenure reduction, interest savings)
- **LoanSimulator**: What-if scenarios (rate changes, tenure changes, extra payments)

### Database
- SQLite at `~/.loan_manager/loans.db`
- Automatic initialization on app startup
- Repository pattern for type-safe data access

### UI Modules
1. ✅ **Dashboard** - KPIs, balance chart, payment distribution
2. ✅ **Loan Management** - Add/edit/delete loans with form validation
3. ⏳ **Amortization** - View/export schedules
4. ⏳ **Extra Payments** - Configure prepayments
5. ⏳ **What-If Simulator** - Run and compare scenarios
6. ⏳ **Reporting** - Export to Excel/PDF

## Important Files

- `src/calculations/emi_calculator.py`: Core EMI math
- `src/calculations/amortization_engine.py`: Schedule generation
- `src/database/repositories.py`: Data access layer
- `src/config.py`: App configuration (paths, defaults)
- `tests/test_emi_calculator.py`: Basic calculation tests

## Development Notes

1. **Input Validation**: Always validate using `src/utils/validators.py`
2. **Database Sessions**: Use `get_db_context()` for transactions
3. **Formatting**: Use `src/utils/helpers.py` for currency/date formatting
4. **Testing**: Add tests to `tests/` for new calculation logic
5. **UI Updates**: Implement tabs in `src/ui/` following the MainWindow skeleton

## Known Limitations (MVP)

- PDF generation not yet implemented
- No multi-loan portfolio features yet
- No refinance module yet
- UI is skeleton only

## Build & Deployment

```bash
pip install -e .  # Development install
python -m pytest  # Run tests
python -m src.main  # Run app
```

Database location: `~/.loan_manager/loans.db`
Logs location: `~/.loan_manager/logs/`

### macOS App Packaging

Builds a standalone `Housing Loan Manager.app` (no Python required to run it) via PyInstaller.

```bash
./scripts/build_app.sh           # -> dist/Housing Loan Manager.app
./scripts/build_dmg.sh           # -> dist/HousingLoanManager-<version>.dmg (drag-to-Applications installer)
./scripts/codesign_notarize.sh   # sign with a Developer ID cert (no-op with instructions if none installed)
./scripts/codesign_notarize.sh --notarize  # sign + notarize + staple (requires notarytool keychain profile)
```

- `HousingLoanManager.spec`: PyInstaller spec (bundle id, version, icon, hidden imports for PySide6/pyqtgraph)
- `scripts/generate_icon.py`: regenerates `assets/AppIcon.icns` from scratch (PIL-drawn house + trend-arrow badge)
- `assets/entitlements.plist`: hardened-runtime entitlements needed for signing PyInstaller's embedded Python/Qt binaries
- Without a paid Apple Developer ID certificate, the app is only ad-hoc signed — it runs fine locally but shows a Gatekeeper "unidentified developer" warning on other Macs. `codesign_notarize.sh` explains how to fix this once a cert is available.

## Recent Additions (Just Built!)

✅ **Dashboard Module** (`src/ui/dashboard.py`)
- KPI cards (Outstanding Balance, Interest Paid, Interest Saved, Closure Date)
- Balance reduction line chart (PyQtGraph)
- Payment distribution bar chart
- Auto-updates when loan selected

✅ **Loan Management Module** (`src/ui/loan_management.py`)
- Add Loan dialog with real-time EMI calculation
- Edit/Delete functionality
- Loan table with all details
- Form validation

✅ **Signal/Slot Integration** (in `src/ui/main_window.py`)
- Loan selection → Dashboard auto-update
- Tab switching on selection
- Status bar feedback

## Next Priority Tasks

1. **Amortization Viewer** - Table display of payment schedule
2. **Extra Payments Module** - Configure prepayments (monthly/quarterly/yearly)
3. **What-If Simulator UI** - Run and compare scenarios
4. **Database Integration** - Persist loans to SQLite
5. **Excel Export** - Export schedules from UI
6. **PDF Reports** - Generate comprehensive reports
