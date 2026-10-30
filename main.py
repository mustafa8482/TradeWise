import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QStackedWidget,
    QScrollArea,
)

from services.trade_service import (get_trade_statistics,get_equity_curve_data,get_drawdown_statistics,get_risk_management_statistics)

from ui.pages.add_trade_page import AddTradePage
from ui.pages.trade_journal_page import TradeJournalPage
from ui.pages.trading_calendar_page import TradingCalendarPage
from ui.pages.performance_analytics_page import PerformanceAnalyticsPage
from ui.pages.trading_psychology_page import TradingPsychologyPage
from ui.pages.strategy_analysis_page import StrategyAnalysisPage
from ui.pages.mistake_journal_page import MistakeJournalPage
from ui.pages.mistake_analytics_page import MistakeAnalyticsPage
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class EquityCurveChart(FigureCanvasQTAgg):

    def __init__(self, parent=None):
        self.figure = Figure(figsize=(8, 3), facecolor="#111C30")
        self.axes = self.figure.add_subplot(111)

        super().__init__(self.figure)
        self.setParent(parent)

        self.setMinimumHeight(300)

        self.figure.subplots_adjust(
            left=0.10,
            right=0.97,
            top=0.90,
            bottom=0.20
        )

    def plot_data(self, data):
        self.axes.clear()
        self.axes.set_facecolor("#111C30")

        if not data:
            self.axes.text(
                0.5, 0.5,
                "No closed trades available",
                color="#94A3B8",
                ha="center",
                va="center",
                transform=self.axes.transAxes
            )
        else:
            dates = [item["date"] for item in data]
            equity = [item["equity"] for item in data]

            self.axes.plot(
                range(len(equity)),
                equity,
                linewidth=2,
                marker="o",
                markersize=4
            )

            self.axes.fill_between(
                range(len(equity)),
                equity,
                alpha=0.12
            )

            self.axes.set_xticks(range(len(dates)))
            self.axes.set_xticklabels(
                dates,
                rotation=30,
                ha="right",
                fontsize=8,
                color="#94A3B8"
            )

        self.axes.set_title(
            "Cumulative Net P&L",
            color="#F8FAFC"
        )

        self.axes.set_ylabel("Equity (₹)", color="#94A3B8")
        self.axes.tick_params(axis="y", colors="#94A3B8")

        for spine in self.axes.spines.values():
            spine.set_color("#263247")

        self.axes.grid(True, alpha=0.15, linestyle="--")

        self.draw()


class TradeWiseApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("TradeWise | Trading Journal")
        self.resize(1250, 780)
        self.setMinimumSize(950, 600)

        self.stat_labels = {}

        self.setup_ui()
        self.refresh_dashboard()

    def setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(230)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 24, 18, 20)
        sidebar_layout.setSpacing(10)

        logo = QLabel("TradeWise")
        logo.setObjectName("logo")

        subtitle = QLabel("TRADING JOURNAL")
        subtitle.setObjectName("sidebarSubtitle")

        sidebar_layout.addWidget(logo)
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addSpacing(25)

        self.nav_buttons = []

        navigation_items = [
            "Dashboard",
            "Trade Journal",
            "Add Trade",
            "Trading Calendar",
            "Performance Analytics",
            "Trading Psychology",
            "Strategy Analysis",
            "Mistake Journal",
            "Mistake Analytics",
            "Reports & Export",
            "Settings & Backup",
        ]

        for index, item in enumerate(navigation_items):
            button = QPushButton(item)
            button.setObjectName("navButton")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setCheckable(True)

            if index == 0:
                button.setChecked(True)

            button.clicked.connect(
                lambda checked=False, name=item: self.select_page(name)
            )

            sidebar_layout.addWidget(button)
            self.nav_buttons.append(button)

        sidebar_layout.addStretch()

        version_label = QLabel("TradeWise v0.1.0")
        version_label.setObjectName("versionLabel")
        sidebar_layout.addWidget(version_label)

        # Main content
        content = QWidget()
        content.setObjectName("content")

        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(28, 24, 28, 24)
        content_layout.setSpacing(18)

        toolbar = QHBoxLayout()

        self.page_title = QLabel("Dashboard")
        self.page_title.setObjectName("pageTitle")

        toolbar_status = QLabel("● DATABASE CONNECTED")
        toolbar_status.setObjectName("statusLabel")

        toolbar.addWidget(self.page_title)
        toolbar.addStretch()
        toolbar.addWidget(toolbar_status)

        content_layout.addLayout(toolbar)

        # Stacked pages
        self.pages = QStackedWidget()

        # 0: Dashboard
        dashboard_page = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_page)
        dashboard_layout.setContentsMargins(0, 0, 0, 0)
        dashboard_layout.setSpacing(18)

        welcome_card = QFrame()
        welcome_card.setObjectName("welcomeCard")

        welcome_layout = QVBoxLayout(welcome_card)
        welcome_layout.setContentsMargins(24, 22, 24, 22)
        welcome_layout.setSpacing(10)

        welcome_title = QLabel("Welcome to TradeWise")
        welcome_title.setObjectName("welcomeTitle")

        welcome_description = QLabel(
            "Your trading performance. Your discipline. Your progress."
        )
        welcome_description.setObjectName("description")

        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_description)

        dashboard_layout.addWidget(welcome_card)

        stats_heading = QLabel("Performance Overview")
        stats_heading.setObjectName("sectionTitle")
        dashboard_layout.addWidget(stats_heading)

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(12)

        stats_config = [
            ("total_trades", "TOTAL TRADES", "0"),
            ("net_pnl", "NET P&L", "₹0.00"),
            ("win_rate", "WIN RATE", "0.0%"),
            ("open_trades", "OPEN TRADES", "0"),
        ]

        for key, title, initial_value in stats_config:
            card = QFrame()
            card.setObjectName("statCard")

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 18, 15, 18)
            card_layout.setSpacing(12)

            title_label = QLabel(title)
            title_label.setObjectName("statTitle")

            value_label = QLabel(initial_value)
            value_label.setObjectName("statValue")

            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)

            stats_layout.addWidget(card)
            self.stat_labels[key] = value_label

        dashboard_layout.addLayout(stats_layout)

        # Equity Curve Card
        equity_card = QFrame()
        equity_card.setObjectName("emptyCard")

        equity_layout = QVBoxLayout(equity_card)
        equity_layout.setContentsMargins(18, 18, 18, 18)
        equity_layout.setSpacing(10)

        equity_title = QLabel("Equity Curve")
        equity_title.setObjectName("emptyTitle")

        equity_subtitle = QLabel(
            "Your cumulative trading profit and loss over time."
        )
        equity_subtitle.setObjectName("description")

        self.equity_chart = EquityCurveChart()

        equity_layout.addWidget(equity_title)
        equity_layout.addWidget(equity_subtitle)
        equity_layout.addWidget(self.equity_chart)

        dashboard_layout.addWidget(equity_card)

        # Drawdown Analytics Section
        drawdown_heading = QLabel("Drawdown Analytics")
        drawdown_heading.setObjectName("sectionTitle")

        dashboard_layout.addWidget(drawdown_heading)

        drawdown_layout = QHBoxLayout()
        drawdown_layout.setSpacing(12)

        drawdown_config = [        
    ("peak_equity", "PEAK EQUITY", "₹0.00"),
    ("current_drawdown", "CURRENT DRAWDOWN", "₹0.00"),
    ("max_drawdown", "MAX DRAWDOWN", "₹0.00"),
    ("max_drawdown_percent", "MAX DRAWDOWN %", "0.00%"),
]

        self.drawdown_labels = {}

        for key, title, initial_value in drawdown_config:
            card = QFrame()
            card.setObjectName("statCard")
        
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 18, 15, 18)
            card_layout.setSpacing(12)
        
            title_label = QLabel(title)
            title_label.setObjectName("statTitle")
        
            value_label = QLabel(initial_value)
            value_label.setObjectName("statValue")
        
            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)
        
            drawdown_layout.addWidget(card)
            self.drawdown_labels[key] = value_label
        
        dashboard_layout.addLayout(drawdown_layout)

        # Risk Management Section
        risk_heading = QLabel("Risk Management")
        risk_heading.setObjectName("sectionTitle")

        dashboard_layout.addWidget(risk_heading)

        risk_layout = QHBoxLayout()
        risk_layout.setSpacing(12)

        risk_config = [
            ("average_risk_reward", "AVERAGE RISK / REWARD", "0.00"),
            ("average_risk", "AVERAGE RISK", "₹0.00"),
            ("largest_winning_trade", "LARGEST WIN", "₹0.00"),
            ("largest_losing_trade", "LARGEST LOSS", "₹0.00"),
            ("consecutive_wins", "CONSECUTIVE WINS", "0"),
            ("consecutive_losses", "CONSECUTIVE LOSSES", "0"),
        ]

        self.risk_labels = {}

        for key, title, initial_value in risk_config:
            card = QFrame()
            card.setObjectName("statCard")

            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(12, 16, 12, 16)
            card_layout.setSpacing(10)

            title_label = QLabel(title)
            title_label.setObjectName("statTitle")
            title_label.setWordWrap(True)

            value_label = QLabel(initial_value)
            value_label.setObjectName("statValue")

            card_layout.addWidget(title_label)
            card_layout.addWidget(value_label)

            risk_layout.addWidget(card)
            self.risk_labels[key] = value_label

        dashboard_layout.addLayout(risk_layout)




        activity_card = QFrame()
        activity_card.setObjectName("emptyCard")

        activity_layout = QVBoxLayout(activity_card)
        activity_layout.setContentsMargins(22, 22, 22, 22)
        activity_layout.setSpacing(10)

        activity_title = QLabel("Trading Journal Overview")
        activity_title.setObjectName("emptyTitle")

        self.activity_description = QLabel(
            "Your recorded trades will appear here."
        )
        self.activity_description.setObjectName("description")
        self.activity_description.setWordWrap(True)

        activity_layout.addWidget(activity_title)
        activity_layout.addWidget(self.activity_description)

        dashboard_layout.addWidget(activity_card, 1)

        self.pages.addWidget(dashboard_page)# Dashboard Scroll Area
        dashboard_scroll = QScrollArea()
        dashboard_scroll.setWidgetResizable(True)
        dashboard_scroll.setFrameShape(QFrame.Shape.NoFrame)
        dashboard_scroll.setWidget(dashboard_page)

        self.pages.addWidget(dashboard_scroll)  # Index 0 

        # 1: Add Trade
        self.add_trade_page = AddTradePage()
        self.add_trade_page.trade_saved.connect(self.refresh_dashboard)

        add_trade_scroll = QScrollArea()
        add_trade_scroll.setWidgetResizable(True)
        add_trade_scroll.setFrameShape(QFrame.Shape.NoFrame)
        add_trade_scroll.setWidget(self.add_trade_page)

        self.pages.addWidget(add_trade_scroll)

        # 2: Trade Journal
        self.trade_journal_page = TradeJournalPage()

        trade_journal_scroll = QScrollArea()
        trade_journal_scroll.setWidgetResizable(True)
        trade_journal_scroll.setFrameShape(QFrame.Shape.NoFrame)
        trade_journal_scroll.setWidget(self.trade_journal_page)

        self.pages.addWidget(trade_journal_scroll)

        # 3: Trading Calendar
        self.trading_calendar_page = TradingCalendarPage()

        calendar_scroll = QScrollArea()
        calendar_scroll.setWidgetResizable(True)
        calendar_scroll.setFrameShape(QFrame.Shape.NoFrame)
        calendar_scroll.setWidget(self.trading_calendar_page)

        self.pages.addWidget(calendar_scroll)

        # 4: Performance Analytics
        self.performance_analytics_page = PerformanceAnalyticsPage()

        analytics_scroll = QScrollArea()
        analytics_scroll.setWidgetResizable(True)
        analytics_scroll.setFrameShape(QFrame.Shape.NoFrame)
        analytics_scroll.setWidget(self.performance_analytics_page)

        self.pages.addWidget(analytics_scroll)

        # 5: Trading Psychology
        self.trading_psychology_page = TradingPsychologyPage()

        psychology_scroll = QScrollArea()
        psychology_scroll.setWidgetResizable(True)
        psychology_scroll.setFrameShape(QFrame.Shape.NoFrame)
        psychology_scroll.setWidget(self.trading_psychology_page)

        self.pages.addWidget(psychology_scroll)

        # 6: Strategy Analysis — actual page
        self.strategy_analysis_page = StrategyAnalysisPage()

        strategy_scroll = QScrollArea()
        strategy_scroll.setWidgetResizable(True)
        strategy_scroll.setFrameShape(QFrame.Shape.NoFrame)
        strategy_scroll.setWidget(self.strategy_analysis_page)

        self.pages.addWidget(strategy_scroll)

        # 7: Mistake Journal
        self.mistake_journal_page = MistakeJournalPage()

        mistake_journal_scroll = QScrollArea()
        mistake_journal_scroll.setWidgetResizable(True)
        mistake_journal_scroll.setFrameShape(QFrame.Shape.NoFrame)
        mistake_journal_scroll.setWidget(self.mistake_journal_page)

        self.pages.addWidget(mistake_journal_scroll)

        # 8: Mistake Analytics — actual page

        self.mistake_analytics_page = MistakeAnalyticsPage()

        self.pages.addWidget(self.mistake_analytics_page)

        # Placeholder pages for features not implemented yet
        self.placeholder_pages = {}

        implemented_pages = {
            "Dashboard",
            "Add Trade",
            "Trade Journal",
            "Trading Calendar",
            "Performance Analytics",
            "Trading Psychology",
            "Strategy Analysis",
            "Mistake Journal",
            "Mistake Analytics",
        }

        for name in navigation_items:
            if name in implemented_pages:
                continue

            placeholder = QWidget()
            placeholder_layout = QVBoxLayout(placeholder)
            placeholder_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            message = QLabel(f"{name} page")
            message.setObjectName("emptyTitle")

            details = QLabel(
                "This feature will be developed in a future step."
            )
            details.setObjectName("description")

            placeholder_layout.addWidget(message)
            placeholder_layout.addWidget(details)

            page_index = self.pages.addWidget(placeholder)
            self.placeholder_pages[name] = page_index

        content_layout.addWidget(self.pages, 1)

        footer = QLabel(
            "TradeWise is a journaling and analytics tool. "
            "It does not guarantee trading profits."
        )
        footer.setObjectName("footer")

        content_layout.addWidget(footer)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content, 1)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #0B1120;
            }

            QWidget#centralWidget {
                background-color: #0B1120;
                color: #E5E7EB;
            }

            QFrame#sidebar {
                background-color: #0F172A;
                border-right: 1px solid #263247;
            }

            QWidget#content {
                background-color: #0B1120;
            }

            QLabel#logo {
                color: #F8FAFC;
                font-size: 27px;
                font-weight: 700;
            }

            QLabel#sidebarSubtitle {
                color: #64748B;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 2px;
            }

            QPushButton#navButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 7px;
                text-align: left;
                padding: 12px 10px;
                font-size: 12px;
            }

            QPushButton#navButton:hover {
                background-color: #1E293B;
                color: #F8FAFC;
            }

            QPushButton#navButton:checked {
                background-color: #173B35;
                color: #4ADE80;
                font-weight: 600;
            }

            QLabel#versionLabel {
                color: #64748B;
                font-size: 11px;
                padding-top: 12px;
            }

            QLabel#pageTitle {
                color: #F8FAFC;
                font-size: 25px;
                font-weight: 700;
            }

            QLabel#statusLabel {
                color: #4ADE80;
                background-color: #132D29;
                border: 1px solid #245044;
                border-radius: 12px;
                padding: 8px 12px;
                font-size: 10px;
                font-weight: 600;
            }

            QFrame#welcomeCard {
                background-color: #111C30;
                border: 1px solid #263247;
                border-radius: 12px;
            }

            QLabel#welcomeTitle {
                color: #F8FAFC;
                font-size: 23px;
                font-weight: 700;
            }

            QLabel#description {
                color: #94A3B8;
                font-size: 12px;
            }

            QLabel#sectionTitle {
                color: #F8FAFC;
                font-size: 17px;
                font-weight: 600;
            }

            QFrame#statCard {
                background-color: #111C30;
                border: 1px solid #263247;
                border-radius: 12px;
            }

            QLabel#statTitle {
                color: #94A3B8;
                font-size: 10px;
                font-weight: 700;
            }

            QLabel#statValue {
                color: #F8FAFC;
                font-size: 22px;
                font-weight: 700;
            }

            QFrame#emptyCard {
                background-color: #0F172A;
                border: 1px solid #263247;
                border-radius: 12px;
            }

            QLabel#emptyTitle {
                color: #E2E8F0;
                font-size: 18px;
                font-weight: 600;
            }

            QLabel#footer {
                color: #64748B;
                font-size: 10px;
            }

            QScrollArea {
                background-color: #0B1120;
                border: none;
            }
        """)

    def refresh_dashboard(self):
        try:
            stats = get_trade_statistics()

            drawdown = get_drawdown_statistics()

            risk = get_risk_management_statistics()

            self.risk_labels["average_risk_reward"].setText(
                f"{risk['average_risk_reward']:.2f} R"
            )

            self.risk_labels["average_risk"].setText(
                f"₹{risk['average_risk']:,.2f}"
            )

            self.risk_labels["largest_winning_trade"].setText(
                f"₹{risk['largest_winning_trade']:,.2f}"
            )

            self.risk_labels["largest_losing_trade"].setText(
                f"₹{risk['largest_losing_trade']:,.2f}"
            )

            self.risk_labels["consecutive_wins"].setText(
                str(risk["consecutive_wins"])
            )

            self.risk_labels["consecutive_losses"].setText(
                str(risk["consecutive_losses"])
            )

            self.drawdown_labels["peak_equity"].setText(
                f"₹{drawdown['peak_equity']:,.2f}"
            )

            self.drawdown_labels["current_drawdown"].setText(
                f"₹{drawdown['current_drawdown']:,.2f}"
            )

            self.drawdown_labels["max_drawdown"].setText(
                f"₹{drawdown['max_drawdown']:,.2f}"
            )

            self.drawdown_labels["max_drawdown_percent"].setText(
                f"{drawdown['max_drawdown_percent']:.2f}%"
            )

            equity_data = get_equity_curve_data()
            self.equity_chart.plot_data(equity_data)
            self.equity_chart.setMinimumHeight(300)
            self.equity_chart.setMaximumHeight(350)

            self.stat_labels["total_trades"].setText(
                str(stats["total_trades"])
            )
            self.stat_labels["net_pnl"].setText(
                f"₹{stats['net_pnl']:,.2f}"
            )
            self.stat_labels["win_rate"].setText(
                f"{stats['win_rate']:.1f}%"
            )
            self.stat_labels["open_trades"].setText(
                str(stats["open_trades"])
            )

            self.activity_description.setText(
                f"Closed trades: {stats['closed_trades']}   |   "
                f"Winning trades: {stats['winning_trades']}   |   "
                f"Losing trades: {stats['losing_trades']}"
            )

        except Exception as error:
            self.activity_description.setText(
                f"Dashboard statistics load nahi ho paayi: {error}"
            )

    def select_page(self, page_name):
        self.page_title.setText(page_name)

        for button in self.nav_buttons:
            button.setChecked(button.text() == page_name)

        if page_name == "Dashboard":
            self.pages.setCurrentIndex(0)
            self.refresh_dashboard()

        elif page_name == "Add Trade":
            self.pages.setCurrentIndex(1)

        elif page_name == "Trade Journal":
            self.pages.setCurrentIndex(2)
            self.trade_journal_page.load_trades()

        elif page_name == "Trading Calendar":
            self.pages.setCurrentIndex(3)
            self.trading_calendar_page.load_trades()

        elif page_name == "Performance Analytics":
            self.pages.setCurrentIndex(4)
            self.performance_analytics_page.load_analytics()

        elif page_name == "Trading Psychology":
            self.pages.setCurrentIndex(5)
            self.trading_psychology_page.load_psychology()

        elif page_name == "Strategy Analysis":
            self.pages.setCurrentIndex(6)
            self.strategy_analysis_page.load_strategy_data()

        elif page_name == "Mistake Journal":
            self.pages.setCurrentIndex(7)

        elif page_name == "Mistake Analytics":
            self.pages.setCurrentIndex(8)
            self.mistake_analytics_page.load_analytics()

        else:
            self.pages.setCurrentIndex(
                self.placeholder_pages[page_name]
            )


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("TradeWise")
    app.setFont(QFont("Segoe UI", 10))

    window = TradeWiseApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

