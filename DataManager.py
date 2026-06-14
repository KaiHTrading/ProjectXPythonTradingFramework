import requests
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv, find_dotenv
import asyncio
import httpx
import os
from apicall import *
from ApiInterface import ApiInterface as Api

def TimeframeType(str):

    if str == 's':
        return 1
    elif str == 'm':
        return 2
    elif str == 'h':
        return 3
    elif str == 'D':
        return 4
    elif str == 'W':
        return 5
    elif str == 'M':
        return 6
    elif str == 'Y':
        return 7
    raise Exception("Invalid Timeframe Str")

class CandleData:

    def __init__(self, 
                 stream,
                 contract_id: str | None, 
                 interface=Api | None, 
                 timeframe='m' | 's, m, h, D, W, M, Y', 
                 compound: int = 1, 
                 max = 1000, 
                 subscribe = list[dataset, schema, stype_in, symbols]):
        
        self.api = interface
        self.stream = stream
        self.timeframe = TimeframeType(timeframe)
        self.compound = compound
        self.data = [None] * max
        self.max = max
        self.con_id = contract_id

        if self.api == None:
            pass #databento implementation coming later

    async def UpdateData(self): #gets past candles to use for calculations

        if self.api == None:
            pass #databento implementation coming later

        else:
            
            candles = await Get_Candles_Sync(self.api.token,self.con_id,unit=self.timeframe,unit_num=self.compound,limit=self.max)


    async def GetClose(self): #gets live price data if needed
        pass