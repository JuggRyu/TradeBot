from turtle import position
import ccxt
import hmac
import time
import json
import pandas as pd
import hashlib
import settings
import requests
from pprint import pprint
from datetime import datetime
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError


position_amount = 0         # current position amount
position_side  = ''        # BUY or SELL
order_list = []         
orderid_list = []      
position_counts_list = list[range(1,8)]
start = time.time()
symbol = "ADAUSDT"
position_amount=[6,12,18,30,48,78,126,204]
position_range_1_4 = 0.01 
position_range_5_6 = 0.0175
position_range_7_7 = 0.0236
position_range_8_8 = 0.0236
error_count = 0
binance_api_key = settings.binance_api_key
binance_api_secret = settings.binance_api_secret
line_user_id = settings.line_user_id
dt_now = datetime.now()
position_close_timing=[0,position_range_1_4*3,position_range_1_4*1.1,position_range_1_4/2,position_range_1_4*2,position_range_1_4*3,position_range_1_4*4.1,position_range_1_4*6]
line_bot_api = LineBotApi(settings.access_token)
def line_send_message_start(str1,price1):
    global line_bot_api
    global line_user_id
    linesendtext = str1 + price1
    line_bot_api.push_message(line_user_id, TextSendMessage(text=linesendtext))  

line_send_message_start("--------------","-----------------")

while True:# loop task infinite
    try:
        check_profit_count()
        check_position_amount()
        time.sleep(20)# waiting 1 second
        error_count = 0
    except Exception as e:
        # when error push notification line
        error_count += 1
        if error_count >= 5:#when 5 errors then stop
            break
        else:
            pass
            print(e)
            print('PASS')

    def check_profit_count():#calc profit
        global position_side
        global position_close_timing
        global position_amount
        global order_list
        global position_side

        print("profit calculating...")

        now_price = get_last_trade_price(symbol)#ADA/USDT recently price
        multiple_plusorminus = 0
        multiple_plusorminus_position_close_timing = 0

        if position_side == 'BUY':
            multiple_plusorminus = -1
            multiple_plusorminus_position_close_timing = 1
        elif position_side =='SELL':
            multiple_plusorminus = 1
            multiple_plusorminus_position_close_timing = -1

        for position_counts in position_counts_list():

            if position_amount == position_counts and multiple_plusorminus*(now_price - (order_list[0]+multiple_plusorminus_position_close_timing*position_close_timing[position_counts])) <= 0:
                line_send_message("価格差(初期エントリーと現在の値段)　",str(multiple_plusorminus*(now_price-order_list[0])))
                line_send_message("ADA/USDT  現在価格　　　　　　　"+position_side+" ",str(now_price))
                line_send_message("ADA/USDT初期エントリー価格　　"+position_side+" ",str(order_list[0]))
                loss_cut("利確数量　"+position_side+" ")
                all_init()
            else:
                pass

    def check_position_amount():# order or not
        global position_amount
        global position_amount
        global order_list
        global position_side
        global position_range_1_4
        global position_range_5_6
        global position_range_7_7
        global position_range_8_8
        now_price = get_last_trade_price(symbol)#ADA/USDT show current price
        multiple_plusorminus = 0
        if position_side == 'BUY':
            multiple_plusorminus = 1
            multiple_plusorminus_position_close_timing = -1
        elif position_side =='SELL':
            multiple_plusorminus = -1
            multiple_plusorminus_position_close_timing = 1

        print("ポジション数と価格差を見て、エントリーor損切判断")
        if position_amount == 0:                      
            position_side = get_position_status()   #(BUYorSELL)
            binance_get_position_ADAUSDT(position_side,position_amount[0]) 
        elif 1 <= position_amount <= 4 and multiple_plusorminus*(now_price - (order_list[-1]+multiple_plusorminus_position_close_timing*position_range_1_4)) <= 0:   #ポジション数1~4回&rangeを超えた時
            line_send_message("価格差(最後のエントリーと現在の値段)　",str(multiple_plusorminus*(now_price - order_list[-1])))
            line_send_message("ADA/USDT現在価格　　　　　　　"+position_side+" ",str(now_price))
            line_send_message("ADA/USDT最後のエントリー価格　　"+position_side+" ",str(order_list[-1]))
            binance_get_position_ADAUSDT(position_side,position_amount[position_amount]) 
        elif 5 <= position_amount <= 6 and multiple_plusorminus*(now_price - (order_list[-1]+multiple_plusorminus_position_close_timing*position_range_5_6)) <= 0: #ポジション数5~6回&rangeを超えた時
            line_send_message("価格差(最後のエントリーと現在の値段)　",str(multiple_plusorminus*(now_price - order_list[-1])))
            line_send_message("ADA/USDT現在価格　　　　　　　　"+position_side+" ",str(now_price))
            line_send_message("ADA/USDT最後のエントリー価格　　"+position_side+" ",str(order_list[-1]))
            binance_get_position_ADAUSDT(position_side,position_amount[position_amount]) 
        elif position_amount == 7 and multiple_plusorminus*(now_price - (order_list[-1]+multiple_plusorminus_position_close_timing*position_range_7_7)) <= 0:      #ポジション数  7回&rangeを超えた時
            line_send_message("価格差(最後のエントリーと現在の値段)　",str(multiple_plusorminus*(now_price - order_list[-1])))
            line_send_message("ADA/USDT現在価格　　　　　　　　"+position_side+" ",str(now_price))
            line_send_message("ADA/USDT最後のエントリー価格　　"+position_side+" ",str(order_list[-1]))
            binance_get_position_ADAUSDT(position_side,position_amount[position_amount]) 
        elif position_amount == 8 and multiple_plusorminus*(now_price - (order_list[-1]+multiple_plusorminus_position_close_timing*position_range_8_8)) <= 0:      #ポジション数  8回&rangeを超えた時
            line_send_message("価格差(最後のエントリーと現在の値段)　",str(multiple_plusorminus*(now_price - order_list[-1])))
            line_send_message("ADA/USDT現在価格　　　　　　　　"+position_side+" ",str(now_price))
            line_send_message("ADA/USDT最後のエントリー価格　　"+position_side+" ",str(order_list[-1]))
            loss_cut("損切数量　")#all loss cut
            all_init()#intialize
        else:
            print('step2 has not additional order')
            print('current position amount is' + str(position_amount))

    def line_send_message(str1,price1):
        global line_bot_api
        global line_user_id
        linesendtext = str1 + price1
        line_bot_api.push_message(line_user_id, TextSendMessage(text=linesendtext))  
            
    def all_init():
        print("reset parameters")
        global position_amount
        global position_side
        global order_list
        global orderid_list
        position_amount = 0         #current position amount
        position_side  = ''        #bid or ask
        order_list = []         # entry price
        orderid_list = []      # position ID

    def every_1hour_adajpy_price(period):
        response = requests.get("https://api.cryptowat.ch/markets/binance/adausdt/ohlc?periods=3600")
        response = response.json()
        pricelist = []
        for i in range(2,int(period)+2):
            data = response["result"]["3600"][i*(-1)]    
            pricelist.append(data[4])

        return pricelist

    def binance_get_position_ADAUSDT(position_side,amount):
        global position_amount
        global dt_now
        print("ADA/USDT ENTRY")
        binance = ccxt.binance({
            'enableRateLimit': True,  # unified exchange property
            'rateLimit': 250,
            'apiKey': str(binance_api_key),
            'secret': str(binance_api_secret),
        })
        binance.options = {'defaultType': 'future', 'adjustForTimeDifference': True,'defaultTimeInForce':False}
        order = binance.create_order('ADAUSDT', 'MARKET', position_side, amount, None)
        position_amount = position_amount + 1
        orderid_list.append(order['id'])
        order_list.append(float(order['price']))
        line_send_message("time stamp　　　 ",str(dt_now))
        line_send_message("ADA/USDT購入　　　　"+position_side+" ",str(order['price']))
        line_send_message("ADA/USDT購入数量　　"+position_side+" ",str(amount))
        line_send_message("現在のポジション数 "+position_side+" ",str(position_amount))
        line_send_message("--------------","-----------------")

        return order

    def get_last_trade_price(symbol):
        print("価格取得")
        exchange = ccxt.binance()
        tiker = exchange.fetch_ticker(symbol)
        print(float(tiker['last']))
        last_price = float(tiker['last'])
        
        return last_price

    def get_position_status():
        print("calculating EMA")
        # calculate EMA
        SMA007 = every_1hour_adajpy_price(8)
        sum007 = sum(SMA007[0:7])
        count_1hour_007 = float(sum007/7)
        after_count_2hour_007 = count_1hour_007+(float(2/8))*(SMA007[1]-count_1hour_007)
        line_send_message("EMA=7　",str(count_1hour_007))

        # calculate EMA
        SMA014 = every_1hour_adajpy_price(14)
        sum014 = sum(SMA014[0:14])
        count_1hour_014 = float(sum014/14)
        after_count_2hour_014 = count_1hour_014+(float(2/15))*(SMA014[1]-count_1hour_014)
        line_send_message("EMA=14　",str(count_1hour_014))
        if (count_1hour_007 - count_1hour_014) < 0:
            return 'SELL'
        else:
            return 'BUY'

    def loss_cut(line_send_message_str):#loss_cut definition
        global position_side
        global position_amount
        binance = ccxt.binance({
            'enableRateLimit': True,  # unified exchange property
            'rateLimit': 250,
            'apiKey': str(binance_api_key),
            'secret': str(binance_api_secret),
        })

        binance.options = {
            'defaultType': 'future', 
            'adjustForTimeDifference': True,
            'defaultTimeInForce':False
        }
        #order = binance.cancelAllOrders('ADAUSDT')
        if position_side=="BUY":
            now_get_position_count = sum(position_amount[0:position_amount])
            order = binance.create_order('ADAUSDT', 'MARKET', "SELL", now_get_position_count, None)
            line_send_message(line_send_message_str,str(now_get_position_count))
        elif position_side=="SELL":
            now_get_position_count = sum(position_amount[0:position_amount])
            order = binance.create_order('ADAUSDT', 'MARKET', "BUY", now_get_position_count, None)
            line_send_message(line_send_message_str,str(now_get_position_count))
