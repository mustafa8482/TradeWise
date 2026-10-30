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
)

from services.trade_service import get_all_trades


class StrategyAnalysisPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        print("Strategy Analysis UI created")
        self.load_strategy_data()
        print("Strategy Analysis data loading finished")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        title = QLabel("Strategy Analysis")
        title.setStyleSheet(
            "font-size: 26px; font-weight: 700; color: #F8FAFC;"
        )

        subtitle = QLabel(
            "Analyze your trading strategies using historical trade data."
        )
        subtitle.setStyleSheet("color: #94A3B8; font-size: 12px;")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(14)

        self.total_strategies_card, self.total_strategies_value = (
            self.create_card("TOTAL STRATEGIES")
        )
        self.total_trades_card, self.total_trades_value = (
            self.create_card("CLOSED TRADES")
        )
        self.total_pnl_card, self.total_pnl_value = (
            self.create_card("TOTAL NET P&L")
        )
        self.best_strategy_card, self.best_strategy_value = (
            self.create_card("BEST STRATEGY")
        )

        for card in (
            self.total_strategies_card,
            self.total_trades_card,
            self.total_pnl_card,
            self.best_strategy_card,
        ):
            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)

        table_title = QLabel("Strategy Performance")
        table_title.setStyleSheet(
            "font-size: 18px; font-weight: 600; color: #F8FAFC;"
        )
        layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Strategy",
            "Total Trades",
            "Wins",
            "Losses",
            "Win Rate",
            "Net P&L",
        ])

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #111C30;
                color: #E2E8F0;
                gridline-color: #263247;
                border: 1px solid #263247;
                border-radius: 8px;
            }
            QHeaderView::section {
                background-color: #1E293B;
                color: #F8FAFC;
                padding: 10px;
                border: none;
                font-weight: 600;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #334155;
            }
        """)

        layout.addWidget(self.table)

        note = QLabel(
            "Win Rate = winning closed trades / all closed trades. "
            "Past performance does not guarantee future results."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #94A3B8; font-size: 11px;")
        layout.addWidget(note)

        self.setStyleSheet("""
            QWidget {
                background-color: #0B1120;
                color: #F8FAFC;
            }
        """)

    def create_card(self, heading):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #111C30;
                border: 1px solid #263247;
                border-radius: 10px;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        label = QLabel(heading)
        label.setStyleSheet(
            "color: #94A3B8; font-size: 10px; font-weight: 600;"
        )

        value = QLabel("--")
        value.setStyleSheet(
            "color: #F8FAFC; font-size: 20px; font-weight: 700;"
        )
        value.setWordWrap(True)

        card_layout.addWidget(label)
        card_layout.addWidget(value)

        return card, value
    
    def load_strategy_data(self):
        try:
            trades = get_all_trades()
            strategies = {}

            for trade in trades:
                # Database se dictionary values read karo
                status = str(trade.get("status", "")).lower()

                # Sirf closed trades count honge
                if status != "closed":
                    continue

                strategy_name = trade.get("strategy") or "Unspecified"

                entry_price = float(trade.get("entry_price") or 0)
                exit_price = float(trade.get("exit_price") or 0)
                quantity = float(trade.get("quantity") or 0)
                multiplier = float(trade.get("multiplier") or 1)

                entry_fees = float(trade.get("entry_fees") or 0)
                exit_fees = float(trade.get("exit_fees") or 0)
                other_charges = float(trade.get("other_charges") or 0)

                direction = str(trade.get("direction") or "Long").lower()

                # Gross P&L calculate karo
                if direction == "short":
                    gross_pnl = (
                        (entry_price - exit_price)
                        * quantity
                        * multiplier
                    )
                else:
                    gross_pnl = (
                        (exit_price - entry_price)
                        * quantity
                        * multiplier
                    )

                # Charges subtract karke Net P&L
                pnl = gross_pnl - entry_fees - exit_fees - other_charges

                if strategy_name not in strategies:
                    strategies[strategy_name] = {
                        "trades": 0,
                        "wins": 0,
                        "losses": 0,
                        "pnl": 0.0,
                    }

                item = strategies[strategy_name]
                item["trades"] += 1
                item["pnl"] += pnl

                if pnl > 0:
                    item["wins"] += 1
                elif pnl < 0:
                    item["losses"] += 1

            # Table update karo
            self.table.setRowCount(len(strategies))

            total_closed = 0
            total_pnl = 0.0

            sorted_strategies = sorted(
                strategies.items(),
                key=lambda item: item[1]["pnl"],
                reverse=True,
            )

            for row, (name, data) in enumerate(sorted_strategies):
                count = data["trades"]
                wins = data["wins"]
                losses = data["losses"]
                pnl = data["pnl"]

                win_rate = (wins / count * 100) if count else 0

                values = [
                    name,
                    str(count),
                    str(wins),
                    str(losses),
                    f"{win_rate:.1f}%",
                    f"₹{pnl:,.2f}",
                ]

                for column, value in enumerate(values):
                    cell = QTableWidgetItem(value)
                    cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    if column == 5:
                        if pnl > 0:
                            cell.setForeground(Qt.GlobalColor.green)
                        elif pnl < 0:
                            cell.setForeground(Qt.GlobalColor.red)

                    self.table.setItem(row, column, cell)

                total_closed += count
                total_pnl += pnl

            # Summary cards update karo
            self.total_strategies_value.setText(str(len(strategies)))
            self.total_trades_value.setText(str(total_closed))
            self.total_pnl_value.setText(f"₹{total_pnl:,.2f}")

            if strategies:
                best_name, best_data = max(
                    strategies.items(),
                    key=lambda item: item[1]["pnl"],
                )

                self.best_strategy_value.setText(best_name)
                self.best_strategy_value.setToolTip(
                    f"Net P&L: ₹{best_data['pnl']:,.2f}"
                )
            else:
                self.best_strategy_value.setText("No data")

            if total_pnl > 0:
                color = "#22C55E"
            elif total_pnl < 0:
                color = "#EF4444"
            else:
                color = "#F8FAFC"

            self.total_pnl_value.setStyleSheet(
                f"color: {color}; font-size: 20px; font-weight: 700;"
            )

        except Exception as error:
            print("Strategy Analysis Error:", repr(error))

            self.table.setRowCount(1)
            self.table.setColumnCount(1)
            self.table.setHorizontalHeaderLabels(["Error"])
            self.table.setItem(
                0,
                0,
                QTableWidgetItem(str(error)),
            )

            self.total_strategies_value.setText("Error")
            self.total_trades_value.setText("--")
            self.total_pnl_value.setText("--")
            self.best_strategy_value.setText("--")

