import requests
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv, find_dotenv
import asyncio
import httpx
import os
from apicall import *
from Accounts import Accounts as AccList
from ApiInterface import ApiInterface as Api
from Account import Account as Acc
from OrderPositionManagement import OrderPositionManager as OPM
from TradeLogPnL import TradeLogPnL as Log

#will add databento compatibility in future update

class Strategy:

    def __init__(self,primary=None | int,timeframe='m' | 's, m, h, D, W, M, Y, t',data=None | list[dataset,schema,stype_in,symbols]):

        self.api = Api()
        self.acc_list = AccList(self.api)
        if primary == None:
            print(str(self.acc_list))
            index = int(input("Choose account to set as primary (0-x): "))
            primary = index
        self.primary = Acc(self.acc_list,primary)
        self.management = OPM(self.primary,self.api)
        self.log = Log(self.api,self.primary)
        #self.data = 
