# Housing Loan Manager

Desktop application built with Python and PySide6 for housing loan management, amortization analysis, prepayment optimization and reporting.

![Platform](https://img.shields.io/badge/platform-macOS-blue) ![Python](https://img.shields.io/badge/python-3.10%2B-green) ![UI](https://img.shields.io/badge/UI-PySide6%20(Qt)-brightgreen)

## Features

- **Dashboard** — KPI cards (outstanding balance, interest paid, interest saved, projected closure date), balance-reduction chart, principal-vs-interest distribution
- **Loan Management** — add/edit/delete loans with live EMI calculation and input validation
- **Amortization** — full month-by-month payment schedule with summary cards and Excel export
- **Extra Payments** — configure any mix of one-time / monthly / quarterly / yearly prepayments and see combined impact (tenure reduction, interest saved, new closure date)
- **What-If Simulator** — compare rate-change, tenure-change, and prepayment scenarios side by side

## Prerequisites

- **macOS** (built and tested on Apple Silicon; Intel Macs work if you build on one)
- **Python 3.10+** (3.11 recommended)
- Xcode Command Line Tools (for `iconutil`, used by icon generation): `xcode-select --install`

## 1. Set Up the Repo

```bash
git clone https://github.com/<your-username>/jb_loan_management.git
cd jb_loan_management

# (recommended) create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# install all dependencies (runtime + build tools)
pip install -r requirements.txt
```

## 2. Run from Source (Development)

```bash
python -m src.main
# or
python run.py
```

Try the calculation engines without the UI:

```bash
python demo.py
```

## 3. Run the Tests

```bash
pytest tests/ -v
```

All calculation logic (EMI, amortization, prepayments, simulator) is covered by unit and regression tests.

## 4. Build the macOS Application (.app)

One command builds a standalone app — end users need no Python installed:

```bash
./scripts/build_app.sh
```

This:
1. Generates the app icon (`assets/AppIcon.icns`) if missing, via `scripts/generate_icon.py`
2. Runs PyInstaller with `HousingLoanManager.spec`
3. Produces **`dist/Housing Loan Manager.app`** (~220 MB)

Launch it like any Mac app:

```bash
open "dist/Housing Loan Manager.app"
```

To rebuild after code changes, just run the script again.

## 5. Package a DMG Installer (Optional)

To create a shareable drag-to-Applications disk image:

```bash
./scripts/build_dmg.sh
```

Produces **`dist/HousingLoanManager-<version>.dmg`** containing the app and an `Applications` shortcut.

## 6. Code Signing & Notarization (Optional — for Distribution)

The build is **ad-hoc signed**, which runs fine on the Mac that built it. To distribute to other Macs without Gatekeeper's "unidentified developer" warning you need a paid Apple Developer ID:

```bash
# sign only (auto-detects a "Developer ID Application" certificate in your keychain)
./scripts/codesign_notarize.sh

# sign + notarize + staple (requires a notarytool keychain profile — see script header)
./scripts/codesign_notarize.sh --notarize
```

If no certificate is installed, the script explains what's needed and exits cleanly without touching the build.

> **Tip for testing on another Mac without signing:** right-click the app → Open → Open (bypasses the Gatekeeper warning once), or `xattr -dr com.apple.quarantine "Housing Loan Manager.app"`.

## Project Structure

```
├── src/
│   ├── calculations/     # EMI, amortization, prepayment & what-if engines
│   ├── ui/               # PySide6 tabs: dashboard, loans, amortization, extra payments, simulator
│   ├── models/           # SQLAlchemy ORM models
│   ├── database/         # Session management + repositories (SQLite)
│   ├── reporting/        # Excel export
│   ├── utils/            # Validators, currency/date formatting helpers
│   ├── config.py         # App configuration (paths, defaults)
│   └── main.py           # Entry point
├── tests/                # Unit + regression tests
├── scripts/
│   ├── build_app.sh          # Build the .app bundle
│   ├── build_dmg.sh          # Package the .dmg installer
│   ├── codesign_notarize.sh  # Sign/notarize for distribution
│   └── generate_icon.py      # Regenerate the app icon
├── HousingLoanManager.spec   # PyInstaller build spec
├── requirements.txt
└── demo.py               # CLI demo of the calculation engines
```

## App Data Locations

| What | Where |
|---|---|
| SQLite database | `~/.loan_manager/loans.db` |
| Logs | `~/.loan_manager/logs/` |

## Troubleshooting

- **App won't open on another Mac ("unidentified developer")** — see section 6; the app isn't notarized unless you sign it with a Developer ID.
- **Build fails on icon generation** — ensure Xcode Command Line Tools are installed (`iconutil` must be on PATH) and Pillow is installed (`pip install -r requirements.txt`).
- **`pyinstaller: command not found`** — activate your virtualenv, or `pip install pyinstaller`.
- **Blank/odd fonts in charts** — harmless Qt font-alias warning on first launch; it resolves itself.

## Known Limitations (MVP)

- Loans are held in memory during a session — SQLite persistence is scaffolded but not yet wired into the UI (planned next)
- PDF report generation not yet implemented
- Single-loan workflows; multi-loan portfolio view planned

See [CLAUDE.md](CLAUDE.md) and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for development details.
