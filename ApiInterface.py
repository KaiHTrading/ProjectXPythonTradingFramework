import requests
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv, find_dotenv
import asyncio
import httpx
import os
from apicall import *

class ApiInterface:

    def __init__(self, str="APIKEY.env"):

        #load dotenv
        load_dotenv(find_dotenv(filename=str,raise_error_if_not_found=True))

        #key and username
        self.key = os.getenv("apiKey")
        self.email = os.getenv("Email")
        self.token = ''

        while self.token == '':
            self.token = Get_Token(self.key, self.email)

    def __int__(self): #who the hell would do this

        return 0
    
    def __str__(self):

        return "Email: " + str(self.email) + " Last 10 characters of token: " + self.token[-10:]
    
    def __bool__(self):
        
        headers = json.dumps({
            'accept': 'text/plain',
            })

        response = requests.get("https://api.topstepx.com/api/Status/ping",headers=headers)

        return response.text == "pong"
    
    def RefreshToken(self):

        self.token = ''

        while self.token == '':
            self.token = Get_Token(self.key, self.email)

    async def Ping():

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

    