from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QScrollArea,
)
from PySide6.QtCore import Qt

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from database.connection import get_connection


class ChartCanvas(FigureCanvasQTAgg):

    def __init__(self, width=5, height=3):
        self.figure = Figure(
            figsize=(width, height),
            dpi=100,
            facecolor="#111c30"
        )

        super().__init__(self.figure)

        self.setStyleSheet("background-color: #111c30;")


class MistakeAnalyticsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: #0b1120;
                color: #e2e8f0;
                font-family: Segoe UI;
            }

            QFrame#analyticsCard {
                background-color: #111c30;
                border: 1px solid #263449;
                border-radius: 10px;
            }
        """)

        self.build_ui()
        self.load_analytics()

    # --------------------------------------------------
    # UI
    # --------------------------------------------------

    def build_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(16)

        heading = QLabel("Mistake Analytics Dashboard")
        heading.setStyleSheet("""
            color: #f8fafc;
            font-size: 24px;
            font-weight: bold;
        """)

        description = QLabel(
            "Understand your trading mistakes through data and charts."
        )
        description.setStyleSheet(
            "color: #94a3b8; font-size: 12px;"
        )

        main_layout.addWidget(heading)
        main_layout.addWidget(description)

        # Summary cards
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(12)

        self.total_label = self.create_card(
            summary_layout, "TOTAL MISTAKES", "0"
        )

        self.impact_label = self.create_card(
            summary_layout, "FINANCIAL IMPACT", "₹0.00"
        )

        self.common_label = self.create_card(
            summary_layout, "TOP MISTAKE", "None"
        )

        self.top_emotion_label = self.create_card(
            summary_layout, "TOP EMOTION", "None"
        )

        main_layout.addLayout(summary_layout)

        # Charts grid
        chart_grid = QGridLayout()
        chart_grid.setSpacing(14)

        # Chart 1
        mistake_card, self.mistake_chart = self.create_chart_card(
            "Mistake Type Analysis"
        )

        chart_grid.addWidget(mistake_card, 0, 0)

        # Chart 2
        emotion_card, self.emotion_chart = self.create_chart_card(
            "Trading Emotion Analysis"
        )

        chart_grid.addWidget(emotion_card, 0, 1)

        # Chart 3
        monthly_card, self.monthly_chart = self.create_chart_card(
            "Monthly Mistake Analysis"
        )

        chart_grid.addWidget(monthly_card, 1, 0)

        # Chart 4
        impact_card, self.impact_chart = self.create_chart_card(
            "Financial Impact by Mistake"
        )

        chart_grid.addWidget(impact_card, 1, 1)

        main_layout.addLayout(chart_grid)

        main_layout.addStretch()

    # --------------------------------------------------
    # SUMMARY CARDS
    # --------------------------------------------------

    def create_card(self, layout, title, value):

        card = QFrame()
        card.setObjectName("analyticsCard")
        card.setMinimumHeight(95)

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
    # CHART CARDS
    # --------------------------------------------------

    def create_chart_card(self, title):

        card = QFrame()
        card.setObjectName("analyticsCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #f8fafc;
            font-size: 14px;
            font-weight: bold;
        """)

        chart = ChartCanvas()

        layout.addWidget(title_label)
        layout.addWidget(chart)

        return card, chart

    # --------------------------------------------------
    # DATABASE
    # --------------------------------------------------

    def get_analytics_data(self):

        with get_connection() as connection:

            mistakes = connection.execute("""
                SELECT *
                FROM mistakes
                ORDER BY mistake_date ASC
            """).fetchall()

            mistake_types = connection.execute("""
                SELECT mistake_type, COUNT(*) AS total
                FROM mistakes
                GROUP BY mistake_type
                ORDER BY total DESC
            """).fetchall()

            emotions = connection.execute("""
                SELECT emotion, COUNT(*) AS total
                FROM mistakes
                GROUP BY emotion
                ORDER BY total DESC
            """).fetchall()

            monthly = connection.execute("""
                SELECT
                    strftime('%Y-%m', mistake_date) AS month,
                    COUNT(*) AS total
                FROM mistakes
                GROUP BY month
                ORDER BY month ASC
            """).fetchall()

            financial = connection.execute("""
                SELECT
                    mistake_type,
                    SUM(financial_impact) AS total_impact
                FROM mistakes
                GROUP BY mistake_type
                ORDER BY total_impact DESC
            """).fetchall()

            summary = connection.execute("""
                SELECT
                    COUNT(*) AS total,
                    COALESCE(SUM(financial_impact), 0) AS impact
                FROM mistakes
            """).fetchone()

        return {
            "mistakes": mistakes,
            "types": mistake_types,
            "emotions": emotions,
            "monthly": monthly,
            "financial": financial,
            "summary": summary,
        }

    # --------------------------------------------------
    # LOAD ANALYTICS
    # --------------------------------------------------

    def load_analytics(self):

        try:
            data = self.get_analytics_data()

            total = data["summary"]["total"]
            impact = float(data["summary"]["impact"] or 0)

            self.total_label.setText(str(total))
            self.impact_label.setText(f"₹{impact:,.2f}")

            if data["types"]:
                self.common_label.setText(
                    data["types"][0]["mistake_type"]
                )
            else:
                self.common_label.setText("None")

            if data["emotions"]:
                self.top_emotion_label.setText(
                    data["emotions"][0]["emotion"]
                )
            else:
                self.top_emotion_label.setText("None")

            self.draw_mistake_chart(data["types"])
            self.draw_emotion_chart(data["emotions"])
            self.draw_monthly_chart(data["monthly"])
            self.draw_impact_chart(data["financial"])

        except Exception as error:
            print(f"Mistake Analytics Error: {error}")

    # --------------------------------------------------
    # CHART 1: MISTAKE TYPE
    # --------------------------------------------------

    def draw_mistake_chart(self, rows):

        figure = self.mistake_chart.figure
        figure.clear()

        ax = figure.add_subplot(111)
        ax.set_facecolor("#111c30")

        if not rows:
            ax.text(
                0.5, 0.5, "No mistake data available",
                ha="center", va="center", color="white"
            )
            ax.set_axis_off()
        else:
            labels = [row["mistake_type"] for row in rows]
            values = [row["total"] for row in rows]

            bars = ax.barh(
                labels,
                values,
                color="#3b82f6"
            )

            ax.invert_yaxis()
            ax.set_xlabel("Number of Mistakes", color="#cbd5e1")

            for bar, value in zip(bars, values):
                ax.text(
                    bar.get_width(),
                    bar.get_y() + bar.get_height() / 2,
                    f" {value}",
                    va="center",
                    color="white"
                )

        self.style_axes(ax)
        figure.tight_layout()
        self.mistake_chart.draw()

    # --------------------------------------------------
    # CHART 2: EMOTIONS
    # --------------------------------------------------

    def draw_emotion_chart(self, rows):

        figure = self.emotion_chart.figure
        figure.clear()

        ax = figure.add_subplot(111)
        ax.set_facecolor("#111c30")

        if not rows:
            ax.text(
                0.5, 0.5, "No emotion data available",
                ha="center", va="center", color="white"
            )
            ax.set_axis_off()
        else:
            labels = [row["emotion"] for row in rows]
            values = [row["total"] for row in rows]

            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct="%1.1f%%",
                startangle=90,
                textprops={"color": "white", "fontsize": 9},
            )

            for text in autotexts:
                text.set_color("white")
                text.set_fontweight("bold")

        figure.tight_layout()
        self.emotion_chart.draw()

    # --------------------------------------------------
    # CHART 3: MONTHLY
    # --------------------------------------------------

    def draw_monthly_chart(self, rows):

        figure = self.monthly_chart.figure
        figure.clear()

        ax = figure.add_subplot(111)
        ax.set_facecolor("#111c30")

        if not rows:
            ax.text(
                0.5, 0.5, "No monthly data available",
                ha="center", va="center", color="white"
            )
            ax.set_axis_off()
        else:
            labels = [row["month"] for row in rows]
            values = [row["total"] for row in rows]

            ax.plot(
                labels,
                values,
                marker="o",
                linewidth=2,
                markersize=7,
                color="#22c55e"
            )

            ax.fill_between(
                range(len(values)),
                values,
                alpha=0.15,
                color="#22c55e"
            )

            ax.set_ylabel("Mistakes", color="#cbd5e1")
            ax.tick_params(axis="x", rotation=30)

        self.style_axes(ax)
        figure.tight_layout()
        self.monthly_chart.draw()

    # --------------------------------------------------
    # CHART 4: FINANCIAL IMPACT
    # --------------------------------------------------

    def draw_impact_chart(self, rows):

        figure = self.impact_chart.figure
        figure.clear()

        ax = figure.add_subplot(111)
        ax.set_facecolor("#111c30")

        if not rows:
            ax.text(
                0.5, 0.5, "No financial data available",
                ha="center", va="center", color="white"
            )
            ax.set_axis_off()
        else:
            labels = [row["mistake_type"] for row in rows]
            values = [
                float(row["total_impact"] or 0)
                for row in rows
            ]

            bars = ax.barh(
                labels,
                values,
                color="#f97316"
            )

            ax.invert_yaxis()
            ax.set_xlabel("Financial Impact (₹)", color="#cbd5e1")

            for bar, value in zip(bars, values):
                ax.text(
                    bar.get_width(),
                    bar.get_y() + bar.get_height() / 2,
                    f" ₹{value:,.2f}",
                    va="center",
                    color="white",
                    fontsize=8
                )

        self.style_axes(ax)
        figure.tight_layout()
        self.impact_chart.draw()

    # --------------------------------------------------
    # COMMON CHART STYLE
    # --------------------------------------------------

    def style_axes(self, ax):

        ax.tick_params(
            axis="both",
            colors="#cbd5e1",
            labelsize=8
        )

        ax.xaxis.label.set_color("#cbd5e1")
        ax.yaxis.label.set_color("#cbd5e1")

        for spine in ax.spines.values():
            spine.set_color("#334155")

        ax.grid(
            axis="x",
            color="#334155",
            linestyle="--",
            alpha=0.35
        )
