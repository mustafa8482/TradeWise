
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QTextEdit,
    QPushButton,
    QMessageBox,
    QFrame,
)

from models.trade import Trade
from services.trade_service import add_trade

class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()

class NoWheelDateEdit(QDateEdit):
    def wheelEvent(self, event):
        event.ignore()

class CleanNumberSpinBox(QDoubleSpinBox):
    """Show clean numbers while preserving decimal price entry."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 999999999)
        self.setDecimals(4)
        self.setSingleStep(1)
        self.setKeyboardTracking(False)

    def wheelEvent(self, event):
        # Mouse wheel must not change the numeric value.
        event.ignore()

    def textFromValue(self, value):
        text = f"{value:.4f}".rstrip("0").rstrip(".")
        return text if text else "0"

class AddTradePage(QWidget):

    trade_saved = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 20, 28, 20)
        main_layout.setSpacing(18)

        heading = QLabel("Record a New Trade")
        heading.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #F8FAFC;"
        )

        description = QLabel(
            "Record your entry, exit, strategy and trading discipline."
        )
        description.setStyleSheet(
            "font-size: 12px; color: #94A3B8;"
        )

        main_layout.addWidget(heading)
        main_layout.addWidget(description)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #111C30;
                border: 1px solid #263247;
                border-radius: 12px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(18)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        label_style = "color: #CBD5E1; font-size: 12px;"

        # Trade date: wheel cannot change date.
        self.trade_date = NoWheelDateEdit()
        self.trade_date.setCalendarPopup(True)
        self.trade_date.setDate(QDate.currentDate())
        self.trade_date.setDisplayFormat("dd MMM yyyy")

        # Symbol
        self.symbol = QLineEdit()
        self.symbol.setPlaceholderText("Example: NIFTY, RELIANCE")

        # Market type
        self.market_type = NoWheelComboBox()
        self.market_type.addItems([
            "Equity",
            "Futures",
            "Options",
            "Crypto",
        ])

        # Direction
        self.direction = NoWheelComboBox()
        self.direction.addItems(["Long", "Short"])

        # Prices and total units
        self.entry_price = self.create_number_field()
        self.exit_price = self.create_number_field()
        self.quantity = self.create_number_field()

        # Single combined charges field
        self.charges = self.create_number_field()

        # Risk management
        self.stop_loss = self.create_number_field()
        self.target_price = self.create_number_field()

        # Status
        self.status = NoWheelComboBox()
        self.status.addItems(["Open", "Closed", "Cancelled"])

        # Strategy and timeframe
        self.strategy = QLineEdit()
        self.strategy.setPlaceholderText("Example: Breakout")

        self.timeframe = NoWheelComboBox()
        self.timeframe.addItems([
            "1m", "3m", "5m", "15m", "30m",
            "1h", "4h", "1d", "Other",
        ])
        self.timeframe.setCurrentText("5m")

        # Notes
        self.notes = QTextEdit()
        self.notes.setPlaceholderText(
            "Why did you take this trade? What was your plan?"
        )
        self.notes.setMinimumHeight(75)

        # Psychology fields
        self.emotion_before = NoWheelComboBox()
        self.emotion_before.addItems([
            "Not Recorded",
            "Calm",
            "Confident",
            "Fearful",
            "Greedy",
            "FOMO",
            "Stressed",
            "Unsure",
        ])

        self.emotion_after = NoWheelComboBox()
        self.emotion_after.addItems([
            "Not Recorded",
            "Neutral",
            "Satisfied",
            "Happy",
            "Frustrated",
            "Regretful",
            "Anxious",
            "Disappointed",
        ])

        self.followed_plan = NoWheelComboBox()
        self.followed_plan.addItems(["Yes", "No"])

        self.lessons_learned = QTextEdit()
        self.lessons_learned.setPlaceholderText(
            "What did you learn from this trade?"
        )
        self.lessons_learned.setMinimumHeight(65)

        fields = [
            ("Trade Date", self.trade_date),
            ("Symbol", self.symbol),
            ("Market Type", self.market_type),
            ("Direction", self.direction),
            ("Entry Price", self.entry_price),
            ("Exit Price (optional)", self.exit_price),
            ("Quantity (total units)", self.quantity),
            ("Charges", self.charges),
            ("Stop Loss (optional)", self.stop_loss),
            ("Target (optional)", self.target_price),
            ("Status", self.status),
            ("Strategy", self.strategy),
            ("Timeframe", self.timeframe),
            ("Notes", self.notes),
            ("Emotion Before Trade", self.emotion_before),
            ("Emotion After Trade", self.emotion_after),
            ("Followed Trading Plan?", self.followed_plan),
            ("Lessons Learned", self.lessons_learned),
        ]

        for field_name, widget in fields:
            label = QLabel(field_name)
            label.setStyleSheet(label_style)
            form.addRow(label, widget)

        card_layout.addLayout(form)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        clear_button = QPushButton("Clear Form")
        clear_button.clicked.connect(self.clear_form)

        save_button = QPushButton("Save Trade")
        save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        save_button.clicked.connect(self.save_trade)

        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                color: #E2E8F0;
                border: 1px solid #334155;
                border-radius: 7px;
                padding: 11px 20px;
            }
            QPushButton:hover {
                background-color: #334155;
            }
        """)

        save_button.setStyleSheet("""
            QPushButton {
                background-color: #166534;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 11px 24px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #15803D;
            }
        """)

        buttons_layout.addWidget(clear_button)
        buttons_layout.addWidget(save_button)
        card_layout.addLayout(buttons_layout)

        main_layout.addWidget(card)
        main_layout.addStretch()

        self.setStyleSheet("""
            QLineEdit, QComboBox, QDateEdit,
            QDoubleSpinBox, QTextEdit {
                background-color: #0B1120;
                color: #F8FAFC;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
                min-height: 22px;
            }

            QComboBox QAbstractItemView {
                background-color: #0F172A;
                color: #F8FAFC;
                selection-background-color: #166534;
            }
        """)

    def create_number_field(self):
        return CleanNumberSpinBox()

    def clear_form(self):
        self.trade_date.setDate(QDate.currentDate())
        self.symbol.clear()
        self.market_type.setCurrentIndex(0)
        self.direction.setCurrentIndex(0)

        self.entry_price.setValue(0)
        self.exit_price.setValue(0)
        self.quantity.setValue(0)
        self.charges.setValue(0)

        self.stop_loss.setValue(0)
        self.target_price.setValue(0)

        self.status.setCurrentText("Open")
        self.strategy.clear()
        self.timeframe.setCurrentText("5m")
        self.notes.clear()

        self.emotion_before.setCurrentIndex(0)
        self.emotion_after.setCurrentIndex(0)
        self.followed_plan.setCurrentText("Yes")
        self.lessons_learned.clear()

    def save_trade(self):
        symbol = self.symbol.text().strip()
        status = self.status.currentText()
        exit_value = self.exit_price.value()

        if not symbol:
            QMessageBox.warning(
                self, "Missing Symbol",
                "Please enter a trading symbol."
            )
            self.symbol.setFocus()
            return

        if self.entry_price.value() <= 0:
            QMessageBox.warning(
                self, "Invalid Entry Price",
                "Entry price zero se greater hona chahiye."
            )
            self.entry_price.setFocus()
            return

        if self.quantity.value() <= 0:
            QMessageBox.warning(
                self, "Invalid Quantity",
                "Quantity zero se greater honi chahiye."
            )
            self.quantity.setFocus()
            return

        if status == "Closed" and exit_value <= 0:
            QMessageBox.warning(
                self, "Missing Exit Price",
                "Closed trade ke liye exit price enter karo."
            )
            self.exit_price.setFocus()
            return

        trade = Trade(
            trade_date=self.trade_date.date().toString("yyyy-MM-dd"),
            symbol=symbol.upper(),
            market_type=self.market_type.currentText(),
            direction=self.direction.currentText(),
            entry_price=self.entry_price.value(),
            exit_price=exit_value if exit_value > 0 else None,
            quantity=self.quantity.value(),

            # Keep existing database/model compatible.
            multiplier=1.0,
            entry_fees=0.0,
            exit_fees=0.0,
            other_charges=self.charges.value(),

            stop_loss=(
                self.stop_loss.value()
                if self.stop_loss.value() > 0 else None
            ),
            target_price=(
                self.target_price.value()
                if self.target_price.value() > 0 else None
            ),
            strategy=self.strategy.text().strip() or None,
            timeframe=self.timeframe.currentText(),
            status=status,
            notes=self.notes.toPlainText().strip() or None,

            emotion_before=(
                None if self.emotion_before.currentText() == "Not Recorded"
                else self.emotion_before.currentText()
            ),
            emotion_after=(
                None if self.emotion_after.currentText() == "Not Recorded"
                else self.emotion_after.currentText()
            ),
            followed_plan=(self.followed_plan.currentText() == "Yes"),
            lessons_learned=(
                self.lessons_learned.toPlainText().strip() or None
            ),
        )

        try:
            trade_id = add_trade(trade)

            QMessageBox.information(
                self,
                "Trade Saved",
                f"Trade successfully save ho gaya!\nTrade ID: {trade_id}"
            )

            self.clear_form()
            self.trade_saved.emit()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Trade save nahi ho saka.\n\nError: {error}"
            )