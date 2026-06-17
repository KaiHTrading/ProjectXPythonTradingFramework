"""
Simple SMA crossover strategy for testing:
"""

from TradingStrategy import *

def SMA(candles: list[dict], length: int, offset: int = 0):
    total: float
    try:
        total = sum([candles[i]['c'] for i in range(offset, length+offset)], start=0.0)
        return float(total)
    except IndexError, TypeError:
        print("Index is out of range.")
        return 0.0

Sma_Fast = 0.0
Sma_Slow = 0.0
api_up = False

async def calc(candles: Chart, slow: int, fast: int): #make your calculation loop here (ohlc features and whatnot)
    
    global Sma_Slow
    global Sma_Fast
    Sma_Slow = SMA(candles.data,slow)
    Sma_Fast = SMA(candles.data,fast)

def set_api_f():

    return set_api_up()

async def set_api_up():

    global api_up
    api_up = await Ping() 

SMA_Crossover = Strategy("Sma Crossover")
print(SMA_Crossover) #check for the token to not be blank (connection is established)
SMA_Crossover.set_primary(name="PRAC") # set your primary account(you can copy the name or use the index you find from the print)
SMA_Crossover.add_data("Nasdaq 100 E-Mini","ENQ","s",15,300) #add candle data
NQ: Chart
NQ = SMA_Crossover.data[0][1]

#setup long and short conditions
dir = 0 if Sma_Fast > Sma_Slow else 1

#setup tasks required for job
SMA_Crossover.add_structured_task("Candle call",
                                  NQ.UpdateDataFactory,
                                  0.25)

SMA_Crossover.add_scheduled_task("Calc",
                                 calc,
                                 8,
                                 data=[NQ,14,9] )

SMA_Crossover.add_scheduled_task("Pos Update",
                                 SMA_Crossover.management.UpdatePositionsFactory,
                                 4)

SMA_Crossover.add_scheduled_task("Close Pos in oppsite direction",
                                 SMA_Crossover.ClosePosition,
                                 8,
                                 dir+1!=SMA_Crossover.management.FindPosition,
                                 data=tuple(NQ.con_id))

SMA_Crossover.add_scheduled_task("Ping API",
                                 set_api_f,
                                 15)

print(SMA_Crossover)

run_command = SMA_Crossover.run()

SMA_Crossover.loop.run_until_complete(run_command)
