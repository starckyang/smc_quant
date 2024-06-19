import numpy as np
import pandas as pd
from backtesting import Strategy
import copy

class OrderBlockStrategy(Strategy):
    lookback_period = 20  # Default value for lookback_period

    def init(self):
        self.index = 2
        self.current_trend = None
        self.breakthrough_found = False
        self.last_bt_index = -999
        self.fvg_found = False
        self.fvg_index = None
        self.orderblock = None
        self.position_each_time = self.equity / 5
        self.live_order_record = None
        self.pending_time = 0
        self.lookback_period = self.lookback_period  # Initialize lookback_period

    def next(self):
        self.fvg_found = False
        self.fvg_index = None
        self.trend_identification()
        self.fvg_identification()
        if (self.breakthrough_found or ((self.index - self.last_bt_index) < 3)) and self.fvg_found:
            self.order_block_identification()
        if self.orderblock:
            self.breaker_block_identification()
            if self.position.size == 0 and self.pending_time == 0:
                self.order_placing()
            elif self.live_order_record:
                self.position_close_check()
        self.index += 1
        if self.pending_time != 0:
            self.pending_time -= 1

    def trend_identification(self):
        # Identify breakthrough with a lookback period
        if (self.data.Close[-1] > np.max(self.data.High[max(0, self.index-self.lookback_period): max(0, self.index-1)])) and \
                (np.mean(self.data.High[max(0, self.index-24): max(0, self.index-1)]) > np.mean(self.data.High[max(0, self.index-72): max(0, self.index-1)])):
            self.current_trend = "upward"
            self.breakthrough_found = True
            self.last_bt_index = self.index
        elif (self.data.Close[-1] < np.min(self.data.Low[max(0, self.index-self.lookback_period): max(0, self.index-1)])) and \
                (np.mean(self.data.High[max(0, self.index-24): max(0, self.index-1)]) < np.mean(self.data.High[max(0, self.index-72): max(0, self.index-1)])):
            self.current_trend = "downward"
            self.breakthrough_found = True
            self.last_bt_index = self.index
        else:
            self.breakthrough_found = False

    def fvg_identification(self):
        if self.index >= 2:
            for i in range(min(3, self.index-2)):
                first_cs = (self.data.High[-3-i], self.data.Low[-3-i])
                previous_cs = (self.data.Open[-2-i], self.data.Close[-2-i])
                current_cs = (self.data.High[-1-i], self.data.Low[-1-i])
                if (self.current_trend == "upward" and first_cs[0] < current_cs[1]) or \
                   (self.current_trend == "downward" and first_cs[1] > current_cs[0]):
                    self.fvg_index = self.index-2-i
                    self.fvg_found = True

    def order_block_identification(self):
        index = self.fvg_index
        count = 10
        while index >= 0 and count > 0:
            if (self.current_trend == "upward" and self.data.Open[index] > self.data.Close[index] and self.data.Close[index+1] > self.data.Open[index]) or \
               (self.current_trend == "downward" and self.data.Open[index] < self.data.Close[index] and self.data.Close[index+1] < self.data.Open[index]):
                self.orderblock = [self.data.High[index], self.data.Low[index], self.current_trend]
                break
            index -= 1
            count -= 1

    def breaker_block_identification(self):
        if self.orderblock[2] == "upward" and self.data.Close[-1] < self.orderblock[1]:
            self.orderblock[2] = "downward"
            self.current_trend = "downward"
            self.pending_time = 3
        elif self.orderblock[2] == "downward" and self.data.Close[-1] > self.orderblock[0]:
            self.orderblock[2] = "upward"
            self.current_trend = "upward"
            self.pending_time = 3

    def order_placing(self):
        entry_price = self.data.Close[-1]
        if self.orderblock[2] == "upward" and entry_price < self.orderblock[0] and entry_price > self.orderblock[1]:
            hard_stop_loss = entry_price * 0.95
            self.buy(size=self.position_each_time//entry_price)
            self.live_order_record = {"ob": copy.deepcopy(self.orderblock), "size": self.position_each_time//entry_price, "sl": hard_stop_loss}
        elif self.orderblock[2] == "downward" and entry_price > self.orderblock[1] and entry_price < self.orderblock[0]:
            hard_stop_loss = entry_price * 1.05
            self.sell(size=self.position_each_time//entry_price, sl=hard_stop_loss)
            self.live_order_record = {"ob": copy.deepcopy(self.orderblock), "size": -self.position_each_time//entry_price, "sl": hard_stop_loss}

    def position_close_check(self):
        low = self.data.Low[-1]
        high = self.data.High[-1]
        if self.current_trend:
            if (self.live_order_record["size"] > 0 and self.current_trend == "downward") or \
               (self.live_order_record["size"] < 0 and self.current_trend == "upward"):
                self.position.close()
                self.live_order_record = None
                return
        if self.live_order_record["size"] > 0 and self.data.Close[-1] < self.live_order_record["ob"][1]:
            self.position.close()
            self.live_order_record = None
            return
        elif self.live_order_record["size
