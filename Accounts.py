import requests
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv, find_dotenv
import asyncio
import httpx
import os
from apicall import *
from ApiInterface import ApiInterface as Api

class Accounts:

    def __init__(self, interface: Api):

        self.api = interface

        self.accounts = ''
        while self.accounts == '':
            self.accounts = Get_Accounts(self.api.token)

    def __str__(self):

        #ID: 16 char Name: 36 Bal: 14
        str = "|Id              |Name                                |Bal           |\n"

        for i in self.accounts:

            strId = f"|{i[0]:<16}|"
            strName = f"{i[1]:<36}|"
            strBal = f"{i[2]:<14}|\n"
            strFull = strId+strName+strBal
            str+=strFull

        return str
    
    async def Update(self, api_up = None | bool, attempts = 5):

        acc_list = ''
        if api_up == None:
            api_up = await Ping()

        attempt = 0
        while acc_list == '' and api_up and attempt < attempts:
            acc_list = Get_Accounts_Sync(self.api.token)
            await acc_list
            attempt += 1

        self.accounts = acc_list if api_up else self.accounts

            