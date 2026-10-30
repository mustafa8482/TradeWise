from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QComboBox,
    QDateEdit,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QAbstractItemView,
)
from PySide6.QtCore import QDate, Qt

from database.connection import get_connection


class WheelLockedComboBox(QComboBox):
    """Prevent accidental dropdown changes using the mouse wheel."""

    def wheelEvent(self, event):
        event.ignore()


class WheelLockedDateEdit(QDateEdit):
    """Prevent accidental date changes using the mouse wheel."""

    def wheelEvent(self, event):
        event.ignore()


class MistakeJournalPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("TradeWise - Mistake Journal")

        self.setStyleSheet("""
            QWidget {
                background-color: #0b1120;
                color: #e2e8f0;
                font-family: Segoe UI;
                font-size: 12px;
            }

            QLabel {
                color: #cbd5e1;
            }

            QLineEdit,
            QComboBox,
            QDateEdit,
            QTextEdit {
                background-color: #0f172a;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
                selection-background-color: #2563eb;
            }

            QComboBox QAbstractItemView {
                background-color: #0f172a;
                color: #f8fafc;
                selection-background-color: #2563eb;
                border: 1px solid #334155;
            }

            QDateEdit::drop-down {
                border: none;
                width: 24px;
            }

            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 9px 16px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }

            QPushButton#deleteButton {
                background-color: #dc2626;
            }

            QPushButton#deleteButton:hover {
                background-color: #b91c1c;
            }

            QPushButton#clearButton {
                background-color: #334155;
            }

            QPushButton#clearButton:hover {
                background-color: #475569;
            }

            QFrame#summaryCard {
                background-color: #111c30;
                border: 1px solid #263449;
                border-radius: 10px;
            }

            QTableWidget {
                background-color: #0f172a;
                alternate-background-color: #111c30;
                color: #e2e8f0;
                border: 1px solid #263449;
                border-radius: 6px;
                gridline-color: #263449;
                selection-background-color: #1e40af;
                selection-color: white;
            }

            QHeaderView::section {
                background-color: #1e293b;
                color: #f8fafc;
                border: none;
                border-right: 1px solid #334155;
                padding: 9px;
                font-weight: bold;
            }
        """)

        self.build_ui()
        self.load_mistakes()

    # --------------------------------------------------
    # USER INTERFACE
    # --------------------------------------------------

    def build_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Page heading
        heading = QLabel("Mistake Journal")
        heading.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            color: #f8fafc;
        """)

        subtitle = QLabel(
            "Track your trading mistakes, financial impact and lessons."
        )
        subtitle.setStyleSheet("color: #94a3b8; font-size: 13px;")

        main_layout.addWidget(heading)
        main_layout.addWidget(subtitle)

        # Summary cards
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(12)

        self.total_mistakes_label = self.create_summary_card(
            summary_layout,
            "TOTAL MISTAKES",
            "0"
        )

        self.financial_impact_label = self.create_summary_card(
            summary_layout,
            "FINANCIAL IMPACT",
            "₹0"
        )

        self.common_mistake_label = self.create_summary_card(
            summary_layout,
            "MOST COMMON MISTAKE",
            "None"
        )

        main_layout.addLayout(summary_layout)

        # Form container
        form_card = QFrame()
        form_card.setObjectName("summaryCard")

        form_layout = QVBoxLayout(form_card)
        form_layout.setContentsMargins(16, 16, 16, 16)
        form_layout.setSpacing(12)

        form_heading = QLabel("Record a Trading Mistake")
        form_heading.setStyleSheet("""
            font-size: 17px;
            font-weight: bold;
            color: #f8fafc;
        """)

        form_layout.addWidget(form_heading)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(12)

        # Date
        grid.addWidget(QLabel("Date"), 0, 0)

        self.date_input = WheelLockedDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd-MM-yyyy")
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMinimumWidth(150)

        grid.addWidget(self.date_input, 0, 1)

        # Symbol
        grid.addWidget(QLabel("Symbol"), 0, 2)

        self.symbol_input = WheelLockedComboBox()
        self.symbol_input.setEditable(True)
        self.symbol_input.addItems([
            "NIFTY",
            "BANKNIFTY",
            "FINNIFTY",
            "SENSEX",
            "RELIANCE",
            "HDFCBANK",
            "ICICIBANK",
            "SBIN",
            "Other",
        ])
        self.symbol_input.setMinimumWidth(170)

        grid.addWidget(self.symbol_input, 0, 3)

        # Mistake type
        grid.addWidget(QLabel("Mistake Type"), 1, 0)

        self.mistake_type_input = WheelLockedComboBox()
        self.mistake_type_input.addItems([
            "Select mistake",
            "Overtrading",
            "Revenge Trading",
            "FOMO",
            "No Stop Loss",
            "Early Entry",
            "Late Entry",
            "Early Exit",
            "Late Exit",
            "Wrong Position Size",
            "Against Trend",
            "No Trading Plan",
            "Emotional Trading",
            "Other",
        ])

        grid.addWidget(self.mistake_type_input, 1, 1)

        # Emotion
        grid.addWidget(QLabel("Emotion"), 1, 2)

        self.emotion_input = WheelLockedComboBox()
        self.emotion_input.addItems([
            "Select emotion",
            "Fear",
            "Greed",
            "Anger",
            "FOMO",
            "Overconfidence",
            "Anxiety",
            "Impatience",
            "Revenge",
            "Calm",
            "Other",
        ])

        grid.addWidget(self.emotion_input, 1, 3)

        # Financial impact - QLineEdit fixes spinbox input issues
        grid.addWidget(QLabel("Financial Impact (₹)"), 2, 0)

        self.impact_input = QLineEdit()
        self.impact_input.setPlaceholderText("Example: 500 or 1000.50")
        self.impact_input.setText("0")
        self.impact_input.setMinimumWidth(150)

        grid.addWidget(self.impact_input, 2, 1)

        form_layout.addLayout(grid)

        # What happened
        form_layout.addWidget(QLabel("What Happened?"))

        self.what_happened_input = QTextEdit()
        self.what_happened_input.setPlaceholderText(
            "Describe your mistake. What did you do and why?"
        )
        self.what_happened_input.setFixedHeight(75)

        form_layout.addWidget(self.what_happened_input)

        # Lesson learned
        form_layout.addWidget(QLabel("Lesson Learned"))

        self.lesson_input = QTextEdit()
        self.lesson_input.setPlaceholderText(
            "What will you do differently next time?"
        )
        self.lesson_input.setFixedHeight(65)

        form_layout.addWidget(self.lesson_input)

        # Form buttons
        button_layout = QHBoxLayout()

        button_layout.addStretch()

        self.clear_button = QPushButton("Clear Form")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.clicked.connect(self.clear_form)

        self.save_button = QPushButton("Save Mistake")
        self.save_button.clicked.connect(self.save_mistake)

        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.save_button)

        form_layout.addLayout(button_layout)

        main_layout.addWidget(form_card)

        # History heading
        history_heading = QLabel("Mistake History")
        history_heading.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #f8fafc;
        """)

        main_layout.addWidget(history_heading)

        # Table
        self.table = QTableWidget()

        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Date",
            "Symbol",
            "Mistake",
            "Emotion",
            "Financial Impact",
            "Lesson Learned",
        ])

        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            5, QHeaderView.ResizeMode.Stretch
        )

        self.table.verticalHeader().setVisible(False)

        main_layout.addWidget(self.table, 1)

        # Delete selected row
        delete_layout = QHBoxLayout()
        delete_layout.addStretch()

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.clicked.connect(
            self.delete_selected_mistake
        )

        delete_layout.addWidget(self.delete_button)

        main_layout.addLayout(delete_layout)

    # --------------------------------------------------
    # SUMMARY CARDS
    # --------------------------------------------------

    def create_summary_card(self, layout, title, value):

        card = QFrame()
        card.setObjectName("summaryCard")
        card.setMinimumHeight(85)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 12, 14, 12)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #94a3b8;
            font-size: 10px;
            font-weight: bold;
        """)

        value_label = QLabel(value)
        value_label.setStyleSheet("""
            color: #f8fafc;
            font-size: 19px;
            font-weight: bold;
        """)

        value_label.setWordWrap(True)

        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)

        layout.addWidget(card)

        return value_label

    # --------------------------------------------------
    # SAVE MISTAKE
    # --------------------------------------------------

    def save_mistake(self):

        mistake_date = self.date_input.date().toString("yyyy-MM-dd")
        symbol = self.symbol_input.currentText().strip()
        mistake_type = self.mistake_type_input.currentText()
        emotion = self.emotion_input.currentText()
        what_happened = self.what_happened_input.toPlainText().strip()
        lesson_learned = self.lesson_input.toPlainText().strip()

        # Validate symbol
        if not symbol:
            QMessageBox.warning(
                self,
                "Missing Symbol",
                "Please enter a trading symbol."
            )
            return

        # Validate mistake type
        if mistake_type == "Select mistake":
            QMessageBox.warning(
                self,
                "Missing Mistake Type",
                "Please select a mistake type."
            )
            return

        # Validate emotion
        if emotion == "Select emotion":
            QMessageBox.warning(
                self,
                "Missing Emotion",
                "Please select an emotion."
            )
            return

        # Validate financial impact
        impact_text = (
            self.impact_input.text()
            .strip()
            .replace(",", "")
            .replace("₹", "")
            .strip()
        )

        try:
            financial_impact = float(impact_text) if impact_text else 0.0

            if financial_impact < 0:
                raise ValueError

        except ValueError:
            QMessageBox.warning(
                self,
                "Invalid Amount",
                "Please enter a valid non-negative amount.\n\n"
                "Examples: 500, 1000, 1000.50"
            )
            return

        # Validate description
        if not what_happened:
            QMessageBox.warning(
                self,
                "Missing Details",
                "Please describe what happened."
            )
            return

        if not lesson_learned:
            QMessageBox.warning(
                self,
                "Missing Lesson",
                "Please enter the lesson you learned."
            )
            return

        try:
            with get_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO mistakes (
                        mistake_date,
                        symbol,
                        mistake_type,
                        emotion,
                        financial_impact,
                        what_happened,
                        lesson_learned
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        mistake_date,
                        symbol.upper(),
                        mistake_type,
                        emotion,
                        financial_impact,
                        what_happened,
                        lesson_learned,
                    ),
                )

            QMessageBox.information(
                self,
                "Success",
                "Trading mistake saved successfully!"
            )

            self.clear_form()
            self.load_mistakes()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not save the mistake.\n\n{error}"
            )

    # --------------------------------------------------
    # LOAD MISTAKES
    # --------------------------------------------------

    def load_mistakes(self):

        try:
            with get_connection() as connection:

                rows = connection.execute(
                    """
                    SELECT *
                    FROM mistakes
                    ORDER BY id DESC
                    """
                ).fetchall()

                total_row = connection.execute(
                    """
                    SELECT
                        COUNT(*) AS total,
                        COALESCE(SUM(financial_impact), 0) AS impact
                    FROM mistakes
                    """
                ).fetchone()

                common_row = connection.execute(
                    """
                    SELECT mistake_type, COUNT(*) AS total
                    FROM mistakes
                    GROUP BY mistake_type
                    ORDER BY total DESC, mistake_type ASC
                    LIMIT 1
                    """
                ).fetchone()

            self.table.setRowCount(0)

            for row_data in rows:

                row_index = self.table.rowCount()
                self.table.insertRow(row_index)

                date_value = row_data["mistake_date"]

                try:
                    date_value = QDate.fromString(
                        date_value, "yyyy-MM-dd"
                    ).toString("dd-MM-yyyy")
                except Exception:
                    pass

                impact_value = float(
                    row_data["financial_impact"] or 0
                )

                values = [
                    date_value,
                    row_data["symbol"],
                    row_data["mistake_type"],
                    row_data["emotion"],
                    f"₹{impact_value:,.2f}",
                    row_data["lesson_learned"],
                ]

                for column, value in enumerate(values):

                    item = QTableWidgetItem(str(value))

                    if column == 0:
                        item.setData(
                            Qt.ItemDataRole.UserRole,
                            row_data["id"]
                        )

                    if column == 4:
                        item.setTextAlignment(
                            Qt.AlignmentFlag.AlignRight
                            | Qt.AlignmentFlag.AlignVCenter
                        )

                    self.table.setItem(
                        row_index,
                        column,
                        item
                    )

            # Update summary cards
            total_mistakes = int(total_row["total"] or 0)
            total_impact = float(total_row["impact"] or 0)

            self.total_mistakes_label.setText(
                str(total_mistakes)
            )

            self.financial_impact_label.setText(
                f"₹{total_impact:,.2f}"
            )

            if common_row:
                self.common_mistake_label.setText(
                    f"{common_row['mistake_type']} "
                    f"({common_row['total']})"
                )
            else:
                self.common_mistake_label.setText("None")

        except Exception as error:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not load mistake history.\n\n{error}"
            )

    # --------------------------------------------------
    # DELETE SELECTED MISTAKE
    # --------------------------------------------------

    def delete_selected_mistake(self):

        selected_row = self.table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a mistake from the table first."
            )
            return

        first_item = self.table.item(selected_row, 0)

        if first_item is None:
            QMessageBox.warning(
                self,
                "Error",
                "Could not identify the selected mistake."
            )
            return

        mistake_id = first_item.data(
            Qt.ItemDataRole.UserRole
        )

        if mistake_id is None:
            QMessageBox.warning(
                self,
                "Error",
                "Mistake ID was not found."
            )
            return

        confirmation = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this mistake?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        try:
            with get_connection() as connection:

                cursor = connection.execute(
                    "DELETE FROM mistakes WHERE id = ?",
                    (mistake_id,)
                )

                deleted_count = cursor.rowcount

            if deleted_count == 0:
                QMessageBox.warning(
                    self,
                    "Not Found",
                    "This mistake was already deleted or does not exist."
                )
                self.load_mistakes()
                return

            self.load_mistakes()

            QMessageBox.information(
                self,
                "Deleted",
                "Selected mistake deleted successfully."
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not delete the mistake.\n\n{error}"
            )

    # --------------------------------------------------
    # CLEAR FORM
    # --------------------------------------------------

    def clear_form(self):

        self.date_input.setDate(QDate.currentDate())

        self.symbol_input.setCurrentIndex(0)
        self.symbol_input.setEditText("NIFTY")

        self.mistake_type_input.setCurrentIndex(0)
        self.emotion_input.setCurrentIndex(0)

        self.impact_input.setText("0")

        self.what_happened_input.clear()
        self.lesson_input.clear()
