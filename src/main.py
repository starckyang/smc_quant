# src/main.py
import pandas as pd
import pickle
import os
from backtesting import Backtest
from src.strategy import OrderBlockStrategy

data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ETHUSDT_testing_15m.pkl')

if __name__ == "__main__":
    # Load your data
    with open(data_path, "rb") as f:
        data = pickle.load(f)
        # Convert "Time" column to datetime and set it as index
    data["Time"] = pd.to_datetime(data["Time"])
    data.set_index("Time", inplace=True)
    # Run the backtest
    bt = Backtest(data, OrderBlockStrategy, cash=1000000)
    stats = bt.run()
    print(stats)
    bt.plot()
