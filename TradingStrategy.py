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

def TimeToNext(mins: int | float):

    now = datetime.now()
    next: float

    if type(mins) == int:
        next = (mins - now.minute % mins) * 60 - now.second - now.microsecond / 1_000_000

    elif type(mins) == float: 
        min = now.minute + now.second / 60 + now.microsecond / 60_000_000
        next = (mins - min % mins) * 60

    return next

def Factory(task: function, data: tuple):

    length = len(data)

    if length == 0:
        return task()
    elif length == 1:
        return task(data[0])
    elif length == 2:
        return task(data[0],data[1])
    elif length == 3:
        return task(data[0],data[1],data[2])
    elif length == 4:
        return task(data[0],data[1],data[2],data[3])
    elif length == 5:
        return task(data[0],data[1],data[2],data[3],data[4])
    elif length == 6:
        return task(data[0],data[1],data[2],data[3],data[4],data[5])
    else:
        print("Too many datapoints")

class Strategy:

    def __init__(self, name: str, primary: int = 0):

        self.name = name
        self.api = Api()
        self.acc_list = AccList(self.api)
        self.primary = Acc(self.acc_list,primary)
        self.management = OPM(self.primary,self.api)
        self.log = Log(self.api,self.primary)
        self.data = []
        self.scheduler = []
        self.structured_scheduler = []
        self.tasksOngoing = []
        self.running = False
        self.loop = asyncio.new_event_loop()

    def __str__(self, api_up: None | bool = None):
        
        """
        Format:

        self.name
        Api connection:
        [api str]

        Trading Account: self.primary.name
        Balance: self.primary.bal
        PnL: self.log.pnl if self.log.pnl != None else asyncio.run(self.log.PullPnl())
        Running: self.running

        Account List:
        [account list]

        Scheduled tasks:
        [names of scheduled tasks]

        Structured tasks:
        [names of structured tasks]


        """

        if self.log.pnl == None:
            asyncio.run(self.log.PullPnL(api_up=api_up))

        scheduled = ''
        structured = ''
        
        for i in self.structured_scheduler:
            structured += i[0] + "\n"
        
        for i in self.scheduler:
            scheduled += i[0] + "\n"

        read = (
                self.name + ':\n' +
                "Api connection:\n" + str(self.api) + '\n\n' +
                "Trading Account: " + self.primary.name + '\n' + 
                "Balance: " + str(self.primary.bal) + '\n' + 
                "Pnl: " + str(self.log.pnl) + '\n' + 
                "Running: " + str(self.running) + '\n\n' +
                "Account List:\n" + str(self.acc_list) + '\n\n' +
                "Scheduled Tasks:\n" + scheduled + '\n\n' +
                "Structured Tasks:\n" + structured + '\n\n'
               )
        
        return read

    def set_primary(self, primary: int = 0, name: str = ''):

        self.primary = Acc(self.acc_list,value=primary,name=name)

    def add_data(self, 
                 name: str, 
                 search: str, 
                 timeframe: str = 'm', 
                 compound: int = 1,
                 max:int = 1000, 
                 data: None | list = None):

        search_Id = Get_ID(self.api.token,search=search)
        datasteam = Chart(contract_id=search_Id['id'],interface=self.api,timeframe=timeframe,compound=compound,subscribe=data,max=max)
        self.data.append((name, datasteam))

    def add_scheduled_task(self, name: str, task: function, frequency: float | int, condition: bool = True, data: tuple = ()):

        period = 60 / frequency
        self.scheduler.append((name,task,period,lambda: condition, data))
    
    def add_structured_task(self, name: str, task: function, mins_exc: int | float = 0, data: tuple = ()):

        self.structured_scheduler.append((name,task,mins_exc, data))

    async def run_task(self, task: tuple):

        while self.running:
            await asyncio.sleep(task[2])
            if task[3] and self.running:
                
                try:
                    print("Running:",task[0])
                    todo = self.loop.create_task(Factory(task[1],task[4]))
                    await todo
                except TypeError:
                    print("Call",task[0],"failed")
                
        
        return
    
    async def run_structured_task(self, task: tuple):

        while self.running:
            
            try:
                print("Running:",task[0])
                await asyncio.sleep(TimeToNext(task[2]))
                todo = self.loop.create_task(Factory(task[1],task[3]))
                await todo
            except TypeError:
                    print("Call",task[0],"failed")
            
        
        return

    def PlaceOrder(self, data: Chart, dir: str, type: int, price: None | float = None, size: int = 1, api_up: None | bool = None):
        
        if api_up == None:
            api_up = bool(self.api)
        
        if not api_up:
            return

        L_S = 0 if dir.__contains__('l') else 1

        return self.management.PlaceOrder(data.con_id,type,price,L_S,size,api_up)
    
    def PlaceOrderOCO(self, data: Chart, dir: str, type: int, price: None | int = None, size: int = 1, api_up: None | bool = None, bracket: tuple = ()): #(sl, tp)
        
        if api_up == None:
            api_up = bool(self.api)
        
        if not api_up:
            return

        L_S = 0 if dir.__contains__('l') else 1
        sl = bracket[0]
        tp = bracket[1]

        return self.management.PlaceOrderOCO(data.con_id,type,price,sl,tp,L_S,size,api_up)

    def ClosePosition(self, data: Chart, api_up: None | bool = None):

        if api_up == None:
            api_up = bool(self.api)
        
        if not api_up:
            return

        return self.management.ClosePosition(data.con_id, api_up)

    async def run(self):

        self.running = True
        print(self.name,"Strategy is now running...")
        async with asyncio.TaskGroup() as tg:
            tasks_scheduled = [tg.create_task(self.run_task(items)) for items in self.scheduler]
            tasks_structured = [tg.create_task(self.run_structured_task(items)) for items in self.structured_scheduler]

    def stop(self):

        self.running = False
        print(self.name,"Strategy is now stopped...")