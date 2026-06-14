import requests
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv, find_dotenv
import os
import asyncio
import httpx

loop_api = asyncio.new_event_loop()

#ping api
async def Ping() -> bool:

    headers = {
        'accept': 'text/plain',
        }

    response = ''

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("https://api.topstepx.com/api/Status/ping",headers=headers,timeout=2)
        except httpx.ReadTimeout:
            print("The server took too long to send data. Moving to the next task...")
            return False
        except httpx.HTTPError as e:
            print(f"An HTTP error occurred: {e}")
            return False

    return response.text == "pong"


#get token for session
async def Get_Token_Sync(apikey, username):
    url = "https://api.topstepx.com/api/Auth/loginKey"

    payload = {
    "userName": username,
    "apiKey": apikey
    }
    headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json'
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url,json=payload,headers=headers,timeout=10)
        except httpx.ReadTimeout:
            print("The server took too long to send data. Moving to the next task...")
        except httpx.HTTPError as e:
            print(f"An HTTP error occurred: {e}")
    response = response.json()
    #print(response['token']) #debug statement

    try:
        return response['token']
    except KeyError:
        pass

def Get_Token(apikey, username):

    """
    Returns a session token for you to use in all your other api calls, save it to a variable\n

    apiKey: your api key, hopefully in a dotenv file (see how to load in test calls)\n
    username: your topstep email, also in the dotenv file hopefully\n
    """

    url = "https://api.topstepx.com/api/Auth/loginKey"

    payload = json.dumps({
    "userName": username,
    "apiKey": apikey
    })
    headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json'
    }

    response = ''
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response = response.json()
    except requests.exceptions.ConnectTimeout:
        return response
    #print(response['token']) #debug statement

    try:
        return response['token']
    except KeyError, TypeError:
        return ''

def Get_Token_Task(apikey, username):
    token = asyncio.create_task(Get_Token_Sync(apikey, username))
    return token

#get active accounts on your topstepx account [0] is id [1] is name of account
async def Get_Accounts_Sync(token):
    url = "https://api.topstepx.com/api/Account/search"

    payload = {
    "onlyActiveAccounts": True
    }
    headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
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
    #print(response['accounts'][0]['id']) #debug statement
    accounts = []

    try:
        for i in range(len(response['accounts'])):
            accounts.append([response['accounts'][i]['id'],response['accounts'][i]['name'],response['accounts'][i]['balance']])

        #returns acc in format of [id,name]
        return accounts
    except KeyError, TypeError:
        return ''

def Get_Accounts(token):

    """
    Finds all accounts using your session token linked to your api key/account\n

    token: session token\n
    """

    url = "https://api.topstepx.com/api/Account/search"

    payload = json.dumps({
    "onlyActiveAccounts": True
    })
    headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }

    response = ''
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response = response.json()
    except requests.exceptions.ConnectTimeout:
        return response
    accounts = []

    try:
        for i in range(len(response['accounts'])):
            accounts.append([response['accounts'][i]['id'],response['accounts'][i]['name'],response['accounts'][i]['balance']])

        #returns acc in format of [id,name]
        return accounts
    
    except KeyError:
        return ''

def Get_Accounts_Task(token):
    accounts = asyncio.create_task(Get_Accounts_Sync(token))
    return accounts

#Get the ID for the contract
async def Get_ID_Sync(token, search):
    url = "https://api.topstepx.com/api/Contract/search"

    payload = {
    "live": False,
    "SearchText": search
    }
    headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url,json=payload,headers=headers,timeout=10)
    response = response.json()
    #print(response['contracts'][0]['id']) #debug statement

    #return the top contract from search
    try:
        return response['contracts'][0]
    except KeyError:
        pass

def Get_ID(token, search):

    """
    Returns the first contract found from the query\n

    search: keyword\n
    token: session token\n
    """

    url = "https://api.topstepx.com/api/Contract/search"

    payload = json.dumps({
    "live": False,
    "SearchText": search
    })
    headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }

    response = ''
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response = response.json()
    except requests.exceptions.ConnectTimeout:
        return response

    #return the top contract from search
    try:
        return response['contracts'][0]
    except KeyError:
        pass

def Get_ID_Task(token, search):
    id = asyncio.create_task(Get_ID_Sync(token, search))
    return id

#place order on an acc
async def Place_Order_Sync_Braket(token, acc_id, contract_id, order_type, side, size, stop_loss=0, take_profit=0, price=None):
    """

    definitions:\n
    
    token: token for your session\n
    acc_id: arr containing acc id and the name of the acc\n
    contract_id: the contract you searched up\n
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

    url = "https://api.topstepx.com/api/Order/place"
    sl = 0
    tp = 0
    if side == 0:
        sl = stop_loss * -1
        tp = take_profit
    if side == 1:
        sl = stop_loss
        tp = take_profit * -1

    #set tp and or sl if used in order (oco brackets that dont delete themselves be careful)
    loss_type = 0
    profit_type = 0
    if sl != 0:
        loss_type = 4
    if tp != 0 :
        profit_type = 1


    payload = {
    "accountId": acc_id[0],
    "contractId": contract_id['id'],
    "type": order_type,
    "side": side,
    "size": size,
    "limitPrice": price,
    "stopPrice": price,
    "trailPrice": price,
    "customTag": None,
    "stopLossBracket": {
        "ticks": sl,
        "type": loss_type
    },
    "takeProfitBracket": {
        "ticks": tp,
        "type": profit_type
    }
    }
    headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url,json=payload,headers=headers)
    response = response.json()
    
    #print order confirmation
    try:
        if response['success']:
            print("\nOrder " + str(response['orderId']) + " placed.")

        return response
    except KeyError:
        pass

async def Place_Order_Sync(token, acc_id, contract_id, order_type, side, size, price=None):
    """

    definitions:\n
    
    token: token for your session\n
    acc_id: arr containing acc id and the name of the acc\n
    contract_id: the contract you searched up\n
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

    url = "https://api.topstepx.com/api/Order/place"


    payload = {
    "accountId": acc_id,
    "contractId": contract_id,
    "type": order_type,
    "side": side,
    "size": size,
    "limitPrice": price,
    "stopPrice": price,
    "trailPrice": price,
    "customTag": None,
    }
    headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url,json=payload,headers=headers)
    response = response.json()
    
    #print order confirmation
    try:
        if response['success']:
            print("\nOrder " + str(response['orderId']) + " placed.")

        return response
    except KeyError:
        pass

def Place_Order_Bracket(token, acc_id, contract_id, order_type, side, size, stop_loss=0, take_profit=0, price=None):
    """
    For placing orders on a given account, stoploss and tp are optional, by default they are off\n
    
    definitions:\n
    
    token: token for your session\n
    acc_id: arr containing acc id and the name of the acc\n
    contract_id: the contract you searched up\n
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

    url = "https://api.topstepx.com/api/Order/place"
    sl = 0
    tp = 0
    if side == 0:
        sl = stop_loss * -1
        tp = take_profit
    if side == 1:
        sl = stop_loss
        tp = take_profit * -1


    #set tp and or sl if used in order (oco brackets that dont delete themselves be careful)
    loss_type = 0
    profit_type = 0
    if sl != 0:
        loss_type = 4
    if tp != 0 :
        profit_type = 1


    payload = json.dumps({
    "accountId": acc_id[0],
    "contractId": contract_id['id'],
    "type": order_type,
    "side": side,
    "size": size,
    "limitPrice": price,
    "stopPrice": price,
    "trailPrice": price,
    "customTag": None,
    "stopLossBracket": {
        "ticks": sl,
        "type": loss_type
    },
    "takeProfitBracket": {
        "ticks": tp,
        "type": profit_type
    }
    })
    headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }

    response = ''
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response = response.json()
    except requests.exceptions.ConnectTimeout:
        return response

    #print order confirmation
    try:
        if response['success']:
            print("\nOrder " + str(response['orderId']) + " placed.")

        return response
    except KeyError, TypeError:
        pass

async def Mod_Order(token, acc_id, order_id, price, size=1):

    url = "https://api.topstepx.com/api/Order/modify"

    payload = json.dumps({
        "accountId": acc_id,
        "orderId": order_id,
        "size": size,
        "limitPrice": None,
        "stopPrice": price,
        "trailPrice": None
        })
    headers = {
        'accept': 'text/plain',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
        }

    response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
    response = response.json()
    print(response)

def Place_Order(token, acc_id, contract_id, order_type, side, size, price=None):
    """

    definitions:\n
    
    token: token for your session\n
    acc_id: arr containing acc id and the name of the acc\n
    contract_id: the contract you searched up\n
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

    url = "https://api.topstepx.com/api/Order/place"


    payload = json.dumps({
    "accountId": acc_id[0],
    "contractId": contract_id['id'],
    "type": order_type,
    "side": side,
    "size": size,
    "limitPrice": price,
    "stopPrice": price,
    "trailPrice": price,
    "customTag": None,
    })
    headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }

    response = ''
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response = response.json()
    except requests.exceptions.ConnectTimeout:
        return response
    
    #print order confirmation
    try:
        if response['success']:
            print("\nOrder " + str(response['orderId']) + " placed.")
            return response
    except KeyError:
        pass

def Place_Trailing_Stop(token, acc_id, contract_id, side, size=1, price=None):

    url = "https://api.topstepx.com/api/Order/place"

    payload = json.dumps({
        "accountId": acc_id,
        "contractId": contract_id,
        "type": 5,
        "side": side,
        "size": size,
        "limitPrice": None,
        "stopPrice": None,
        "trailPrice": price
        })
    headers = {
        'accept': 'text/plain',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
        }

    response = ''
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response = response.json()
    except requests.exceptions.ConnectTimeout:
        return response
    
    print(response, "Trailing Stop")
    return response

def Place_Order_Task(token, acc_id, contract_id, order_type, side, size, stop_loss, take_profit):
    response = asyncio.create_task(Place_Order_Sync(token, acc_id, contract_id, order_type, side, size, stop_loss, take_profit))
    return response

#close all open orders and positions
async def Close_All_Orders_And_Postions_Sync(token, acc_id):
    url1 = "https://api.topstepx.com/api/Order/searchOpen"

    payload1 = {
    "accountId": acc_id
    }
    headers1 = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }

    async with httpx.AsyncClient() as client:
        response1 = await client.post(url1,json=payload1,headers=headers1)
    response1 = response1.json()
    
    tasklist = []

    async with asyncio.TaskGroup() as tg1:
        try:
            for i in range(len(response1['orders'])):
                tg1.create_task(cancel_order(token, acc_id,response1['orders'][i]['id']))
        except KeyError:
            pass



    url2 = "https://api.topstepx.com/api/Position/searchOpen"

    payload2 = {
    "accountId": acc_id[0]
    }
    headers2 = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }

    async with httpx.AsyncClient() as client:
        try:
            response2 = await client.post(url,json=payload,headers=headers,timeout=10)
        except httpx.ReadTimeout:
            print("The server took too long to send data. Moving to the next task...")
        except httpx.HTTPError as e:
            print(f"An HTTP error occurred: {e}")
    response2 = response2.json()
    
    for i in range(len(response2['positions'])):

        url = "https://api.topstepx.com/api/Position/closeContract"

        payload = {
        "accountId": acc_id[0],
        "contractId": response2['positions'][i]['contractId']
        }
        headers = {
        'accept': 'text/plain',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
        }

        async with httpx.AsyncClient() as client:
            response3 = await client.post(url,json=payload,headers=headers)
        response3 = response3.json()
        print("Postion " + str(response2['positions'][i]['id']) + " Closed.")

def Close_All_Orders_And_Postions(token, acc_id):
    """
    Loops through all orders and positions and closes all of said positions and orders on a given account\n

    WARNING: This makes a lot of api calls so be carful not to run over the limit using this see \n
    https://gateway.docs.projectx.com/docs/getting-started/rate-limits for your rate limits, 50 per 30s as of 30/05/2026\n

    definitions:\n

    token: session token\n
    acc_id: id of account to close all orders on\n

    """

    url1 = "https://api.topstepx.com/api/Order/searchOpen"

    payload1 = json.dumps({
    "accountId": acc_id[0]
    })
    headers1 = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }

    response1 = ''
    try:
        response1 = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response1 = response1.json()
    except requests.exceptions.ConnectTimeout:
        return response1
    
    try:
        for i in range(len(response1['orders'])):

            url = "https://api.topstepx.com/api/Order/cancel"

            payload = json.dumps({
            "accountId": acc_id[0],
            "orderId": response1['orders'][i]['id']
            })
            headers = {
            'accept': 'text/plain',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            print("Order on " + response1['orders'][i]['contractId'] + " Closed.")
    except KeyError:
        return ''

    url2 = "https://api.topstepx.com/api/Position/searchOpen"

    payload2 = json.dumps({
    "accountId": acc_id[0]
    })
    headers2 = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }

    response2 = ''
    try:
        response2 = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response2 = response2.json()
    except requests.exceptions.ConnectTimeout:
        return response2
    
    try:
        for i in range(len(response2['positions'])):

            url = "https://api.topstepx.com/api/Position/closeContract"

            payload = json.dumps({
            "accountId": acc_id[0],
            "contractId": response2['positions'][i]['contractId']
            })
            headers = {
            'accept': 'text/plain',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            response = response.json()
            print("Postion on " + response2['positions'][i]['contractId'] + " Closed.")
    except KeyError:
        return ''

def Close_All_Orders_And_Postions_Task(token, acc_id):
    response = asyncio.create_task(Close_All_Orders_And_Postions_Sync(token, acc_id))
    return response

#close just orders
async def Close_All_Orders(token, acc_id):
    
    """

    Loops through all orders and closes all of said positions and orders on a given account

    WARNING: This makes a lot of api calls so be carful not to run over the limit using this see 
    https://gateway.docs.projectx.com/docs/getting-started/rate-limits for your rate limits, 50 per 30s as of 30/05/2026

    definitions:

    token: session token
    acc_id: id of account to close all orders on

    """

    url1 = "https://api.topstepx.com/api/Order/searchOpen"

    payload1 = json.dumps({
    "accountId": acc_id
    })
    headers1 = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }

    response1 = ''
    try:
        response1 = requests.request("POST", url1, headers=headers1, data=payload1, timeout=10)
        response1 = response1.json()
        print(response1) 
    except requests.exceptions.ConnectTimeout:
        print("Orders not found")
        return ''

    
    async with asyncio.TaskGroup() as tg2:
        try:
            for i in response1['orders']:
                print("\ncancelling order", i['id'])
                tg2.create_task(cancel_order(token, acc_id, i['id']))
        except KeyError, TypeError:
            return ''   
    
async def cancel_order(token, acc_id, order_id):

    url = "https://api.topstepx.com/api/Order/cancel"

    payload = {
    "accountId": acc_id,
    "orderId": order_id
    }
    headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url,json=payload,headers=headers,timeout=10)

#get candles
async def Get_Candles_Sync(token, contract_id, live=False, unit=2, unit_num=1, limit=2, include_curr=False):
    """
    definitions:\n
    
    token: session token\n
    contract_id: Id of contract to pull bars from\n
    unit_num: number of units in the candle\n
    unit: smallest unit in the candle\n
    1 = Second\n
    2 = Minute\n
    3 = Hour\n
    4 = Day\n
    5 = Week\n
    6 = Month\n
    limit: bars to retrieve\n
    include_curr: if you want the partially done bar\n
    """

    time_now = datetime.now(timezone.utc).astimezone()
    t1 = timedelta(seconds=1)
    #set the timedelta
    if unit == 1:
        total_time = limit * (unit_num)
        t1 = timedelta(seconds=total_time)
    elif unit == 2:
        total_time = limit * (unit_num)
        t1 = timedelta(minutes=total_time)
    elif unit == 3:
        total_time = limit * (unit_num)
        t1 = timedelta(hours=total_time)
    elif unit == 4:
        total_time = limit * (unit_num)
        t1 = timedelta(days=total_time)
    elif unit == 5:
        total_time = limit * (unit_num)
        t1 = timedelta(weeks=total_time)
    elif unit == 6:
        total_time = limit * (unit_num) * 4
        t1 = timedelta(weeks=total_time)

    #compile time
    time_start = time_now - t1
    time_zone = (time_now.strftime("%z")[0] + 
                time_now.strftime("%z")[1] + 
                time_now.strftime("%z")[2] + 
                ":" + 
                time_now.strftime("%z")[3] + 
                time_now.strftime("%z")[4])
    end = time_now.strftime("%Y-%m-%d") + "T" + time_now.strftime("%T.%f") + time_zone
    start = time_start.strftime("%Y-%m-%d") + "T" + time_start.strftime("%T.%f") + time_zone

    url = "https://api.topstepx.com/api/History/retrieveBars"

    payload = {
    "contractId": contract_id,
    "live": live,
    "startTime": start,
    "endTime": end,
    "unit": unit,
    "unitNumber": unit_num,
    "limit": limit,
    "includePartialBar": include_curr
    }
    headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }
    response = ''
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url,json=payload,headers=headers,timeout=10)
            response = response.json()
        except httpx.ReadTimeout:
            print("The server took too long to send data. Moving to the next task...")
            return ''
        except httpx.HTTPError as e:
            print(f"An HTTP error occurred: {e}")
            return ''
    #print(response)

    try:
        return response['bars']
    except KeyError, TypeError:
        return None

def Get_Candles(token, contract_id, live=False, unit=2, unit_num=1, limit=2, include_curr=False):
    """
    Returns a number of candles over a given timeframe, \n
    otherwise return the previous candle before the current one\n\n

    definitions:\n\n
    
    token: session token\n
    contract_id: Id of contract to pull bars from\n
    unit_num: number of units in the candle\n
    unit: smallest unit in the candle\n
    1 = Second\n
    2 = Minute\n
    3 = Hour\n
    4 = Day\n
    5 = Week\n
    6 = Month\n
    limit: bars to retrieve\n
    include_curr: if you want the partially done bar
    """

    time_now = datetime.now(timezone.utc).astimezone()
    t1 = timedelta(seconds=1)
    #set the timedelta
    if unit == 1:
        total_time = limit * (unit_num)
        t1 = timedelta(seconds=total_time)
    elif unit == 2:
        total_time = limit * (unit_num)
        t1 = timedelta(minutes=total_time)
    elif unit == 3:
        total_time = limit * (unit_num)
        t1 = timedelta(hours=total_time)
    elif unit == 4:
        total_time = limit * (unit_num)
        t1 = timedelta(days=total_time)
    elif unit == 5:
        total_time = limit * (unit_num)
        t1 = timedelta(weeks=total_time)
    elif unit == 6:
        total_time = limit * (unit_num) * 4
        t1 = timedelta(weeks=total_time)

    #compile time
    time_start = time_now - t1
    time_zone = (time_now.strftime("%z")[0] + 
                time_now.strftime("%z")[1] + 
                time_now.strftime("%z")[2] + 
                ":" + 
                time_now.strftime("%z")[3] + 
                time_now.strftime("%z")[4])
    end = time_now.strftime("%Y-%m-%d") + "T" + time_now.strftime("%T.%f") + time_zone
    start = time_start.strftime("%Y-%m-%d") + "T" + time_start.strftime("%T.%f") + time_zone

    url = "https://api.topstepx.com/api/History/retrieveBars"

    payload = json.dumps({
    "contractId": contract_id,
    "live": live,
    "startTime": start,
    "endTime": end,
    "unit": unit,
    "unitNumber": unit_num,
    "limit": limit,
    "includePartialBar": include_curr
    })
    headers = {
    'accept': 'text/plain',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
    }

    response = ''
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response = response.json()
    except requests.exceptions.ConnectTimeout:
        return response
    #print(response)

    try:
        return response['bars']
    except KeyError:
        return ''

def Get_Candles_Task(token, contract_id, live=False, unit=2, unit_num=1, limit=2, include_curr=False):
    candles = asyncio.create_task(Get_Candles_Sync(token, contract_id, live, unit, unit_num, limit, include_curr))
    return candles

#check for open positions
def Check_Positions(token, acc_id):

    url = "https://api.topstepx.com/api/Position/searchOpen"

    payload = json.dumps({
        "accountId": acc_id
        })
    headers = {
        'accept': 'text/plain',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
        }

    response = ''
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response = response.json()
    except requests.exceptions.ConnectTimeout:
        return response
    
    try:
        return response['positions']
    except KeyError:
        pass

async def Check_Positions_Sync(token, acc_id):

    url = "https://api.topstepx.com/api/Position/searchOpen"

    payload = {
        "accountId": acc_id
        }
    headers = {
        'accept': 'text/plain',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
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
    #print(response)

    try:
        return response['positions']
    except KeyError, TypeError:
        pass

#check open orders
def Check_Orders(token, acc_id):

    url = "https://api.topstepx.com/api/Order/searchOpen"

    payload = json.dumps({
        "accountId": acc_id
        })
    headers = {
        'accept': 'text/plain',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
        }

    response = ''
    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response = response.json()
    except requests.exceptions.ConnectTimeout:
        return response

    try:
        return response['orders']
    except KeyError:
        pass

async def Check_Orders_Sync(token, acc_id):

    url = "https://api.topstepx.com/api/Order/searchOpen"

    payload = json.dumps({
        "accountId": acc_id
        })
    headers = {
        'accept': 'text/plain',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
        }


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
        return response['orders']
    except KeyError:
        return ''

#test all calls to see if they all run (only tests on practice accounts)
async def test_calls():
    #load dotenv
    load_dotenv(find_dotenv(filename="APIKEY.env",raise_error_if_not_found=True))

    #key and username
    key = os.getenv("apiKey")
    usrnme = os.getenv("Email")
    #print(key, usrnme)

    #session token and accounts
    token = await Get_Token_Sync(key,usrnme)
    accounts = Get_Accounts(token)
    account = []

    #only test on practice accounts dumbass
    for i in accounts:
        if i[1].__contains__("PRAC"):
            account.append(i)
            print(i)

    #test contract search with NQ
    Id_NQ = Get_ID_Sync(token, "ENQ")
    Id_ES = Get_ID_Sync(token, "EP")
    Ids = await asyncio.gather(Id_NQ, Id_ES)
    Id_NQ = Ids[0]
    Id_ES = Ids[1]
    print("\n" + Id_NQ['id'])
    print("\n" + Id_ES['id'])

    #test place and close positions and orders if you want
    #Place_Order(token=token,acc_id=account[0],contract_id=Id_NQ,order_type=2,side=0,size=1)
    #await Close_All_Orders_And_Postions_Sync(token,account[0])
    #await Check_Positions_Sync(token=token,acc_id=account[0][0])

    #test multi orders and full cancellation
    async with asyncio.TaskGroup() as tg1:
        for i in range(5):
            tg1.create_task(Place_Order_Sync(token, account[0][0], Id_NQ['id'], 1, 0, 1, price=i))
    
    #full cancellation
    Place_Trailing_Stop(token, account[0][0], Id_NQ['id'], 0 ,price=10)
    await Close_All_Orders(token, account[0][0])

    #get bars on NQ (also check your getting candles)
    candles = Get_Candles(token,Id_NQ['id'],False,2,5,100,True)
    for i in range(len(candles)):
        print(str(i) + ". " + str(candles[i]['c']))

async def Ping_test():
    start = datetime.now()
    bool = await Ping()
    end = datetime.now()
    delta = end - start
    print(bool,str(delta))

    

#asyncio.run(test_calls()) #test all calls
#asyncio.run(Ping_test())