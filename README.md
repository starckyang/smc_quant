# SMC-based Algorithmic Trading Strategy for ETH

## 📌 Project Overview
This project implements an **algorithmic trading strategy** based on the **Smart Money Concept (SMC)** in the Ethereum (ETHUSDT) market.  
It identifies institutional trading patterns such as **Order Blocks (OB)**, **Fair Value Gaps (FVG)**, and **Break of Structure (BoS)** to capture large market moves.

The strategy is backtested using **Binance API** for historical data retrieval and **backtesting.py** for performance evaluation.  
Data processing and analytics are handled with **pandas**, **numpy**, and **scipy**.

---

## 🎯 Strategy Logic

### Smart Money Concept (SMC)
- **Order Blocks (OB)**: The last opposing candle before a major move.
- **Fair Value Gap (FVG)**: Unfilled price gaps left by strong institutional moves.
- **Break of Structure (BoS)** / **Change of Character (CHoCH)**: Key market structure shifts.

### Trade Execution Flow
1. Identify **BoS** or **CHoCH**.
2. Detect **FVG** and locate the relevant **OB**.
3. Wait for price retracement into the OB zone.
4. Enter trade with:
   - **Stop-loss** at OB boundary.
   - **Exit** based on trend reversal or fixed drawdown rule.

---

## 📊 Backtest Results

| Dataset       | Annualized Return | Sharpe Ratio | Calmar Ratio | Max Drawdown | Win Rate |
|---------------|------------------|--------------|--------------|--------------|----------|
| Training (2020–2021) | **91.77%** | 1.31 | 4.20 | 28.2% | 23% |
| Test (2024)   | **53.39%** | 1.26 | 4.07 | 16.6% | 50% |

**Key Observations**
- Works well in trending markets with high liquidity pools.
- Suffers in choppy markets with frequent false entries.
- Requires longer execution horizon for optimal performance.

---

## 🛠️ Tech Stack
- **Python**: Core implementation
- **Binance API**: Market data retrieval
- **backtesting.py**: Backtesting framework
- **pandas**, **numpy**, **scipy**: Data processing and analytics
