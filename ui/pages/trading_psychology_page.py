from collections import Counter

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

from PySide6.QtCore import Qt

from services.trade_service import get_all_trades


class TradingPsychologyPage(QWidget):

    def __init__(self):
        super().__init__()

        self.trades = []
        self.setup_ui()
        self.load_psychology()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(18)

        title = QLabel("Trading Psychology")
        title.setStyleSheet(
            "font-size: 26px; font-weight: bold; color: #F8FAFC;"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Understand your emotions, discipline and trading habits."
        )
        subtitle.setStyleSheet("font-size: 13px; color: #94A3B8;")
        layout.addWidget(subtitle)

        # Summary cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(12)

        self.metric_labels = {}

        metrics = [
            ("total", "TOTAL TRADES", "0"),
            ("followed", "PLAN FOLLOWED", "0"),
            ("discipline", "DISCIPLINE RATE", "0.0%"),
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
            card_layout.setContentsMargins(16, 18, 16, 18)
            card_layout.setSpacing(10)

            heading_label = QLabel(heading)
            heading_label.setStyleSheet(
                "font-size: 10px; font-weight: bold; color: #94A3B8;"
            )

            value_label = QLabel(initial_value)
            value_label.setStyleSheet(
                "font-size: 22px; font-weight: bold; color: #F8FAFC;"
            )

            card_layout.addWidget(heading_label)
            card_layout.addWidget(value_label)
            cards_layout.addWidget(card)

            self.metric_labels[key] = value_label

        layout.addLayout(cards_layout)

        # Emotion summary
        emotion_title = QLabel("Emotion Insights")
        emotion_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #F8FAFC;"
        )
        layout.addWidget(emotion_title)

        self.emotion_summary = QLabel()
        self.emotion_summary.setWordWrap(True)
        self.emotion_summary.setStyleSheet("""
            background-color: #111C30;
            border: 1px solid #263247;
            border-radius: 10px;
            padding: 16px;
            color: #CBD5E1;
            font-size: 13px;
        """)
        layout.addWidget(self.emotion_summary)

        # Psychology history table
        history_title = QLabel("Trade Psychology History")
        history_title.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #F8FAFC;"
        )
        layout.addWidget(history_title)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Date",
            "Symbol",
            "Emotion Before",
            "Emotion After",
            "Plan Followed",
            "Lessons Learned",
        ])

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        layout.addWidget(self.table, 1)

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

    def load_psychology(self):
        try:
            self.trades = get_all_trades()

            total_trades = len(self.trades)

            # Database default is 1, so this includes older trades
            # where the user did not explicitly record their discipline.
            followed_count = sum(
                1 for trade in self.trades
                if int(trade.get("followed_plan") or 0) == 1
            )

            discipline_rate = (
                followed_count / total_trades * 100
                if total_trades else 0
            )

            self.metric_labels["total"].setText(str(total_trades))
            self.metric_labels["followed"].setText(str(followed_count))
            self.metric_labels["discipline"].setText(
                f"{discipline_rate:.1f}%"
            )

            before_counter = Counter()
            after_counter = Counter()

            for trade in self.trades:
                before = trade.get("emotion_before")
                after = trade.get("emotion_after")

                if before:
                    before_counter[str(before)] += 1

                if after:
                    after_counter[str(after)] += 1

            before_text = (
                ", ".join(
                    f"{emotion}: {count}"
                    for emotion, count in before_counter.most_common()
                )
                or "No emotions recorded yet"
            )

            after_text = (
                ", ".join(
                    f"{emotion}: {count}"
                    for emotion, count in after_counter.most_common()
                )
                or "No emotions recorded yet"
            )

            self.emotion_summary.setText(
                f"Before Trade: {before_text}\n\n"
                f"After Trade: {after_text}\n\n"
                "Tip: Review repeated emotions and check whether they "
                "influence your trading decisions."
            )

            self.table.setRowCount(total_trades)

            # Newest trade dates first.
            sorted_trades = sorted(
                self.trades,
                key=lambda trade: str(trade.get("trade_date", "")),
                reverse=True,
            )

            self.table.setRowCount(len(sorted_trades))

            for row, trade in enumerate(sorted_trades):
                followed = (
                    "Yes"
                    if int(trade.get("followed_plan") or 0) == 1
                    else "No"
                )

                values = [
                    str(trade.get("trade_date", "")),
                    str(trade.get("symbol", "")),
                    str(trade.get("emotion_before") or "—"),
                    str(trade.get("emotion_after") or "—"),
                    followed,
                    str(trade.get("lessons_learned") or "—"),
                ]

                for column, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    if column == 4:
                        if followed == "Yes":
                            item.setForeground(Qt.GlobalColor.green)
                        else:
                            item.setForeground(Qt.GlobalColor.red)

                    self.table.setItem(row, column, item)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Psychology Error",
                f"Trading Psychology load nahi hua:\n{error}",
            )
