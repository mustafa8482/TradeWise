# 📊 TradeWise — Professional Trading Journal

**Trade Smarter. Track Better. Improve Consistently.**

TradeWise is a professional desktop-based trading journal application designed to help traders record their trades, analyze performance, understand trading psychology, evaluate strategies, and identify recurring mistakes.

Built with Python, PySide6, and SQLite, TradeWise provides an organized workspace with performance analytics and visual insights to help traders make more informed decisions.

---

## ✨ Key Features

### 📈 Trade Management

* Add and record trading activities.
* Track entry price, exit price, quantity, and charges.
* Calculate trade profit and loss.
* Maintain a detailed trade history.

### 📊 Performance Analytics

* Track total trades, winning trades, and losing trades.
* Analyze win rate and profitability.
* Visualize trading performance.
* Monitor equity curve.

### 📅 Trading Calendar

* View trading activity by date.
* Track daily trading performance.
* Review historical trading activity.

### 🧠 Trading Psychology

* Track emotions during trading.
* Understand emotional trading patterns.
* Improve trading discipline.

### 🎯 Strategy Analysis

* Evaluate trading strategies.
* Compare strategy performance.
* Identify strategies that need improvement.

### ⚠️ Mistake Journal

* Record trading mistakes.
* Identify repeated mistakes.
* Review mistakes to improve trading decisions.

### 📉 Risk Management

* Monitor risk-related statistics.
* Track average risk and risk-reward performance.
* Analyze winning and losing streaks.
* Monitor drawdown.

---

## 🛠️ Tech Stack

| Technology   | Purpose                       |
| ------------ | ----------------------------- |
| Python       | Core Programming Language     |
| PySide6      | Desktop Application UI        |
| SQLite       | Database Management           |
| Matplotlib   | Charts and Data Visualization |
| Git & GitHub | Version Control               |

---

## 📂 Project Structure

```text
TradeWise/
│
├── database/
│   └── connection.py
│
├── models/
│   └── trade.py
│
├── services/
│   └── trade_service.py
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
│       └── mistake_analytics_page.py
│
├── main.py
├── README.md
└── .gitignore
```

---

## 💻 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/TradeWise.git
```

### 2. Navigate to Project Folder

```bash
cd TradeWise
```

### 3. Create Virtual Environment

```bash
python -m venv .venv
```

### 4. Activate Virtual Environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
pip install PySide6 matplotlib
```

Install any additional dependencies required by the project.

### 6. Run the Application

```bash
python main.py
```
---

## 🚀 Future Improvements

* Interactive equity curve and advanced performance charts.
* Advanced trading statistics.
* Detailed risk and reward analysis.
* PDF and Excel report generation.
* Trade import and export functionality.
* Automated backup and restore.
* Improved dashboard UI and user experience.

---

## 🎯 Project Goal

The goal of TradeWise is to help traders develop consistency, maintain discipline, understand their trading behavior, and improve their decision-making through structured trade records and performance analysis.

**TradeWise is a trading journal and analytics tool, not a trading signal or guaranteed-profit system.**

---

## 👨‍💻 Developer

**Golam Mostafa Sekh**

* GitHub: https://github.com/mustafa8482

---

## 📄 License

This project is currently available for personal and educational development.

A formal open-source license may be added in the future.
