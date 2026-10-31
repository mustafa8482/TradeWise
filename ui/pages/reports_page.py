from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QComboBox,
    QDateEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
    QFileDialog,
)

from PySide6.QtCore import Qt, QDate

from services.trade_service import get_report_data

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


class ReportsPage(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # PAGE TITLE

        title = QLabel("Trading Reports")
        title.setObjectName("pageTitle")

        description = QLabel(
            "Analyze your trading performance and export reports."
        )
        description.setObjectName("description")

        main_layout.addWidget(title)
        main_layout.addWidget(description)

        # FILTER SECTION

        filter_card = QFrame()
        filter_card.setObjectName("panelCard")

        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(20, 20, 20, 20)
        filter_layout.setSpacing(15)

        self.report_type = QComboBox()
        self.report_type.addItems([
            "All Trades",
            "Performance Report",
            "Monthly Report",
        ])

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(
            QDate.currentDate().addMonths(-1)
        )

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())

        self.generate_button = QPushButton("Generate Report")
        self.generate_button.setObjectName("primaryButton")

        filter_layout.addWidget(QLabel("Report Type"))
        filter_layout.addWidget(self.report_type)

        filter_layout.addWidget(QLabel("From"))
        filter_layout.addWidget(self.start_date)

        filter_layout.addWidget(QLabel("To"))
        filter_layout.addWidget(self.end_date)

        filter_layout.addWidget(self.generate_button)

        self.generate_button.clicked.connect(
            self.generate_report
        )

        main_layout.addWidget(filter_card)

        # SUMMARY SECTION

        summary_layout = QHBoxLayout()

        self.total_trades_card = self.create_card(
            "Total Trades", "0"
        )

        self.total_profit_card = self.create_card(
            "Net Profit/Loss", "₹0.00"
        )

        self.win_rate_card = self.create_card(
            "Win Rate", "0%"
        )

        self.average_pnl_card = self.create_card(
            "Average P&L", "₹0.00"
        )

        summary_layout.addWidget(self.total_trades_card)
        summary_layout.addWidget(self.total_profit_card)
        summary_layout.addWidget(self.win_rate_card)
        summary_layout.addWidget(self.average_pnl_card)

        main_layout.addLayout(summary_layout)

        # TRADE REPORT TABLE

        table_card = QFrame()
        table_card.setObjectName("panelCard")

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_layout.setSpacing(15)

        table_title = QLabel("Report Details")
        table_title.setObjectName("panelTitle")

        self.report_table = QTableWidget()
        self.report_table.setColumnCount(7)

        self.report_table.setHorizontalHeaderLabels([
            "Date",
            "Symbol",
            "Market",
            "Direction",
            "Entry Price",
            "Exit Price",
            "Net P&L",
        ])

        self.report_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.report_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.report_table.verticalHeader().setVisible(False)

        self.report_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        table_layout.addWidget(table_title)
        table_layout.addWidget(self.report_table)

        main_layout.addWidget(table_card)

        # EXPORT BUTTONS

        export_layout = QHBoxLayout()

        self.pdf_button = QPushButton("Export PDF")
        self.pdf_button.setObjectName("primaryButton")

        self.excel_button = QPushButton("Export Excel")
        self.excel_button.setObjectName("primaryButton")

        self.pdf_button.clicked.connect(self.export_pdf)
        self.excel_button.clicked.connect(self.export_excel)

        export_layout.addStretch()
        export_layout.addWidget(self.pdf_button)
        export_layout.addWidget(self.excel_button)

        main_layout.addLayout(export_layout)

        main_layout.addStretch()

    # CREATE SUMMARY CARD

    def create_card(self, title, value):

        card = QFrame()
        card.setObjectName("panelCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)

        title_label = QLabel(title)
        title_label.setObjectName("description")

        value_label = QLabel(value)
        value_label.setObjectName("cardValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        card.value_label = value_label

        return card

    # GENERATE REPORT

    def generate_report(self):

        start_date = self.start_date.date().toString(
            "yyyy-MM-dd"
        )

        end_date = self.end_date.date().toString(
            "yyyy-MM-dd"
        )

        if start_date > end_date:

            QMessageBox.warning(
                self,
                "Invalid Date",
                "Start date cannot be greater than end date."
            )

            return

        report = get_report_data(start_date, end_date)

        # UPDATE SUMMARY CARDS

        self.total_trades_card.value_label.setText(
            str(report["total_trades"])
        )

        self.total_profit_card.value_label.setText(
            f'₹{report["net_pnl"]:,.2f}'
        )

        self.win_rate_card.value_label.setText(
            f'{report["win_rate"]:.2f}%'
        )

        self.average_pnl_card.value_label.setText(
            f'₹{report["average_pnl"]:,.2f}'
        )

        # UPDATE REPORT TABLE

        trades = report["trades"]

        self.report_table.setRowCount(len(trades))

        for row, trade in enumerate(trades):

            entry = float(
                trade.get("entry_price") or 0
            )

            exit_price = trade.get("exit_price")

            if exit_price not in (None, ""):
                exit_price = float(exit_price)
            else:
                exit_price = None

            pnl = "—"
            net_pnl = 0

            if (
                trade.get("status") == "Closed"
                and exit_price is not None
            ):

                quantity = float(
                    trade.get("quantity") or 0
                )

                multiplier = float(
                    trade.get("multiplier") or 1
                )

                if trade["direction"] == "Short":

                    gross_pnl = (
                        (entry - exit_price)
                        * quantity
                        * multiplier
                    )

                else:

                    gross_pnl = (
                        (exit_price - entry)
                        * quantity
                        * multiplier
                    )

                charges = (
                    float(trade.get("entry_fees") or 0)
                    + float(trade.get("exit_fees") or 0)
                    + float(trade.get("other_charges") or 0)
                )

                net_pnl = gross_pnl - charges

                pnl = f"₹{net_pnl:,.2f}"

            values = [
                str(trade.get("trade_date", "")),
                str(trade.get("symbol", "")),
                str(trade.get("market_type", "")),
                str(trade.get("direction", "")),
                f"₹{entry:,.2f}",
                (
                    f"₹{exit_price:,.2f}"
                    if exit_price is not None
                    else "—"
                ),
                pnl,
            ]

            for column, value in enumerate(values):

                item = QTableWidgetItem(value)

                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignCenter
                )

                # PROFIT / LOSS COLOR

                if column == 6 and pnl != "—":

                    if net_pnl > 0:

                        item.setForeground(
                            Qt.GlobalColor.green
                        )

                    elif net_pnl < 0:

                        item.setForeground(
                            Qt.GlobalColor.red
                        )

                self.report_table.setItem(
                    row,
                    column,
                    item
                )

    # EXPORT PDF

    def export_pdf(self):

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Trading Report",
            "TradeWise_Report.pdf",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".pdf"):
            file_path += ".pdf"

        start_date = self.start_date.date().toString(
            "yyyy-MM-dd"
        )

        end_date = self.end_date.date().toString(
            "yyyy-MM-dd"
        )

        if start_date > end_date:

            QMessageBox.warning(
                self,
                "Invalid Date",
                "Start date cannot be greater than end date."
            )

            return

        report = get_report_data(start_date, end_date)

        doc = SimpleDocTemplate(
            file_path,
            pagesize=landscape(A4)
        )

        elements = []

        styles = getSampleStyleSheet()

        # TITLE

        elements.append(
            Paragraph(
                "TradeWise - Trading Report",
                styles["Title"]
            )
        )

        elements.append(Spacer(1, 15))

        elements.append(
            Paragraph(
                f"Report Period: {start_date} to {end_date}",
                styles["Normal"]
            )
        )

        elements.append(Spacer(1, 20))

        # SUMMARY

        summary_data = [
            [
                "Total Trades",
                "Net P&L",
                "Win Rate",
                "Average P&L"
            ],
            [
                str(report["total_trades"]),
                f'Rs. {report["net_pnl"]:,.2f}',
                f'{report["win_rate"]:.2f}%',
                f'Rs. {report["average_pnl"]:,.2f}',
            ]
        ]

        summary_table = Table(summary_data)

        summary_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#0F172A")
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("PADDING", (0, 0), (-1, -1), 10),
            ])
        )

        elements.append(summary_table)

        elements.append(Spacer(1, 25))

        # TRADE TABLE

        table_data = [
            [
                "Date",
                "Symbol",
                "Market",
                "Direction",
                "Entry",
                "Exit",
                "Net P&L"
            ]
        ]

        for trade in report["trades"]:

            entry = float(
                trade.get("entry_price") or 0
            )

            exit_price = trade.get("exit_price")

            pnl = "—"

            if (
                trade.get("status") == "Closed"
                and exit_price is not None
            ):

                exit_price = float(exit_price)

                quantity = float(
                    trade.get("quantity") or 0
                )

                multiplier = float(
                    trade.get("multiplier") or 1
                )

                if trade["direction"] == "Short":

                    gross_pnl = (
                        (entry - exit_price)
                        * quantity
                        * multiplier
                    )

                else:

                    gross_pnl = (
                        (exit_price - entry)
                        * quantity
                        * multiplier
                    )

                charges = (
                    float(trade.get("entry_fees") or 0)
                    + float(trade.get("exit_fees") or 0)
                    + float(trade.get("other_charges") or 0)
                )

                net_pnl = gross_pnl - charges

                pnl = f"Rs. {net_pnl:,.2f}"

            table_data.append([
                str(trade.get("trade_date", "")),
                str(trade.get("symbol", "")),
                str(trade.get("market_type", "")),
                str(trade.get("direction", "")),
                f"Rs. {entry:,.2f}",
                (
                    f"Rs. {float(exit_price):,.2f}"
                    if exit_price is not None
                    else "—"
                ),
                pnl
            ])

        trade_table = Table(
            table_data,
            repeatRows=1
        )

        trade_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#0F172A")
                ),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("PADDING", (0, 0), (-1, -1), 7),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ])
        )

        elements.append(trade_table)

        # CREATE PDF

        try:

            doc.build(elements)

            QMessageBox.information(
                self,
                "PDF Exported",
                "Trading report PDF successfully saved!"
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "PDF Export Error",
                f"Could not export PDF:\n{error}"
            )

        # EXPORT EXCEL

    def export_excel(self):

        start_date = self.start_date.date().toString("yyyy-MM-dd")
        end_date = self.end_date.date().toString("yyyy-MM-dd")

        if start_date > end_date:
            QMessageBox.warning(
                self,
                "Invalid Date",
                "Start date cannot be greater than end date."
            )
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Trading Report",
            "TradeWise_Report.xlsx",
            "Excel Files (*.xlsx)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".xlsx"):
            file_path += ".xlsx"

        try:

            report = get_report_data(start_date, end_date)

            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Trading Report"

            # TITLE
            sheet.merge_cells("A1:G1")
            sheet["A1"] = "TradeWise - Trading Report"
            sheet["A1"].font = Font(
                size=16, bold=True, color="FFFFFF"
            )
            sheet["A1"].fill = PatternFill(
                "solid", fgColor="0F172A"
            )
            sheet["A1"].alignment = Alignment(
                horizontal="center"
            )

            sheet.merge_cells("A2:G2")
            sheet["A2"] = f"Report Period: {start_date} to {end_date}"

            # SUMMARY
            summary_headers = [
                "Total Trades",
                "Closed Trades",
                "Net P&L",
                "Win Rate",
                "Average P&L"
            ]

            summary_values = [
                report["total_trades"],
                report["closed_trades"],
                report["net_pnl"],
                report["win_rate"] / 100,
                report["average_pnl"]
            ]

            for col, value in enumerate(summary_headers, 1):
                cell = sheet.cell(row=4, column=col, value=value)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(
                    "solid", fgColor="334155"
                )

            for col, value in enumerate(summary_values, 1):
                sheet.cell(row=5, column=col, value=value)

            sheet["C5"].number_format = '₹#,##0.00'
            sheet["D5"].number_format = "0.00%"
            sheet["E5"].number_format = '₹#,##0.00'

            # TRADE DETAILS
            headers = [
                "Date",
                "Symbol",
                "Market",
                "Direction",
                "Entry Price",
                "Exit Price",
                "Net P&L"
            ]

            header_row = 8

            for col, heading in enumerate(headers, 1):
                cell = sheet.cell(
                    row=header_row,
                    column=col,
                    value=heading
                )
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(
                    "solid", fgColor="0F172A"
                )

            for row, trade in enumerate(
                report["trades"],
                start=header_row + 1
            ):

                entry = float(trade.get("entry_price") or 0)

                exit_value = trade.get("exit_price")

                exit_price = (
                    float(exit_value)
                    if exit_value not in (None, "")
                    else None
                )

                pnl = None

                if (
                    trade.get("status") == "Closed"
                    and exit_price is not None
                ):

                    quantity = float(trade.get("quantity") or 0)
                    multiplier = float(trade.get("multiplier") or 1)

                    if trade["direction"] == "Short":
                        gross_pnl = (
                            entry - exit_price
                        ) * quantity * multiplier
                    else:
                        gross_pnl = (
                            exit_price - entry
                        ) * quantity * multiplier

                    charges = (
                        float(trade.get("entry_fees") or 0)
                        + float(trade.get("exit_fees") or 0)
                        + float(trade.get("other_charges") or 0)
                    )

                    pnl = round(gross_pnl - charges, 2)

                values = [
                    trade.get("trade_date", ""),
                    trade.get("symbol", ""),
                    trade.get("market_type", ""),
                    trade.get("direction", ""),
                    entry,
                    exit_price,
                    pnl
                ]

                for col, value in enumerate(values, 1):

                    cell = sheet.cell(
                        row=row,
                        column=col,
                        value=value
                    )

                    cell.alignment = Alignment(
                        horizontal="center"
                    )

                    if col in (5, 6, 7) and value is not None:
                        cell.number_format = '₹#,##0.00'

                    if col == 7 and pnl is not None:

                        if pnl > 0:
                            cell.font = Font(
                                color="008000",
                                bold=True
                            )

                        elif pnl < 0:
                            cell.font = Font(
                                color="FF0000",
                                bold=True
                            )

            # COLUMN WIDTH
            widths = [16, 18, 16, 14, 18, 18, 18]

            for col, width in enumerate(widths, 1):
                sheet.column_dimensions[
                    get_column_letter(col)
                ].width = width

            sheet.freeze_panes = "A9"

            sheet.auto_filter.ref = (
                f"A8:G{max(8, sheet.max_row)}"
            )

            workbook.save(file_path)

            QMessageBox.information(
                self,
                "Excel Exported",
                "Trading report Excel file successfully saved!"
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Excel Export Error",
                f"Could not export Excel:\n{error}"
            )