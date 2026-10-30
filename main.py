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
    QGridLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from services.trade_service import (
    get_trade_statistics,
    get_equity_curve_data,
    get_drawdown_statistics,
    get_risk_management_statistics,
)

from ui.pages.add_trade_page import AddTradePage
from ui.pages.trade_journal_page import TradeJournalPage
from ui.pages.trading_calendar_page import TradingCalendarPage
from ui.pages.performance_analytics_page import PerformanceAnalyticsPage
from ui.pages.trading_psychology_page import TradingPsychologyPage
from ui.pages.strategy_analysis_page import StrategyAnalysisPage
from ui.pages.mistake_journal_page import MistakeJournalPage
from ui.pages.mistake_analytics_page import MistakeAnalyticsPage
from ui.pages.reports_page import ReportsPage
from services.trade_service import (
    get_trade_statistics,
    get_equity_curve_data,
    get_drawdown_statistics,
    get_risk_management_statistics,
    get_all_trades,
)


# =========================================================
# EQUITY CURVE CHART
# =========================================================

class EquityCurveChart(FigureCanvasQTAgg):

    def __init__(self, parent=None):
        self.figure = Figure(
            figsize=(10, 4),
            facecolor="#111827"
        )

        self.axes = self.figure.add_subplot(111)

        super().__init__(self.figure)
        self.setParent(parent)

        self.setMinimumHeight(340)

        self.figure.subplots_adjust(
            left=0.09,
            right=0.98,
            top=0.88,
            bottom=0.20
        )

    def plot_data(self, data):

        self.axes.clear()
        self.axes.set_facecolor("#111827")

        if not data:

            self.axes.text(
                0.5,
                0.5,
                "No closed trades available",
                color="#94A3B8",
                ha="center",
                va="center",
                transform=self.axes.transAxes,
                fontsize=12
            )

        else:

            dates = [item["date"] for item in data]
            equity = [item["equity"] for item in data]

            positive = equity[-1] >= 0

            line_color = "#22C55E" if positive else "#EF4444"

            x_values = range(len(equity))

            self.axes.plot(
                x_values,
                equity,
                color=line_color,
                linewidth=2.5,
                marker="o",
                markersize=4
            )

            self.axes.fill_between(
                x_values,
                equity,
                0,
                color=line_color,
                alpha=0.10
            )

            self.axes.axhline(
                0,
                color="#475569",
                linewidth=0.8,
                linestyle="--"
            )

            self.axes.set_xticks(list(x_values))

            self.axes.set_xticklabels(
                dates,
                rotation=30,
                ha="right",
                fontsize=8,
                color="#94A3B8"
            )

        self.axes.set_title(
            "Cumulative Net P&L",
            color="#F8FAFC",
            fontsize=14,
            fontweight="bold",
            loc="left",
            pad=15
        )

        self.axes.set_ylabel(
            "Equity (₹)",
            color="#94A3B8"
        )

        self.axes.tick_params(
            axis="y",
            colors="#94A3B8"
        )

        self.axes.tick_params(
            axis="x",
            colors="#94A3B8"
        )

        for spine in self.axes.spines.values():
            spine.set_color("#263449")

        self.axes.grid(
            True,
            color="#334155",
            alpha=0.35,
            linestyle="--"
        )

        self.draw()


# =========================================================
# TRADEWISE MAIN APPLICATION
# =========================================================

class TradeWiseApp(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle("TradeWise | Professional Trading Journal")

        self.resize(1450, 900)
        self.setMinimumSize(1100, 700)

        self.stat_labels = {}
        self.drawdown_labels = {}
        self.risk_labels = {}
        self.nav_buttons = {}
        self.placeholder_pages = {}

        self.setup_ui()
        self.refresh_dashboard()

    # =====================================================
    # UI SETUP
    # =====================================================

    def setup_ui(self):

        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")

        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # SIDEBAR

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(245)

        sidebar_layout = QVBoxLayout(sidebar)

        sidebar_layout.setContentsMargins(
            18, 28, 18, 20
        )

        sidebar_layout.setSpacing(8)

        logo = QLabel("TradeWise")
        logo.setObjectName("logo")

        subtitle = QLabel("PROFESSIONAL TRADING JOURNAL")
        subtitle.setObjectName("sidebarSubtitle")

        sidebar_layout.addWidget(logo)
        sidebar_layout.addWidget(subtitle)

        sidebar_layout.addSpacing(30)

        navigation_items = [
            "Dashboard",
            "Add Trade",
            "Trade Journal",
            "Trading Calendar",
            "Performance Analytics",
            "Trading Psychology",
            "Strategy Analysis",
            "Mistake Journal",
            "Mistake Analytics",
            "Reports & Export",
            "Settings & Backup",
        ]

        for item in navigation_items:

            button = QPushButton(item)

            button.setObjectName("navButton")
            button.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            button.setCheckable(True)

            button.clicked.connect(
                lambda checked=False, name=item:
                self.select_page(name)
            )

            sidebar_layout.addWidget(button)

            self.nav_buttons[item] = button

        self.nav_buttons["Dashboard"].setChecked(True)

        sidebar_layout.addStretch()

        version = QLabel("TRADEWISE  •  VERSION 0.2")
        version.setObjectName("versionLabel")

        sidebar_layout.addWidget(version)

        # MAIN CONTENT

        content = QWidget()
        content.setObjectName("content")

        content_layout = QVBoxLayout(content)

        content_layout.setContentsMargins(
            30, 25, 30, 20
        )

        content_layout.setSpacing(20)

        # HEADER

        toolbar = QHBoxLayout()

        self.page_title = QLabel("Dashboard")
        self.page_title.setObjectName("pageTitle")

        status = QLabel("● DATABASE CONNECTED")
        status.setObjectName("statusLabel")

        toolbar.addWidget(self.page_title)
        toolbar.addStretch()
        toolbar.addWidget(status)

        content_layout.addLayout(toolbar)

        # STACKED WIDGET

        self.pages = QStackedWidget()

        # DASHBOARD PAGE

        dashboard_page = QWidget()

        dashboard_layout = QVBoxLayout(dashboard_page)

        dashboard_layout.setContentsMargins(0, 0, 0, 0)
        dashboard_layout.setSpacing(22)

        # SCROLL AREA
        # Dashboard is added only once to QStackedWidget.

        dashboard_scroll = QScrollArea()

        dashboard_scroll.setWidgetResizable(True)
        dashboard_scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        dashboard_scroll.setWidget(dashboard_page)

        self.pages.addWidget(dashboard_scroll)

        # WELCOME SECTION

        welcome_card = QFrame()
        welcome_card.setObjectName("welcomeCard")

        welcome_layout = QVBoxLayout(welcome_card)

        welcome_layout.setContentsMargins(
            25, 25, 25, 25
        )

        welcome_layout.setSpacing(10)

        welcome_title = QLabel("Welcome to TradeWise 👋")
        welcome_title.setObjectName("welcomeTitle")

        welcome_description = QLabel(
            "Track your trades. Analyze your performance. "
            "Improve your trading discipline."
        )

        welcome_description.setObjectName("description")

        welcome_layout.addWidget(welcome_title)
        welcome_layout.addWidget(welcome_description)

        dashboard_layout.addWidget(welcome_card)

        # PERFORMANCE OVERVIEW

        stats_heading = QLabel("Performance Overview")
        stats_heading.setObjectName("sectionTitle")

        dashboard_layout.addWidget(stats_heading)

        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)

        stats_config = [
            ("total_trades", "TOTAL TRADES", "0"),
            ("net_pnl", "NET P&L", "₹0.00"),
            ("win_rate", "WIN RATE", "0.0%"),
            ("open_trades", "OPEN TRADES", "0"),
        ]

        for index, (key, title, initial) in enumerate(stats_config):

            card = self.create_stat_card(
                title,
                initial
            )

            self.stat_labels[key] = card.findChild(
                QLabel,
                "statValue"
            )

            stats_grid.addWidget(
                card,
                0,
                index
            )

        dashboard_layout.addLayout(stats_grid)

        # EQUITY CURVE

        equity_card = QFrame()
        equity_card.setObjectName("panelCard")

        equity_layout = QVBoxLayout(equity_card)

        equity_layout.setContentsMargins(
            22, 20, 22, 20
        )

        equity_layout.setSpacing(12)

        equity_title = QLabel("Equity Curve")
        equity_title.setObjectName("panelTitle")

        equity_description = QLabel(
            "Visual representation of your cumulative trading P&L."
        )

        equity_description.setObjectName("description")

        self.equity_chart = EquityCurveChart()

        equity_layout.addWidget(equity_title)
        equity_layout.addWidget(equity_description)
        equity_layout.addWidget(self.equity_chart)

        dashboard_layout.addWidget(equity_card)

        # DRAWDOWN ANALYTICS

        drawdown_heading = QLabel("Drawdown Analytics")
        drawdown_heading.setObjectName("sectionTitle")

        dashboard_layout.addWidget(drawdown_heading)

        drawdown_grid = QGridLayout()
        drawdown_grid.setSpacing(15)

        drawdown_config = [
            ("peak_equity", "PEAK EQUITY", "₹0.00"),
            ("current_drawdown", "CURRENT DRAWDOWN", "₹0.00"),
            ("max_drawdown", "MAX DRAWDOWN", "₹0.00"),
            ("max_drawdown_percent", "MAX DRAWDOWN %", "0.00%"),
        ]

        for index, (key, title, initial) in enumerate(drawdown_config):

            card = self.create_stat_card(
                title,
                initial
            )

            self.drawdown_labels[key] = card.findChild(
                QLabel,
                "statValue"
            )

            drawdown_grid.addWidget(
                card,
                0,
                index
            )

        dashboard_layout.addLayout(drawdown_grid)

        # RISK MANAGEMENT

        risk_heading = QLabel("Risk Management")
        risk_heading.setObjectName("sectionTitle")

        dashboard_layout.addWidget(risk_heading)

        risk_grid = QGridLayout()
        risk_grid.setSpacing(15)

        risk_config = [
            ("average_risk_reward", "AVERAGE RISK / REWARD", "0.00 R"),
            ("average_risk", "AVERAGE RISK", "₹0.00"),
            ("largest_winning_trade", "LARGEST WIN", "₹0.00"),
            ("largest_losing_trade", "LARGEST LOSS", "₹0.00"),
            ("consecutive_wins", "CONSECUTIVE WINS", "0"),
            ("consecutive_losses", "CONSECUTIVE LOSSES", "0"),
        ]

        for index, (key, title, initial) in enumerate(risk_config):

            card = self.create_stat_card(
                title,
                initial
            )

            self.risk_labels[key] = card.findChild(
                QLabel,
                "statValue"
            )

            risk_grid.addWidget(
                card,
                index // 3,
                index % 3
            )

        dashboard_layout.addLayout(risk_grid)

        # TRADING ACTIVITY

        activity_card = QFrame()
        activity_card.setObjectName("panelCard")

        activity_layout = QVBoxLayout(activity_card)

        activity_layout.setContentsMargins(
            22, 20, 22, 20
        )

        activity_title = QLabel("Trading Activity")
        activity_title.setObjectName("panelTitle")

        self.activity_description = QLabel(
            "Your recorded trades will appear here."
        )

        self.activity_description.setObjectName("description")
        self.activity_description.setWordWrap(True)

        activity_layout.addWidget(activity_title)
        activity_layout.addWidget(
            self.activity_description
        )

        dashboard_layout.addWidget(activity_card)

        # RECENT TRADES TABLE

        recent_card = QFrame()
        recent_card.setObjectName("panelCard")

        recent_layout = QVBoxLayout(recent_card)

        recent_layout.setContentsMargins(22, 20, 22, 20)
        recent_layout.setSpacing(14)

        recent_title = QLabel("Recent Trades")
        recent_title.setObjectName("panelTitle")

        recent_description = QLabel(
            "Your latest 10 recorded trades."
        )
        recent_description.setObjectName("description")

        self.recent_trades_table = QTableWidget()
        self.recent_trades_table.setColumnCount(8)

        self.recent_trades_table.setHorizontalHeaderLabels([
            "Date",
            "Symbol",
            "Market",
            "Direction",
            "Entry Price",
            "Exit Price",
            "Net P&L",
            "Status",
        ])

        self.recent_trades_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.recent_trades_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.recent_trades_table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.recent_trades_table.setAlternatingRowColors(True)
        self.recent_trades_table.verticalHeader().setVisible(False)

        self.recent_trades_table.setMinimumHeight(300)

        header = self.recent_trades_table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        recent_layout.addWidget(recent_title)
        recent_layout.addWidget(recent_description)
        recent_layout.addWidget(self.recent_trades_table)

        dashboard_layout.addWidget(recent_card)

        # ADD TRADE PAGE

        self.add_trade_page = AddTradePage()

        self.add_trade_page.trade_saved.connect(
            self.refresh_dashboard
        )

        self.add_page_with_scroll(self.add_trade_page)

        # TRADE JOURNAL

        self.trade_journal_page = TradeJournalPage()

        self.add_page_with_scroll(
            self.trade_journal_page
        )

        # TRADING CALENDAR

        self.trading_calendar_page = TradingCalendarPage()

        self.add_page_with_scroll(
            self.trading_calendar_page
        )

        # PERFORMANCE ANALYTICS

        self.performance_analytics_page = PerformanceAnalyticsPage()

        self.add_page_with_scroll(
            self.performance_analytics_page
        )

        # TRADING PSYCHOLOGY

        self.trading_psychology_page = TradingPsychologyPage()

        self.add_page_with_scroll(
            self.trading_psychology_page
        )

        # STRATEGY ANALYSIS

        self.strategy_analysis_page = StrategyAnalysisPage()

        self.add_page_with_scroll(
            self.strategy_analysis_page
        )

        # MISTAKE JOURNAL

        self.mistake_journal_page = MistakeJournalPage()

        self.add_page_with_scroll(
            self.mistake_journal_page
        )

        # MISTAKE ANALYTICS

        self.mistake_analytics_page = MistakeAnalyticsPage()

        self.add_page_with_scroll(
            self.mistake_analytics_page
        )

        # REPORTS & EXPORT

        self.reports_page = ReportsPage()

        self.reports_page_index = self.add_page_with_scroll(
            self.reports_page
        )

        # PLACEHOLDER PAGES

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
            "Reports & Export",
        }

        for name in navigation_items:

            if name in implemented_pages:
                continue

            placeholder = QWidget()

            placeholder_layout = QVBoxLayout(placeholder)

            placeholder_layout.setAlignment(
                Qt.AlignmentFlag.AlignCenter
            )

            message = QLabel(f"{name} page")
            message.setObjectName("panelTitle")

            details = QLabel(
                "This feature will be developed in a future update."
            )

            details.setObjectName("description")

            placeholder_layout.addWidget(message)
            placeholder_layout.addWidget(details)

            self.placeholder_pages[name] = (
                self.pages.addWidget(placeholder)
            )

        content_layout.addWidget(self.pages, 1)

        # FOOTER

        footer = QLabel(
            "TradeWise is a trading journal and analytics tool. "
            "It does not guarantee trading profits."
        )

        footer.setObjectName("footer")

        content_layout.addWidget(footer)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content, 1)

        # GLOBAL STYLESHEET

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
                border-right: 1px solid #263449;
            }

            QWidget#content {
                background-color: #0B1120;
            }

            QLabel#logo {
                color: #F8FAFC;
                font-size: 29px;
                font-weight: 800;
            }

            QLabel#sidebarSubtitle {
                color: #64748B;
                font-size: 9px;
                font-weight: 700;
            }

            QPushButton#navButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 8px;
                text-align: left;
                padding: 13px 12px;
                font-size: 12px;
            }

            QPushButton#navButton:hover {
                background-color: #1E293B;
                color: #F8FAFC;
            }

            QPushButton#navButton:checked {
                background-color: #173B35;
                color: #4ADE80;
                font-weight: 700;
                border-left: 3px solid #22C55E;
            }

            QLabel#versionLabel {
                color: #64748B;
                font-size: 10px;
                padding-top: 15px;
            }

            QLabel#pageTitle {
                color: #F8FAFC;
                font-size: 27px;
                font-weight: 800;
            }

            QLabel#statusLabel {
                color: #4ADE80;
                background-color: #132D29;
                border: 1px solid #245044;
                border-radius: 12px;
                padding: 9px 14px;
                font-size: 10px;
                font-weight: 700;
            }

            QFrame#welcomeCard {
                background-color: #111C30;
                border: 1px solid #263449;
                border-radius: 14px;
            }

            QLabel#welcomeTitle {
                color: #F8FAFC;
                font-size: 25px;
                font-weight: 800;
            }

            QLabel#description {
                color: #94A3B8;
                font-size: 12px;
            }

            QLabel#sectionTitle {
                color: #F8FAFC;
                font-size: 18px;
                font-weight: 700;
            }

            QFrame#statCard {
                background-color: #111C30;
                border: 1px solid #263449;
                border-radius: 13px;
            }

            QLabel#statTitle {
                color: #94A3B8;
                font-size: 10px;
                font-weight: 700;
            }

            QLabel#statValue {
                color: #F8FAFC;
                font-size: 23px;
                font-weight: 800;
            }

            QFrame#panelCard {
                background-color: #111827;
                border: 1px solid #263449;
                border-radius: 14px;
            }

            QLabel#panelTitle {
                color: #F8FAFC;
                font-size: 17px;
                font-weight: 700;
            }

            QLabel#footer {
                color: #64748B;
                font-size: 10px;
            }

            QScrollArea {
                background-color: #0B1120;
                border: none;
            }

            QScrollArea QWidget {
                background-color: transparent;
            }

            QScrollBar:vertical {
                background: #0F172A;
                width: 9px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #334155;
                border-radius: 4px;
                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {
                background: #475569;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }

        """)

    # =====================================================
    # REUSABLE STAT CARD
    # =====================================================

    def create_stat_card(self, title, value):

        card = QFrame()
        card.setObjectName("statCard")

        card.setMinimumHeight(105)

        layout = QVBoxLayout(card)

        layout.setContentsMargins(
            17, 17, 17, 17
        )

        layout.setSpacing(12)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        title_label.setWordWrap(True)

        value_label = QLabel(value)
        value_label.setObjectName("statValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return card

    # =====================================================
    # ADD SCROLLABLE PAGE
    # =====================================================

    def add_page_with_scroll(self, page):

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        scroll.setFrameShape(
            QFrame.Shape.NoFrame
        )

        scroll.setWidget(page)

        page_index = self.pages.addWidget(scroll)

        return page_index

    # =====================================================
    # LOAD RECENT TRADES
    # =====================================================

    def load_recent_trades(self):

        trades = get_all_trades()

        recent_trades = trades[:10]

        self.recent_trades_table.setRowCount(
            len(recent_trades)
        )

        for row, trade in enumerate(recent_trades):

            entry_price = float(
                trade.get("entry_price") or 0
            )

            exit_value = trade.get("exit_price")

            if (
                trade.get("status") == "Closed"
                and exit_value not in (None, "")
            ):

                exit_price = float(exit_value)

                quantity = float(
                    trade.get("quantity") or 0
                )

                multiplier = float(
                    trade.get("multiplier") or 1
                )

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
                net_pnl = None
                pnl_text = "—"

            values = [
                str(trade.get("trade_date", "")),
                str(trade.get("symbol", "")),
                str(trade.get("market_type", "")),
                str(trade.get("direction", "")),
                f"₹{entry_price:,.2f}",
                (
                    f"₹{exit_price:,.2f}"
                    if exit_price is not None
                    else "—"
                ),
                pnl_text,
                str(trade.get("status", "")),
            ]

            for column, value in enumerate(values):

                item = QTableWidgetItem(value)

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                if column == 6 and net_pnl is not None:

                    if net_pnl > 0:
                        item.setForeground(Qt.GlobalColor.green)

                    elif net_pnl < 0:
                        item.setForeground(Qt.GlobalColor.red)

                if column == 7:

                    if trade.get("status") == "Open":
                        item.setForeground(Qt.GlobalColor.yellow)

                    elif trade.get("status") == "Closed":
                        item.setForeground(Qt.GlobalColor.green)

                self.recent_trades_table.setItem(
                    row,
                    column,
                    item
                )

    # =====================================================
    # REFRESH DASHBOARD
    # =====================================================

    def refresh_dashboard(self):

        try:

            stats = get_trade_statistics()

            drawdown = get_drawdown_statistics()

            risk = get_risk_management_statistics()

            # PERFORMANCE

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

            # P&L COLOR

            pnl_color = (
                "#22C55E"
                if stats["net_pnl"] >= 0
                else "#EF4444"
            )

            self.stat_labels["net_pnl"].setStyleSheet(
                f"color: {pnl_color};"
            )

            # DRAWDOWN

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

            # RISK MANAGEMENT

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

            # EQUITY CURVE

            equity_data = get_equity_curve_data()

            self.equity_chart.plot_data(
                equity_data
            )

             # RECENT TRADES

            self.load_recent_trades()

            # ACTIVITY

            self.activity_description.setText(
                f"Closed Trades: {stats['closed_trades']}     |     "
                f"Winning Trades: {stats['winning_trades']}     |     "
                f"Losing Trades: {stats['losing_trades']}"
            )

        except Exception as error:

            self.activity_description.setText(
                f"Dashboard statistics load nahi ho paayi: {error}"
            )

    # =====================================================
    # PAGE NAVIGATION
    # =====================================================

    def select_page(self, page_name):

        self.page_title.setText(page_name)

        for name, button in self.nav_buttons.items():

            button.setChecked(
                name == page_name
            )

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

        elif page_name == "Reports & Export":

            self.pages.setCurrentIndex(
                self.reports_page_index
            )

            self.reports_page.generate_report()

        else:

            self.pages.setCurrentIndex(
                self.placeholder_pages[page_name]
            )


# =========================================================
# APPLICATION ENTRY POINT
# =========================================================

def main():

    app = QApplication(sys.argv)

    app.setApplicationName("TradeWise")

    app.setFont(
        QFont("Segoe UI", 10)
    )

    window = TradeWiseApp()

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":

    main()