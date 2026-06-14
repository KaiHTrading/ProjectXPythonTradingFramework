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

class Account:

    def __init__(self, list: AccList, value=0):
        
        try:
            self.account = AccList.accounts[value]
            self.api = AccList.api
            self.id = self.account[0]
            self.name = self.account[1]
            self.bal = self.account[2]
        except IndexError:
            print("Failed to find account at value:",value)
    
    def __str__(self):

        str = "|Id              |Name                                |Bal           |\n"
        str1 = f"|{self.id:<16}|"
        str2 = f"{self.name:<36}|"
        str3 = f"{self.bal:<14}|"
        str4 = str1+str2+str3
        str+=str4

        return str
    
    def __repr__(self):
        
        str1 = f"{self.id:<16},"
        str2 = f" {self.name:<36},"
        str3 = f" {self.bal:<14}"
        str4 = str1+str2+str3
        return str4

    async def Update(self, api_up = None | bool):

        if api_up == None:
            api_up = await Ping()

        if api_up:
            acc_list = Get_Accounts_Sync(self.api.token)
            await acc_list

            for i in acc_list:

                self.account = i if i[0] == self.account[0] else self.account

            self.id = self.account[0]
            self.name = self.account[1]
            self.bal = self.account[2]