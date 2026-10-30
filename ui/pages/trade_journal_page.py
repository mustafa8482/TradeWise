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
)
from PySide6.QtCore import Qt

from services.trade_service import get_all_trades, delete_trade


class TradeJournalPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setObjectName("TradeJournalPage")
        self.setup_ui()
        self.load_trades()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Page heading
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

        # Search and refresh
        toolbar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by symbol or strategy...")
        self.search_input.setMinimumHeight(38)
        self.search_input.textChanged.connect(self.filter_trades)

        refresh_button = QPushButton("Refresh")
        refresh_button.setMinimumHeight(38)
        refresh_button.clicked.connect(self.load_trades)

        toolbar.addWidget(self.search_input)
        toolbar.addWidget(refresh_button)

        layout.addLayout(toolbar)

        # Summary
        self.summary_label = QLabel("Total Trades: 0")
        self.summary_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #CBD5E1;"
        )
        layout.addWidget(self.summary_label)

        # Trades table
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

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        delete_button = QPushButton("Delete Selected Trade")
        delete_button.setMinimumHeight(40)
        delete_button.clicked.connect(self.delete_selected_trade)

        bottom_layout.addWidget(delete_button)
        layout.addLayout(bottom_layout)

        # Dark professional theme
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
            self.filter_trades()
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

        self.table.setRowCount(len(filtered_trades))

        for row, trade in enumerate(filtered_trades):
            entry_price = float(trade.get("entry_price") or 0)
            exit_value = trade.get("exit_price")

            if trade.get("status") == "Closed" and exit_value not in (None, ""):
                exit_price = float(exit_value)
                quantity = float(trade.get("quantity") or 0)
                multiplier = float(trade.get("multiplier") or 1)

                if trade.get("direction") == "Short":
                    gross_pnl = (entry_price - exit_price) * quantity * multiplier
                else:
                    gross_pnl = (exit_price - entry_price) * quantity * multiplier

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

    def delete_selected_trade(self):
        selected_row = self.table.currentRow()

        if selected_row < 0:
            QMessageBox.warning(
                self,
                "No Trade Selected",
                "Delete karne ke liye pehle table mein ek trade select karo.",
            )
            return

        trade_id_item = self.table.item(selected_row, 0)

        if trade_id_item is None:
            return

        trade_id = int(trade_id_item.text())

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

