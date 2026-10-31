# 📊 TradeWise — Professional Trading Journal

### Trade Smarter. Track Better. Improve Consistently.

TradeWise is a professional Windows desktop trading journal built to help traders record their trades, analyze performance, understand trading psychology, evaluate strategies, and identify recurring mistakes.

Developed using **Python, PySide6, SQLite, and Matplotlib**, TradeWise provides a centralized workspace for trade management, performance analytics, risk analysis, and trading behavior tracking.

---

## ✨ Features

### 📈 Trade Management

* Add and record trading activities.
* Track entry price, exit price, quantity, and charges.
* Calculate gross and net profit/loss.
* Maintain detailed trade history.
* Close and review open trades.

### 📊 Performance Analytics

* Total trades, winning trades, and losing trades.
* Win rate and net P&L calculations.
* Performance visualization.
* Equity curve tracking.
* Drawdown analysis.
* Risk management statistics.

### 📅 Trading Calendar

* View trading activity by date.
* Track daily trading performance.
* Review historical trades.

### 🧠 Trading Psychology

* Track emotions during trading.
* Understand emotional trading patterns.
* Review trading discipline.

### 🎯 Strategy Analysis

* Evaluate trading strategies.
* Analyze strategy performance.
* Identify areas for improvement.

### ⚠️ Mistake Journal & Analytics

* Record trading mistakes.
* Track mistake types and emotions.
* Record financial impact.
* Identify recurring mistakes.
* Analyze mistakes through visual insights.

### 📉 Risk Management

* Monitor risk-related statistics.
* Analyze winning and losing streaks.
* Track drawdown.
* Review risk and reward performance.

### 📄 Reports & Export

* Generate PDF reports.
* Export trading records to Excel.
* Review and maintain trading reports.

### ⚙️ Settings & Backup

* View database information.
* Create database backups.
* Restore database backups.
* Validate backup integrity before restoration.

---

## 🛠️ Tech Stack

| Technology     | Purpose                          |
| -------------- | -------------------------------- |
| Python         | Core programming language        |
| PySide6        | Desktop graphical user interface |
| SQLite         | Database management              |
| Matplotlib     | Charts and data visualization    |
| Pandas / NumPy | Data processing and calculations |
| ReportLab      | PDF report generation            |
| OpenPyXL       | Excel export                     |
| PyInstaller    | Windows executable generation    |
| Git & GitHub   | Version control                  |

---

## 📂 Project Structure

```text
TradeWise/
│
├── assets/
├── backups/
├── calculations/
├── config/
├── database/
│   └── connection.py
│
├── exports/
├── imports/
├── models/
│   └── trade.py
│
├── services/
│   └── trade_service.py
│
├── tests/
│
├── ui/
│   └── pages/
│       ├── add_trade_page.py
│       ├── trade_journal_page.py
│       ├── trading_calendar_page.py
│       ├── performance_analytics_page.py
│       ├── trading_psychology_page.py
│       ├── strategy_analysis_page.py
│       ├── mistake_journal_page.py
│       ├── mistake_analytics_page.py
│       ├── reports_page.py
│       └── settings_page.py
│
├── main.py
├── README.md
└── .gitignore
```

---

## 💻 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/mustafa8482/TradeWise.git
```

### 2. Navigate to Project Folder

```bash
cd TradeWise
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate Virtual Environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
python -m pip install PySide6 matplotlib pandas numpy reportlab openpyxl platformdirs
```

Install any additional dependencies required by the project.

### 6. Run the Application

```bash
python main.py
```

---

## 📦 Build Windows EXE

TradeWise supports Windows executable generation using PyInstaller.

### Install PyInstaller

```bash
python -m pip install pyinstaller
```

### Build the Application

```bash
pyinstaller --noconfirm --clean --windowed --name TradeWise main.py
```

After successful compilation, the executable will be available inside:

```text
dist/
└── TradeWise/
    ├── TradeWise.exe
    └── Required application files
```

**Note:** Share the complete `TradeWise` folder rather than copying only the EXE file.

---

## 🚀 Future Improvements

* Interactive equity curve and advanced chart customization.
* More advanced trading performance metrics.
* Detailed risk and reward analysis.
* Improved user interface and experience.
* Additional broker data import integrations.
* Advanced reporting and analytics.

---

## 🎯 Project Goal

The goal of TradeWise is to help traders:

* Maintain structured trading records.
* Understand their trading performance.
* Develop better trading discipline.
* Identify recurring trading mistakes.
* Evaluate strategies using historical data.
* Make more informed trading decisions.

**TradeWise is a trading journal and analytics tool, not a trading signal or guaranteed-profit system.**

---

## 👨‍💻 Developer

**Golam Mostafa Sekh**

* GitHub: https://github.com/mustafa8482
* Project Repository: https://github.com/mustafa8482/TradeWise

---

## 📄 License

This project is currently available for personal and educational development.

A formal open-source license may be added in the future.
