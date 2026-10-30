from collections import defaultdict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)

from services.trade_service import get_all_trades


class PerformanceAnalyticsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.trades = []
        self.setup_ui()
        self.load_analytics()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)

        title = QLabel("Performance Analytics")
        title.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #F8FAFC;"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Understand your results using closed-trade performance metrics."
        )
        subtitle.setStyleSheet("font-size: 13px; color: #94A3B8;")
        layout.addWidget(subtitle)

        # Metric cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.metric_labels = {}

        metrics = [
            ("total_closed", "CLOSED TRADES", "0"),
            ("win_rate", "WIN RATE", "0.0%"),
            ("profit_factor", "PROFIT FACTOR", "0.00"),
            ("net_pnl", "NET P&L", "₹0.00"),
        ]

        for key, heading, initial_value in metrics:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #111C30;
                    border: 1px solid #263247;
                    border-radius: 10px;
                }
            """)

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(14, 18, 14, 18)
            card_layout.setSpacing(10)

            heading_label = QLabel(heading)
            heading_label.setStyleSheet(
                "font-size: 10px; font-weight: bold; color: #94A3B8;"
            )

            value_label = QLabel(initial_value)
            value_label.setStyleSheet(
                "font-size: 21px; font-weight: bold; color: #F8FAFC;"
            )

            card_layout.addWidget(heading_label)
            card_layout.addWidget(value_label)
            cards_layout.addWidget(card)

            self.metric_labels[key] = value_label

        layout.addLayout(cards_layout)

        # Additional statistics
        self.additional_stats = QLabel()
        self.additional_stats.setWordWrap(True)
        self.additional_stats.setStyleSheet("""
            background-color: #111C30;
            border: 1px solid #263247;
            border-radius: 10px;
            padding: 16px;
            color: #CBD5E1;
            font-size: 13px;
        """)
        layout.addWidget(self.additional_stats)

        # Equity curve heading
        curve_title = QLabel("Realized Equity Curve")
        curve_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #F8FAFC;"
        )
        layout.addWidget(curve_title)

        self.curve_description = QLabel(
            "Cumulative realized P&L from closed trades."
        )
        self.curve_description.setStyleSheet(
            "font-size: 12px; color: #94A3B8;"
        )
        layout.addWidget(self.curve_description)

        # Table-based equity curve: avoids additional chart dependencies.
        self.curve_table = QTableWidget()
        self.curve_table.setColumnCount(4)
        self.curve_table.setHorizontalHeaderLabels([
            "Trade Date",
            "Symbol",
            "Trade Net P&L",
            "Cumulative Net P&L",
        ])
        self.curve_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.curve_table.verticalHeader().setVisible(False)
        self.curve_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.curve_table.setAlternatingRowColors(True)
        self.curve_table.setMinimumHeight(230)

        layout.addWidget(self.curve_table, 1)

        self.setStyleSheet("""
            QWidget {
                background-color: #0B1120;
                color: #E2E8F0;
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

    def calculate_pnl(self, trade):
        if trade.get("status") != "Closed":
            return None

        exit_value = trade.get("exit_price")

        if exit_value in (None, ""):
            return None

        entry = float(trade.get("entry_price") or 0)
        exit_price = float(exit_value)
        quantity = float(trade.get("quantity") or 0)
        multiplier = float(trade.get("multiplier") or 1)

        if trade.get("direction") == "Short":
            gross_pnl = (entry - exit_price) * quantity * multiplier
        else:
            gross_pnl = (exit_price - entry) * quantity * multiplier

        charges = (
            float(trade.get("entry_fees") or 0)
            + float(trade.get("exit_fees") or 0)
            + float(trade.get("other_charges") or 0)
        )

        return gross_pnl - charges

    def load_analytics(self):
        try:
            self.trades = get_all_trades()

            closed_results = []

            for trade in self.trades:
                pnl = self.calculate_pnl(trade)

                if pnl is not None:
                    closed_results.append({
                        "date": str(trade.get("trade_date", ""))[:10],
                        "symbol": str(trade.get("symbol", "")),
                        "pnl": pnl,
                    })

            total_closed = len(closed_results)
            winning = [t["pnl"] for t in closed_results if t["pnl"] > 0]
            losing = [t["pnl"] for t in closed_results if t["pnl"] < 0]

            net_pnl = sum(t["pnl"] for t in closed_results)
            gross_profit = sum(winning)
            gross_loss = abs(sum(losing))

            win_rate = (
                len(winning) / total_closed * 100
                if total_closed else 0
            )

            if gross_loss > 0:
                profit_factor = gross_profit / gross_loss
                profit_factor_text = f"{profit_factor:.2f}"
            elif gross_profit > 0:
                profit_factor_text = "∞"
            else:
                profit_factor_text = "N/A"

            self.metric_labels["total_closed"].setText(str(total_closed))
            self.metric_labels["win_rate"].setText(f"{win_rate:.1f}%")
            self.metric_labels["profit_factor"].setText(profit_factor_text)
            self.metric_labels["net_pnl"].setText(f"₹{net_pnl:,.2f}")

            avg_win = gross_profit / len(winning) if winning else 0
            avg_loss = gross_loss / len(losing) if losing else 0

            self.additional_stats.setText(
                f"Winning Trades: {len(winning)}     |     "
                f"Losing Trades: {len(losing)}\n\n"
                f"Gross Profit: ₹{gross_profit:,.2f}     |     "
                f"Gross Loss: ₹{gross_loss:,.2f}\n\n"
                f"Average Win: ₹{avg_win:,.2f}     |     "
                f"Average Loss: ₹{avg_loss:,.2f}"
            )

            # Sort by date, then calculate cumulative realized P&L.
            closed_results.sort(key=lambda item: item["date"])

            self.curve_table.setRowCount(len(closed_results))
            cumulative_pnl = 0.0

            for row, result in enumerate(closed_results):
                cumulative_pnl += result["pnl"]

                values = [
                    result["date"],
                    result["symbol"],
                    f"₹{result['pnl']:,.2f}",
                    f"₹{cumulative_pnl:,.2f}",
                ]

                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    if column in (2, 3):
                        amount = (
                            result["pnl"]
                            if column == 2
                            else cumulative_pnl
                        )

                        if amount > 0:
                            item.setForeground(Qt.GlobalColor.green)
                        elif amount < 0:
                            item.setForeground(Qt.GlobalColor.red)

                    self.curve_table.setItem(row, column, item)

            if not closed_results:
                self.curve_description.setText(
                    "No closed trades yet. Close a trade to start tracking "
                    "your realized equity curve."
                )
            else:
                self.curve_description.setText(
                    f"{total_closed} closed trades | "
                    f"Final cumulative realized P&L: ₹{cumulative_pnl:,.2f}"
                )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Analytics Error",
                f"Performance analytics load nahi hui:\n{error}",
            )

