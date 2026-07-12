"""Main entry point for the application."""

import sys
from PySide6.QtWidgets import QApplication
from src.database import init_db
from src.ui import MainWindow
from src.config import APP_NAME, APP_VERSION


def main():
    """Initialize and run the application."""
    # Initialize database
    init_db()

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
