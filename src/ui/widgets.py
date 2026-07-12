"""Shared UI widgets."""

from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout
from PySide6.QtGui import QFont


class StatCard(QFrame):
    """Stat card showing a titled metric value.

    Single implementation shared by the Dashboard KPIs, the Amortization
    summary row, and the Extra Payments impact row.
    """

    def __init__(self, title: str, value: str = "--", subtitle: str = "",
                 color: str = "#366092", value_point_size: int = 16):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #f9f9f9;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(9)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #666;")

        self.value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(value_point_size)
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        self.value_label.setStyleSheet(f"color: {color};")

        layout.addWidget(title_label)
        layout.addWidget(self.value_label)

        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_font = QFont()
            subtitle_font.setPointSize(8)
            subtitle_label.setFont(subtitle_font)
            subtitle_label.setStyleSheet("color: #999;")
            layout.addWidget(subtitle_label)

        layout.addStretch()

    def set_value(self, value: str):
        """Update the displayed value."""
        self.value_label.setText(value)
