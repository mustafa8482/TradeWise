from database.connection import get_connection
from models.trade import Trade


def add_trade(trade: Trade) -> int:
    """Database mein naya trade save karta hai aur uski ID return karta hai."""

    query = """
        INSERT INTO trades (
            trade_date,
            symbol,
            market_type,
            direction,
            entry_price,
            exit_price,
            quantity,
            multiplier,
            entry_fees,
            exit_fees,
            other_charges,
            stop_loss,
            target_price,
            strategy,
            timeframe,
            status,
            notes,
            followed_plan,
            emotion_before,
            emotion_after,
            lessons_learned
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """

    values = (
        trade.trade_date,
        trade.symbol,
        trade.market_type,
        trade.direction,
        str(trade.entry_price),
        str(trade.exit_price) if trade.exit_price is not None else None,
        str(trade.quantity),
        str(trade.multiplier),
        str(trade.entry_fees),
        str(trade.exit_fees),
        str(trade.other_charges),
        str(trade.stop_loss) if trade.stop_loss is not None else None,
        str(trade.target_price) if trade.target_price is not None else None,
        trade.strategy,
        trade.timeframe,
        trade.status,
        trade.notes,
        int(trade.followed_plan),
        trade.emotion_before,
        trade.emotion_after,
        trade.lessons_learned,
    )

    with get_connection() as connection:
        cursor = connection.execute(query, values)
        return cursor.lastrowid


def get_all_trades() -> list[dict]:
    """Database ke saare trades return karta hai."""

    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM trades ORDER BY trade_date DESC, id DESC"
        ).fetchall()

        return [dict(row) for row in rows]


def get_trade_by_id(trade_id: int) -> dict | None:
    """ID se ek specific trade find karta hai."""

    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM trades WHERE id = ?",
            (trade_id,),
        ).fetchone()

        return dict(row) if row else None


def delete_trade(trade_id: int) -> bool:
    """ID ke basis par trade delete karta hai."""

    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM trades WHERE id = ?",
            (trade_id,),
        )

        return cursor.rowcount > 0

def get_trade_statistics() -> dict:
    """Database se dashboard ke liye trading statistics calculate karta hai."""

    trades = get_all_trades()

    total_trades = len(trades)
    closed_trades = [trade for trade in trades if trade["status"] == "Closed"]
    open_trades = [trade for trade in trades if trade["status"] == "Open"]

    net_pnl = 0.0
    winning_trades = 0
    losing_trades = 0

    for trade in closed_trades:
        entry_price = float(trade["entry_price"])
        exit_price = float(trade["exit_price"] or 0)
        quantity = float(trade["quantity"])
        multiplier = float(trade["multiplier"] or 1)

        if trade["direction"] == "Short":
            gross_pnl = (entry_price - exit_price) * quantity * multiplier
        else:
            gross_pnl = (exit_price - entry_price) * quantity * multiplier

        charges = (
            float(trade["entry_fees"] or 0)
            + float(trade["exit_fees"] or 0)
            + float(trade["other_charges"] or 0)
        )

        trade_pnl = gross_pnl - charges
        net_pnl += trade_pnl

        if trade_pnl > 0:
            winning_trades += 1
        elif trade_pnl < 0:
            losing_trades += 1

    win_rate = (
        winning_trades / len(closed_trades) * 100
        if closed_trades
        else 0.0
    )

    return {
        "total_trades": total_trades,
        "closed_trades": len(closed_trades),
        "open_trades": len(open_trades),
        "net_pnl": round(net_pnl, 2),
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": round(win_rate, 2),
    }

def get_equity_curve_data() -> list[dict]:
    """Closed trades ka date-wise cumulative net P&L return karta hai."""

    trades = get_all_trades()

    closed_trades = [
        trade for trade in trades
        if trade["status"] == "Closed" and trade["exit_price"] is not None
    ]

    closed_trades.sort(
        key=lambda trade: (trade["trade_date"], trade["id"])
    )

    equity = 0.0
    equity_data = []

    for trade in closed_trades:
        entry_price = float(trade["entry_price"])
        exit_price = float(trade["exit_price"])
        quantity = float(trade["quantity"])
        multiplier = float(trade["multiplier"] or 1)

        if trade["direction"] == "Short":
            gross_pnl = (entry_price - exit_price) * quantity * multiplier
        else:
            gross_pnl = (exit_price - entry_price) * quantity * multiplier

        charges = (
            float(trade["entry_fees"] or 0)
            + float(trade["exit_fees"] or 0)
            + float(trade["other_charges"] or 0)
        )

        net_pnl = gross_pnl - charges
        equity += net_pnl

        equity_data.append({
            "date": trade["trade_date"],
            "trade_id": trade["id"],
            "net_pnl": round(net_pnl, 2),
            "equity": round(equity, 2),
        })

    return equity_data

def get_drawdown_statistics() -> dict:
    """Equity curve se drawdown statistics calculate karta hai."""

    equity_data = get_equity_curve_data()

    if not equity_data:
        return {
            "peak_equity": 0.0,
            "current_drawdown": 0.0,
            "max_drawdown": 0.0,
            "max_drawdown_percent": 0.0,
            "current_drawdown_percent": 0.0,
        }

    peak_equity = 0.0
    max_drawdown = 0.0
    max_drawdown_percent = 0.0

    for item in equity_data:
        equity = item["equity"]

        peak_equity = max(peak_equity, equity)

        drawdown = peak_equity - equity

        drawdown_percent = (
            (drawdown / peak_equity) * 100
            if peak_equity > 0
            else 0.0
        )

        max_drawdown = max(max_drawdown, drawdown)
        max_drawdown_percent = max(
            max_drawdown_percent,
            drawdown_percent
        )

    latest_equity = equity_data[-1]["equity"]
    current_drawdown = max(peak_equity - latest_equity, 0)

    current_drawdown_percent = (
        (current_drawdown / peak_equity) * 100
        if peak_equity > 0
        else 0.0
    )

    return {
        "peak_equity": round(peak_equity, 2),
        "current_drawdown": round(current_drawdown, 2),
        "max_drawdown": round(max_drawdown, 2),
        "max_drawdown_percent": round(max_drawdown_percent, 2),
        "current_drawdown_percent": round(
            current_drawdown_percent, 2
        ),
    }

def get_risk_management_statistics() -> dict:
    """Closed trades se risk management statistics calculate karta hai."""

    trades = get_all_trades()

    closed_trades = [
        trade for trade in trades
        if trade["status"] == "Closed"
        and trade["exit_price"] is not None
    ]

    closed_trades.sort(
        key=lambda trade: (trade["trade_date"], trade["id"])
    )

    if not closed_trades:
        return {
            "average_risk_reward": 0.0,
            "average_risk": 0.0,
            "largest_winning_trade": 0.0,
            "largest_losing_trade": 0.0,
            "consecutive_wins": 0,
            "consecutive_losses": 0,
        }

    risk_values = []
    reward_ratios = []
    pnl_values = []

    for trade in closed_trades:
        entry = float(trade["entry_price"])
        exit_price = float(trade["exit_price"])
        quantity = float(trade["quantity"])
        multiplier = float(trade["multiplier"] or 1)

        if trade["direction"] == "Short":
            gross_pnl = (entry - exit_price) * quantity * multiplier
        else:
            gross_pnl = (exit_price - entry) * quantity * multiplier

        charges = (
            float(trade["entry_fees"] or 0)
            + float(trade["exit_fees"] or 0)
            + float(trade["other_charges"] or 0)
        )

        net_pnl = gross_pnl - charges
        pnl_values.append(net_pnl)

        stop_loss = trade["stop_loss"]

        if stop_loss is not None:
            stop_loss = float(stop_loss)

            risk_per_unit = abs(entry - stop_loss)
            total_risk = risk_per_unit * quantity * multiplier

            if total_risk > 0:
                risk_values.append(total_risk)

                if net_pnl > 0:
                    reward_ratios.append(net_pnl / total_risk)

    winning_trades = [pnl for pnl in pnl_values if pnl > 0]
    losing_trades = [pnl for pnl in pnl_values if pnl < 0]

    consecutive_wins = 0
    consecutive_losses = 0

    for pnl in reversed(pnl_values):
        if pnl > 0 and consecutive_losses == 0:
            consecutive_wins += 1
        else:
            break

    for pnl in reversed(pnl_values):
        if pnl < 0 and consecutive_wins == 0:
            consecutive_losses += 1
        else:
            break

    return {
        "average_risk_reward": round(
            sum(reward_ratios) / len(reward_ratios), 2
        ) if reward_ratios else 0.0,

        "average_risk": round(
            sum(risk_values) / len(risk_values), 2
        ) if risk_values else 0.0,

        "largest_winning_trade": round(
            max(winning_trades), 2
        ) if winning_trades else 0.0,

        "largest_losing_trade": round(
            min(losing_trades), 2
        ) if losing_trades else 0.0,

        "consecutive_wins": consecutive_wins,
        "consecutive_losses": consecutive_losses,
    }






