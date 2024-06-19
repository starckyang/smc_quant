# src/strategy.py

import numpy as np
import pandas as pd
from backtesting import Strategy
import copy
from config.config import *

class OrderBlockStrategy(Strategy):
    def init(self):
        self.index = 2
        self.current_trend = None
        self.breakthrough_found = False
        self.last_bt_index = -999
        self.fvg_found = False
        self.fvg_index = None
        self.orderblock = None
        self.position_each_time = 1000000 * investment_proportion
        self.live_order_record = None
        self.pending_time = 0
        self.portion = stop_loss_percentage
        self.previous_high_index = 0
        self.high = None
        self.high_index = None
        self.previous_low_index = 0
        self.low = None
        self.low_index = None
        self.reversal_percentage = reversal_percentage

    def next(self):
        self.fvg_found = False
        self.fvg_index = None
        self.trend_identification()
        self.fvg_identification()
        if (self.breakthrough_found or ((self.index - self.last_bt_index) < 3)) and self.fvg_found:
            self.order_block_identification()
        if self.orderblock:
            if (self.position.size == 0) and (self.pending_time == 0):
                self.order_placing()
        if self.live_order_record:
            self.position_close_check()
        self.index += 1
        if self.pending_time != 0:
            self.pending_time -= 1

    def trend_identification(self):
        if (self.high is None) or (self.data.Close[-1] >= self.high):
            self.high = self.data.Close[-1]
            self.high_index = self.index - 1
            self.current_trend = "upward"
            self.breakthrough_found = True
            self.last_bt_index = self.index
            self.low = np.inf
            for i in range(self.previous_high_index, self.high_index):
                if self.data.Close[i] <= self.low:
                    self.low = self.data.Close[i]
                    self.low_index = i
            self.previous_high_index = self.high_index
        elif (self.low is None) or (self.data.Close[-1] <= self.low):
            self.low = self.data.Close[-1]
            self.low_index = self.index - 1
            self.high = -np.inf
            self.current_trend = "downward"
            self.breakthrough_found = True
            self.last_bt_index = self.index
            for i in range(self.previous_low_index, self.low_index):
                if self.data.Close[i] <= self.low:
                    self.high = self.data.Close[i]
                    self.high_index = i
            self.previous_low_index = self.low_index
        else:
            self.breakthrough_found = False

    def fvg_identification(self):
        if self.index >= 2:
            for i in range(min(3, self.index-2)):
                first_cs = (self.data.High[-3-i], self.data.Low[-3-i])
                current_cs = (self.data.High[-1-i], self.data.Low[-1-i])
                if ((self.current_trend == "upward") & (first_cs[0] < current_cs[1])) or \
                   ((self.current_trend == "downward") & (first_cs[1] > current_cs[0])):
                    self.fvg_index = self.index-2-i
                    self.fvg_found = True

    def order_block_identification(self):
        index = self.fvg_index
        count = 10
        while (index >= 0) & (count > 0):
            if ((self.current_trend == "upward") & (self.data.Open[index] > self.data.Close[index]) & (self.data.Close[index+1] > self.data.Open[index])) or \
               ((self.current_trend == "downward") & (self.data.Open[index] < self.data.Close[index]) & (self.data.Close[index+1] < self.data.Open[index])):
                self.orderblock = [self.data.High[index], self.data.Low[index], self.current_trend, self.index]
                break
            index -= 1
            count -= 1

    def order_placing(self):
        entry_price = self.data.Close[-1]
        if (self.orderblock[2] == "upward") & (entry_price < self.orderblock[0]) & (entry_price > self.orderblock[1]):
            hard_stop_loss = entry_price * (1-self.portion)
            self.buy(size=self.position_each_time//entry_price)
            self.live_order_record = {"ob": copy.deepcopy(self.orderblock), "size": self.position_each_time//entry_price,
                                      "sl": hard_stop_loss, "top": copy.deepcopy(entry_price)}
            self.orderblock = None
        elif (self.orderblock[2] == "downward") & (entry_price > self.orderblock[1]) & (entry_price < self.orderblock[0]):
            hard_stop_loss = entry_price * (1+self.portion)
            self.sell(size=self.position_each_time//entry_price, sl=hard_stop_loss)
            self.live_order_record = {"ob": copy.deepcopy(self.orderblock), "size": -self.position_each_time//entry_price,
                                      "sl": hard_stop_loss, "top": copy.deepcopy(entry_price)}
            self.orderblock = None

    def position_close_check(self):
        low = copy.deepcopy(self.data.Low[-1])
        high = copy.deepcopy(self.data.High[-1])
        if (self.live_order_record["size"] > 0) & (high > self.live_order_record["top"]):
            self.live_order_record["top"] = copy.deepcopy(high)
        elif (self.live_order_record["size"] < 0) & (low < self.live_order_record["top"]):
            self.live_order_record["top"] = copy.deepcopy(low)
        if (self.live_order_record["size"] > 0) & (high < self.live_order_record["top"]*(1-self.reversal_percentage)):
            self.position_closing()
            return
        if (self.live_order_record["size"] < 0) & (low > self.live_order_record["top"]*(1+self.reversal_percentage)):
            self.position_closing()
            return
        if (self.live_order_record["size"] > 0) & (self.data.Close[-1] < self.live_order_record["sl"]):
            self.position_closing()
            return
        elif (self.live_order_record["size"] < 0) & (self.data.Close[-1] > self.live_order_record["sl"]):
            self.position_closing()
            return

    def position_closing(self):
        self.position.close()
        self.live_order_record = None
