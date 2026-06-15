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
from DataManager import CandleData as Chart

#will add databento compatibility in future update

class Strategy:

    def __init__(self,primary: int = 0,data: None | list[dataset,schema,stype_in,symbols] = None):

        self.api = Api()
        self.acc_list = AccList(self.api)
        self.primary = Acc(self.acc_list,primary)
        self.management = OPM(self.primary,self.api)
        self.log = Log(self.api,self.primary)
        self.data = []
        self.scheduler = []
        self.loop = asyncio.new_event_loop()

    def add_data(self, 
                 name: str, 
                 search: str, 
                 timeframe: str = 'm', 
                 compound: int = 1,
                 max:int = 1000, 
                 data: None | list[dataset,schema,stype_in,symbols] = None):

        search_Id = Get_ID(self.api.token,search=search)
        datasteam = Chart(search_Id,self.api,timeframe=timeframe,compound=compound,data=data,max=max)
        self.data.append((name, datasteam))

    def add_scheduled_task(self, name: str, task: asyncio.Coroutine, frequency: int, condition: bool = True):

        period = frequency / 60
        self.scheduler.append((name,task,period,condition))
    
    async def run_task(self, task: tuple):

        asyncio.wait(task[2])
        if task[3]:
            self.loop.create_task(task[1])

        return 'Done task ' + task[0]
