from collections import defaultdict
from datetime import date

from PySide6.QtCore import Qt, QDate
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QCalendarWidget,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)

from services.trade_service import get_all_trades


class TradingCalendarPage(QWidget):

    def __init__(self):
        super().__init__()

        self.trades = []
        self.daily_stats = defaultdict(
            lambda: {
                "trades": 0,
                "net_pnl": 0.0,
                "wins": 0,
                "losses": 0,
            }
        )

        self.setup_ui()
        self.load_trades()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title = QLabel("Trading Calendar")
        title.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #F8FAFC;"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Review your trading activity and daily performance."
        )
        subtitle.setStyleSheet("color: #94A3B8; font-size: 13px;")
        layout.addWidget(subtitle)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(18)

        # Calendar
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
        )
        self.calendar.setMinimumWidth(320)
        self.calendar.setSelectedDate(QDate.currentDate())
        self.calendar.selectionChanged.connect(
            self.show_selected_date
        )
        self.calendar.currentPageChanged.connect(
            self.update_calendar_marks
        )

        content_layout.addWidget(self.calendar, 1)

        # Selected date details
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background-color: #111C30;
                border: 1px solid #263247;
                border-radius: 10px;
            }
        """)

        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(18, 18, 18, 18)
        details_layout.setSpacing(12)

        self.selected_date_label = QLabel("Selected Date")
        self.selected_date_label.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #F8FAFC;"
        )
        details_layout.addWidget(self.selected_date_label)

        self.daily_trades_label = QLabel("Trades: 0")
        self.daily_pnl_label = QLabel("Net P&L: ₹0.00")
        self.daily_wins_label = QLabel("Winning Trades: 0")
        self.daily_losses_label = QLabel("Losing Trades: 0")

        for label in (
            self.daily_trades_label,
            self.daily_pnl_label,
            self.daily_wins_label,
            self.daily_losses_label,
        ):
            label.setStyleSheet(
                "font-size: 14px; color: #CBD5E1; padding: 4px;"
            )
            details_layout.addWidget(label)

        details_layout.addStretch()
        content_layout.addWidget(details_frame, 1)

        layout.addLayout(content_layout, 2)

        # Selected date's trades
        table_title = QLabel("Trades on Selected Date")
        table_title.setStyleSheet(
            "font-size: 17px; font-weight: bold; color: #F8FAFC;"
        )
        layout.addWidget(table_title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Symbol",
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
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table, 2)

        self.setStyleSheet("""
            QWidget {
                background-color: #0B1120;
                color: #E2E8F0;
            }

            QCalendarWidget QWidget {
                background-color: #111C30;
                color: #E2E8F0;
            }

            QCalendarWidget QToolButton {
                color: #F8FAFC;
                background-color: #1E293B;
                padding: 6px;
                border-radius: 4px;
            }

            QCalendarWidget QMenu {
                background-color: #111C30;
                color: #F8FAFC;
            }

            QCalendarWidget QSpinBox {
                background-color: #1E293B;
                color: #F8FAFC;
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
                padding: 8px;
                border: 1px solid #334155;
            }
        """)

    def calculate_trade_pnl(self, trade):
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

    def load_trades(self):
        try:
            self.trades = get_all_trades()
            self.daily_stats.clear()

            for trade in self.trades:
                trade_date = str(trade.get("trade_date", ""))[:10]

                try:
                    date.fromisoformat(trade_date)
                except ValueError:
                    continue

                # Sirf closed trades ka realized P&L calculate hoga.
                pnl = self.calculate_trade_pnl(trade)

                if pnl is None:
                    continue

                stats = self.daily_stats[trade_date]
                stats["trades"] += 1
                stats["net_pnl"] += pnl

                if pnl > 0:
                    stats["wins"] += 1
                elif pnl < 0:
                    stats["losses"] += 1

            self.update_calendar_marks()
            self.show_selected_date()

        except Exception as error:
            QMessageBox.critical(
                self,
                "Calendar Error",
                f"Trading calendar load nahi hua:\n{error}",
            )

    def update_calendar_marks(self, *args):
        current_month = self.calendar.monthShown()
        current_year = self.calendar.yearShown()

        # Reset all date formats before marking current month's days.
        self.calendar.setDateTextFormat(
            QDate(),
            self.calendar.dateTextFormat(QDate())
        )

        for trade_date, stats in self.daily_stats.items():
            try:
                parsed_date = date.fromisoformat(trade_date)
            except ValueError:
                continue

            if (
                parsed_date.month != current_month
                or parsed_date.year != current_year
            ):
                continue

            calendar_date = QDate(
                parsed_date.year,
                parsed_date.month,
                parsed_date.day,
            )

            if stats["net_pnl"] > 0:
                background = "#14532D"
            elif stats["net_pnl"] < 0:
                background = "#7F1D1D"
            else:
                background = "#334155"

            from PySide6.QtGui import QTextCharFormat, QColor

            text_format = QTextCharFormat()
            text_format.setBackground(QColor(background))
            text_format.setForeground(QColor("#FFFFFF"))

            self.calendar.setDateTextFormat(
                calendar_date,
                text_format,
            )

    def show_selected_date(self):
        selected = self.calendar.selectedDate()
        selected_text = selected.toString("yyyy-MM-dd")

        stats = self.daily_stats.get(
            selected_text,
            {
                "trades": 0,
                "net_pnl": 0.0,
                "wins": 0,
                "losses": 0,
            },
        )

        self.selected_date_label.setText(
            f"Date: {selected.toString('dd MMM yyyy')}"
        )
        self.daily_trades_label.setText(
            f"Closed Trades: {stats['trades']}"
        )
        self.daily_pnl_label.setText(
            f"Net P&L: ₹{stats['net_pnl']:,.2f}"
        )
        self.daily_wins_label.setText(
            f"Winning Trades: {stats['wins']}"
        )
        self.daily_losses_label.setText(
            f"Losing Trades: {stats['losses']}"
        )

        selected_trades = [
            trade for trade in self.trades
            if str(trade.get("trade_date", ""))[:10] == selected_text
        ]

        self.table.setRowCount(len(selected_trades))

        for row, trade in enumerate(selected_trades):
            pnl = self.calculate_trade_pnl(trade)

            values = [
                str(trade.get("symbol", "")),
                str(trade.get("direction", "")),
                f"{float(trade.get('entry_price') or 0):,.2f}",
                (
                    f"{float(trade['exit_price']):,.2f}"
                    if trade.get("exit_price") not in (None, "")
                    else "—"
                ),
                f"₹{pnl:,.2f}" if pnl is not None else "—",
                str(trade.get("status", "")),
            ]

            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if column == 4 and pnl is not None:
                    if pnl > 0:
                        item.setForeground(Qt.GlobalColor.green)
                    elif pnl < 0:
                        item.setForeground(Qt.GlobalColor.red)

                self.table.setItem(row, column, item)

