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
from DataManager import CandleData as Chart

class OrderPositionManager:

    def __init__(self, acc: Account, api: Api):

        self.primary = acc
        self.api = api
        self.orderlist = []
        self.positionlist = []

    async def FindPosition(self, contract: str):

        send = 0
        for i in self.positionlist:

            send = i["type"] if contract == i['contractId'] else send
        
        return send

    async def Update(self, api_up: None | bool = None):

        if api_up == None:
            api_up = await Ping()
        
        if not api_up:
            return

        orders = Check_Orders_Sync(self.api.token,self.primary.id)
        positions = Check_Positions_Sync(self.api.token,self.primary.id)

        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(orders)
            t2 = tg.create_task(positions)

        orders = t1.result()
        positions = t2.result()

        self.orderlist = orders if orders != '' else self.orderlist
        self.positionlist = positions if positions != '' else self.positionlist

        return orders, positions
    
    async def UpdateOrders(self, api_up: None | bool = None):
        
        if api_up == None:
            api_up = await Ping()
        
        if not api_up:
            return

        orders = await Check_Orders_Sync(self.api.token,self.primary.id)

        self.orderlist = orders if orders != '' else self.orderlist

        return orders
    
    async def UpdatePositions(self, api_up: None | bool = None):
        
        if api_up == None:
            api_up = await Ping()
        
        if not api_up:
            return

        positions = await Check_Positions_Sync(self.api.token,self.primary.id)

        self.positionlist = positions if positions != '' else self.positionlist

        return positions

    async def PlaceOrder(self, con_id: str, order_type: int, price: float, order_side = 0 | 1, order_size = 1, api_up = None | bool):
        
        """

        definitions:\n
        
        con_id: the contract you searched up\n
        order_type: type of order\n
        0 = Unknown\n
        1 = Limit\n
        2 = Market\n
        3 = StopLimit\n
        4 = Stop\n
        5 = TrailingStop\n
        6 = JoinBid\n
        7 = JoinAsk\n
        order_side: side your trading\n
        0 = long\n
        1 = short\n
        size: contracts to trade\n
        stop_loss: Stop loss in ticks\n
        take_profit: Take profit in ticks\n
        
        """

        if api_up == None:
            api_up = await Ping()
        
        if not api_up:
            return

        order = await Place_Order_Sync(self.api.token,
                                       self.primary.id,
                                       contract_id=con_id,
                                       order_type=order_type,
                                       side=order_side,
                                       size=order_size,
                                       price=price)

        try:
            if order['success']:
                self.UpdateOrders(api_up=api_up)
                print("Order Placed:",order['orderId'])
            else:
                print("Order Failed to place")
                return ''

        except KeyError:
            return ''

    async def PlaceOrderOCO(self, con_id: str, order_type: int, price: float, sl: int, tp: int, order_side = 0 | 1, order_size = 1, api_up = None | bool):
        
        if api_up == None:
            api_up = await Ping()
        
        if not api_up:
            return
        
        order=await Place_Order_Sync_Braket(self.api.token,
                                            self.primary.id,
                                            contract_id=con_id,
                                            order_type=order_type,
                                            side=order_side,
                                            size=order_size,
                                            stop_loss=sl,
                                            take_profit=tp,
                                            price=price)

        try:
            if order['success']:
                self.UpdateOrders(api_up=api_up)
                print("Order Placed:",order['orderId'])
            else:
                print("Order Failed to place")
                return ''

        except KeyError:
            return ''
        
    async def CloseOrder(self, value: int = 0, api_up: None | bool = None):
        
        if api_up == None:
            api_up = await Ping()
        
        if not api_up:
            return

        order_id = self.orderlist[value]['id']

        url = "https://api.topstepx.com/api/Order/cancel"

        payload = {
        "accountId": self.primary.id,
        "orderId": order_id
        }
        headers = {
        'accept': 'text/plain',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + self.api.token
        }

        response = ''
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url,json=payload,headers=headers,timeout=5)
        except httpx.ReadTimeout:
            print("The server took too long to send data. Moving to the next task...")
            return ''
        except httpx.HTTPError as e:
            print(f"An HTTP error occurred: {e}")
            return ''
        
        response = response.json()

        try:
            if response['success'] or response['errorCode'] == 2:
                self.orderlist.remove(self.orderlist[value])

        except KeyError:
            return ''
        
    async def ClosePosition(self, con_id: str, api_up: None | bool = None):

        if api_up == None:
            api_up = await Ping()
        
        if not api_up:
            return

        url = "https://api.topstepx.com/api/Position/closeContract"

        payload = {
        "accountId": self.primary.id,
        "contractId": con_id
        }
        headers = {
        'accept': 'text/plain',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + self.api.token
        }

        response = ''
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url,json=payload,headers=headers,timeout=5)
        except httpx.ReadTimeout:
            print("The server took too long to send data. Moving to the next task...")
            return ''
        except httpx.HTTPError as e:
            print(f"An HTTP error occurred: {e}")
            return ''