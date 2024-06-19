# src/main.py

import pickle
import os
from backtesting import Backtest
from src.strategy import OrderBlockStrategy

data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ETHUSDT_training.pkl')

if __name__ == "__main__":
    # Load your data
    with open(data_path, "rb") as f:
        data = pickle.load(f)
    # Run the backtest
    bt = Backtest(data, OrderBlockStrategy, cash=1000000)
    stats = bt.run()
    print(stats)
    bt.plot()
