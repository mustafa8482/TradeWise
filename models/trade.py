from dataclasses import dataclass
from typing import Optional


@dataclass
class Trade:
    """TradeWise ke ek trade ka data model."""

    trade_date: str
    symbol: str
    market_type: str
    direction: str
    entry_price: float
    quantity: float

    exit_price: Optional[float] = None
    multiplier: float = 1.0

    entry_fees: float = 0.0
    exit_fees: float = 0.0
    other_charges: float = 0.0

    stop_loss: Optional[float] = None
    target_price: Optional[float] = None

    strategy: Optional[str] = None
    timeframe: Optional[str] = None

    status: str = "Open"
    notes: Optional[str] = None

    followed_plan: bool = True

    emotion_before: Optional[str] = None
    emotion_after: Optional[str] = None

    lessons_learned: Optional[str] = None

    def calculate_gross_pnl(self) -> float:
        """Trade ka gross profit/loss calculate karta hai."""

        if self.exit_price is None:
            return 0.0

        price_difference = self.exit_price - self.entry_price

        if self.direction == "Short":
            price_difference = -price_difference

        return price_difference * self.quantity * self.multiplier

    def calculate_net_pnl(self) -> float:
        """Charges minus karke net profit/loss calculate karta hai."""

        total_charges = (
            self.entry_fees
            + self.exit_fees
            + self.other_charges
        )

        return self.calculate_gross_pnl() - total_charges

