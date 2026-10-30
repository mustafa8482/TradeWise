import sqlite3
from pathlib import Path
from platformdirs import user_data_dir


APP_NAME = "TradeWise"
APP_AUTHOR = "TradeWise"

# Application data directory
DATA_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))
DATABASE_PATH = DATA_DIR / "tradewise.db"


def get_connection():
    """
    SQLite database connection return karta hai.
    Database folder automatically create ho jayega.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """
    Existing trades table ko safe rakhte hue
    mistakes table bhi create karta hai.
    """

    with get_connection() as connection:

        # Existing trades table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_date TEXT NOT NULL,
                symbol TEXT NOT NULL,

                market_type TEXT NOT NULL
                    CHECK (
                        market_type IN (
                            'Equity',
                            'Futures',
                            'Options',
                            'Crypto'
                        )
                    ),

                direction TEXT NOT NULL
                    CHECK (direction IN ('Long', 'Short')),

                entry_price TEXT NOT NULL,
                exit_price TEXT,
                quantity TEXT NOT NULL,
                multiplier TEXT NOT NULL DEFAULT '1',

                entry_fees TEXT NOT NULL DEFAULT '0',
                exit_fees TEXT NOT NULL DEFAULT '0',
                other_charges TEXT NOT NULL DEFAULT '0',

                stop_loss TEXT,
                target_price TEXT,

                strategy TEXT,
                timeframe TEXT,

                status TEXT NOT NULL DEFAULT 'Open'
                    CHECK (
                        status IN ('Open', 'Closed', 'Cancelled')
                    ),

                notes TEXT,

                followed_plan INTEGER NOT NULL DEFAULT 1
                    CHECK (followed_plan IN (0, 1)),

                emotion_before TEXT,
                emotion_after TEXT,
                lessons_learned TEXT,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # New mistakes table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS mistakes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                mistake_date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                mistake_type TEXT NOT NULL,
                emotion TEXT NOT NULL,

                financial_impact REAL NOT NULL DEFAULT 0,

                what_happened TEXT NOT NULL,
                lesson_learned TEXT NOT NULL,

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


if __name__ == "__main__":
    initialize_database()

    print("TradeWise database initialized successfully.")
    print(f"Database location: {DATABASE_PATH}")
