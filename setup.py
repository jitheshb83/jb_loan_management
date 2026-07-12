from setuptools import setup, find_packages

setup(
    name="jb-loan-management",
    version="0.1.0",
    description="Desktop application for housing loan management, amortization analysis, and prepayment optimization",
    author="Jithesh Bharathan",
    author_email="jithesh@jithonline.com",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "PySide6>=6.6.0",
        "pandas>=2.1.0",
        "numpy>=1.26.0",
        "matplotlib>=3.8.0",
        "PyQtGraph>=0.13.0",
        "SQLAlchemy>=2.0.0",
        "python-dateutil>=2.8.0",
        "openpyxl>=3.11.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "loan-manager=src.main:main",
        ],
    },
)
