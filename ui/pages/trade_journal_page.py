from datetime import date

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QDialog,
    QFormLayout,
    QDoubleSpinBox,
    QDateEdit,
    QTextEdit,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt, QDate

from services.trade_service import (
    get_all_trades,
    delete_trade,
    close_trade,
)


class CloseTradeDialog(QDialog):

    def __init__(self, trade, parent=None):
        super().__init__(parent)

        self.trade = trade

        self.setWindowTitle("Close Trade")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.exit_price = QDoubleSpinBox()
        self.exit_price.setRange(0.01, 999999999)
        self.exit_price.setDecimals(2)
        self.exit_price.setValue(float(trade["entry_price"]))

        self.exit_date = QDateEdit()
        self.exit_date.setCalendarPopup(True)
        self.exit_date.setDisplayFormat("dd-MM-yyyy")
        self.exit_date.setDate(QDate.currentDate())

        self.exit_fees = QDoubleSpinBox()
        self.exit_fees.setRange(0, 999999999)
        self.exit_fees.setDecimals(2)

        self.other_charges = QDoubleSpinBox()
        self.other_charges.setRange(0, 999999999)
        self.other_charges.setDecimals(2)

        self.closing_notes = QTextEdit()
        self.closing_notes.setPlaceholderText(
            "Trade close karne ka reason ya observations..."
        )
        self.closing_notes.setMaximumHeight(90)

        form.addRow("Symbol:", QLabel(str(trade["symbol"])))
        form.addRow("Direction:", QLabel(str(trade["direction"])))
        form.addRow("Entry Price:", QLabel(str(trade["entry_price"])))
        form.addRow("Exit Price:", self.exit_price)
        form.addRow("Exit Date:", self.exit_date)
        form.addRow("Exit Fees:", self.exit_fees)
        form.addRow("Other Charges:", self.other_charges)
        form.addRow("Closing Notes:", self.closing_notes)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)

        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
                color: #F1F5F9;
            }

            QLabel {
                color: #CBD5E1;
            }

            QLineEdit, QDoubleSpinBox, QDateEdit, QTextEdit {
                background-color: #1E293B;
                color: #F1F5F9;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 7px;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                padding: 8px 14px;
                border-radius: 6px;
            }
        """)

    def validate_and_accept(self):

        if self.exit_price.value() <= 0:
            QMessageBox.warning(
                self,
                "Invalid Price",
                "Exit price enter karo."
            )
            return

        self.accept()

    def get_data(self):

        return {
            "exit_price": self.exit_price.value(),
            "exit_date": self.exit_date.date().toString("yyyy-MM-dd"),
            "exit_fees": self.exit_fees.value(),
            "other_charges": self.other_charges.value(),
            "closing_notes": self.closing_notes.toPlainText().strip(),
        }


class TradeJournalPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("TradeJournalPage")
        self.trades = []

        self.setup_ui()
        self.load_trades()

    def setup_ui(self):

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        heading = QLabel("Trade Journal")
        heading.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #F1F5F9;"
        )
        layout.addWidget(heading)

        subtitle = QLabel(
            "Review your trades, track P&L and learn from your trading history."
        )
        subtitle.setStyleSheet("font-size: 13px; color: #94A3B8;")
        layout.addWidget(subtitle)

        toolbar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search by symbol or strategy..."
        )
        self.search_input.setMinimumHeight(38)
        self.search_input.textChanged.connect(self.filter_trades)

        refresh_button = QPushButton("Refresh")
        refresh_button.setMinimumHeight(38)
        refresh_button.clicked.connect(self.load_trades)

        toolbar.addWidget(self.search_input)
        toolbar.addWidget(refresh_button)

        layout.addLayout(toolbar)

        self.summary_label = QLabel("Total Trades: 0")
        self.summary_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #CBD5E1;"
        )
        layout.addWidget(self.summary_label)

        self.table = QTableWidget()
        self.table.setColumnCount(9)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Date",
            "Symbol",
            "Market",
            "Direction",
            "Entry",
            "Exit",
            "Net P&L",
            "Status",
        ])

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.table)

        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.close_button = QPushButton("Close Selected Trade")
        self.close_button.setMinimumHeight(40)
        self.close_button.clicked.connect(self.close_selected_trade)
        self.close_button.setEnabled(False)

        delete_button = QPushButton("Delete Selected Trade")
        delete_button.setMinimumHeight(40)
        delete_button.clicked.connect(self.delete_selected_trade)

        bottom_layout.addWidget(self.close_button)
        bottom_layout.addWidget(delete_button)

        layout.addLayout(bottom_layout)

        self.table.itemSelectionChanged.connect(
            self.update_close_button
        )

        self.setStyleSheet("""
            QWidget#TradeJournalPage {
                background-color: #0F172A;
            }

            QLineEdit {
                background-color: #1E293B;
                color: #F1F5F9;
                border: 1px solid #334155;
                border-radius: 7px;
                padding: 8px;
            }

            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 7px;
                padding: 8px 14px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1D4ED8;
            }

            QPushButton:disabled {
                background-color: #334155;
                color: #94A3B8;
            }

            QTableWidget {
                background-color: #111827;
                alternate-background-color: #1E293B;
                color: #E2E8F0;
                gridline-color: #334155;
                border: 1px solid #334155;
                border-radius: 8px;
                selection-background-color: #1D4ED8;
            }

            QHeaderView::section {
                background-color: #1E293B;
                color: #F8FAFC;
                padding: 9px;
                border: 1px solid #334155;
                font-weight: bold;
            }
        """)

    def load_trades(self):

        try:
            self.trades = get_all_trades()
            self.filter_trades(self.search_input.text())

        except Exception as error:
            QMessageBox.critical(
                self,
                "Loading Error",
                f"Trades load nahi ho sake:\n{error}",
            )

    def filter_trades(self, text=""):

        search_text = text.strip().lower()

        filtered_trades = [
            trade
            for trade in self.trades
            if search_text in str(trade.get("symbol") or "").lower()
            or search_text in str(trade.get("strategy") or "").lower()
        ]

        self.filtered_trades = filtered_trades

        self.table.setRowCount(len(filtered_trades))

        for row, trade in enumerate(filtered_trades):

            entry_price = float(trade.get("entry_price") or 0)
            exit_value = trade.get("exit_price")

            if trade.get("status") == "Closed" and exit_value not in (None, ""):

                exit_price = float(exit_value)
                quantity = float(trade.get("quantity") or 0)
                multiplier = float(trade.get("multiplier") or 1)

                if trade.get("direction") == "Short":
                    gross_pnl = (
                        entry_price - exit_price
                    ) * quantity * multiplier
                else:
                    gross_pnl = (
                        exit_price - entry_price
                    ) * quantity * multiplier

                charges = (
                    float(trade.get("entry_fees") or 0)
                    + float(trade.get("exit_fees") or 0)
                    + float(trade.get("other_charges") or 0)
                )

                net_pnl = gross_pnl - charges
                pnl_text = f"₹{net_pnl:,.2f}"

            else:
                exit_price = None
                pnl_text = "—"

            values = [
                str(trade.get("id", "")),
                str(trade.get("trade_date", "")),
                str(trade.get("symbol", "")),
                str(trade.get("market_type", "")),
                str(trade.get("direction", "")),
                f"{entry_price:,.2f}",
                f"{exit_price:,.2f}" if exit_price is not None else "—",
                pnl_text,
                str(trade.get("status", "")),
            ]

            for column, value in enumerate(values):

                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if column == 7 and pnl_text != "—":
                    item.setForeground(
                        Qt.GlobalColor.green
                        if net_pnl > 0
                        else Qt.GlobalColor.red
                        if net_pnl < 0
                        else Qt.GlobalColor.white
                    )

                self.table.setItem(row, column, item)

        self.summary_label.setText(
            f"Showing {len(filtered_trades)} of {len(self.trades)} trades"
        )

        self.update_close_button()

    def update_close_button(self):

        selected_row = self.table.currentRow()

        if selected_row < 0:
            self.close_button.setEnabled(False)
            return

        trade_id_item = self.table.item(selected_row, 0)

        if trade_id_item is None:
            self.close_button.setEnabled(False)
            return

        trade_id = int(trade_id_item.text())

        trade = next(
            (
                item for item in self.filtered_trades
                if item["id"] == trade_id
            ),
            None
        )

        self.close_button.setEnabled(
            trade is not None and trade["status"] == "Open"
        )

    def close_selected_trade(self):

        selected_row = self.table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(
                self,
                "No Trade Selected",
                "Pehle ek open trade select karo."
            )
            return

        trade_id = int(self.table.item(selected_row, 0).text())

        trade = next(
            (
                item for item in self.filtered_trades
                if item["id"] == trade_id
            ),
            None
        )

        if trade is None or trade["status"] != "Open":
            QMessageBox.warning(
                self,
                "Invalid Trade",
                "Selected trade open nahi hai."
            )
            return

        dialog = CloseTradeDialog(trade, self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        data = dialog.get_data()

        confirmation = QMessageBox.question(
            self,
            "Confirm Close Trade",
            f"Trade close karna chahte ho?\n\n"
            f"Exit Price: ₹{data['exit_price']:,.2f}\n"
            f"Exit Date: {data['exit_date']}",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        try:
            closed = close_trade(
                trade_id=trade_id,
                exit_price=data["exit_price"],
                exit_date=data["exit_date"],
                exit_fees=data["exit_fees"],
                other_charges=data["other_charges"],
                closing_notes=data["closing_notes"],
            )

            if closed:
                QMessageBox.information(
                    self,
                    "Trade Closed",
                    "Trade successfully close ho gaya!"
                )
                self.load_trades()

            else:
                QMessageBox.warning(
                    self,
                    "Not Found",
                    "Trade nahi mila. Refresh karke try karo."
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Close Trade Error",
                f"Trade close nahi hua:\n{error}"
            )

    def delete_selected_trade(self):

        selected_row = self.table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(
                self,
                "No Trade Selected",
                "Delete karne ke liye pehle table mein ek trade select karo.",
            )
            return

        trade_id = int(self.table.item(selected_row, 0).text())

        confirmation = QMessageBox.question(
            self,
            "Confirm Delete",
            "Kya tum selected trade permanently delete karna chahte ho?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirmation != QMessageBox.StandardButton.Yes:
            return

        try:
            deleted = delete_trade(trade_id)

            if deleted:
                QMessageBox.information(
                    self,
                    "Success",
                    "Trade successfully delete ho gaya.",
                )
                self.load_trades()

            else:
                QMessageBox.warning(
                    self,
                    "Not Found",
                    "Selected trade nahi mila. Refresh karke try karo.",
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Delete Error",
                f"Trade delete nahi hua:\n{error}",
            )