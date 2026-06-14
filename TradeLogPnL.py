import requests
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv, find_dotenv
import asyncio
import httpx
import os
from apicall import *
from Account import Account
from ApiInterface import ApiInterface as Api

class TradeLogPnL:

    def __init__(self, api: Api, account: Account) -> TradeLogPnL:

        self.api = api
        self.account = account

    async def PullLog(self, length=1, api_up = None | bool) -> str:
        """
        definitions:\n
        length: Length of trade log in days, 1 day is from 22:00 UTC to 21:00 UTC\n 
        of next day or current time(whichever is closest)
        """

        if api_up == None:
            api_up = await Ping()

        if api_up:
            # 1. Get current time in UTC
            time_now = datetime.now(timezone.utc)

            # 2. Create the target time for today at 22:00 UTC
            target_time = time_now.replace(hour=22, minute=0, second=0, microsecond=0)

            # 3. If 22:00 UTC hasn't happened yet today, the "last time" was yesterday
            if time_now < target_time:
                target_time -= timedelta(days=1)

            if length > 1:
                target_time -= timedelta(days=length-1)

            # 4. Calculate the difference
            time_difference = time_now - target_time


            #compile time
            time_start = time_now - time_difference
            start = time_start.strftime("%Y-%m-%d") + "T" + time_start.strftime("%T.%f")[:-3] + 'Z'
            end = time_now.strftime("%Y-%m-%d") + "T" + time_now.strftime("%T.%f")[:-3] + 'Z'

            url = "https://api.topstepx.com/api/History/retrieveBars"

            payload = {
            "accountId": self.account.id,
            "startTimestamp": start,
            "endTimestamp": end
            }
            headers = {
            'accept': 'text/plain',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.api.token
            }

            response = ''
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(url,json=payload,headers=headers,timeout=10)
                except httpx.ReadTimeout:
                    print("The server took too long to send data. Moving to the next task...")
                    return ''
                except httpx.HTTPError as e:
                    print(f"An HTTP error occurred: {e}")
                    return ''
            response = response.json()

            try:
                """
                format:\n\n
                trade: tradeid\n
                contract: contractid\n
                PnL: pnl\n
                Timestamp: Timestamp

                """

                log = f"|{"TradeId:":^16}|" + f"{"ContractId":^32}|" + f"{"PnL":^9}|" + f"{"Timestamp":^26}|\n"
                for i in response['trades']:

                    pnl = i["profitAndLoss"] + i['fees'] + i['comissions'] if not i['voided'] else 0
                    log += f"|{i['id']:^16}|" + f"{i['contractId']:^32}|" + f"{str(round(pnl,2)):^9}|" + f"{i['creationTimestamp']:^26}|\n"

                return log

            except KeyError:
                return ''

    async def PullPnL(self, length=1, api_up = None | bool) -> float:
        """
        definitions:\n
        length: Length of trade log in days, 1 day is from 22:00 UTC to 21:00 UTC\n 
        of next day or current time(whichever is closest)
        """

        if api_up == None:
            api_up = await Ping()

        if api_up:
            # 1. Get current time in UTC
            time_now = datetime.now(timezone.utc)

            # 2. Create the target time for today at 22:00 UTC
            target_time = time_now.replace(hour=22, minute=0, second=0, microsecond=0)

            # 3. If 22:00 UTC hasn't happened yet today, the "last time" was yesterday
            if time_now < target_time:
                target_time -= timedelta(days=1)

            if length > 1:
                target_time -= timedelta(days=length-1)

            # 4. Calculate the difference
            time_difference = time_now - target_time


            #compile time
            time_start = time_now - time_difference
            start = time_start.strftime("%Y-%m-%d") + "T" + time_start.strftime("%T.%f")[:-3] + 'Z'
            end = time_now.strftime("%Y-%m-%d") + "T" + time_now.strftime("%T.%f")[:-3] + 'Z'

            url = "https://api.topstepx.com/api/History/retrieveBars"

            payload = {
            "accountId": self.account.id,
            "startTimestamp": start,
            "endTimestamp": end
            }
            headers = {
            'accept': 'text/plain',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + self.api.token
            }

            response = ''
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.post(url,json=payload,headers=headers,timeout=10)
                except httpx.ReadTimeout:
                    print("The server took too long to send data. Moving to the next task...")
                    return ''
                except httpx.HTTPError as e:
                    print(f"An HTTP error occurred: {e}")
                    return ''
            response = response.json()

            try:
                pnl = 0
                for i in response['trades']:
                
                    pnl += i["profitAndLoss"] + i['fees'] + i['comissions'] if not i['voided'] else 0

                return pnl

            except KeyError:
                return ''

