from binance.client import Client
from binance.enums import *
import math
import sys
import string
from twilio_handler import sms_send
from config import *


API_KEY = BINANCE_API_KEY
SEC_KEY = BINANCE_SEC_KEY

# instantiate BinaceUS client, 
# if you are using Binance and not BinanceUS
# then remove the tld arguement
client = Client(API_KEY, SEC_KEY, tld='us')


def get_buy_quantity(symbol_stripped, symbol_tokens):
    global client
    last = client.get_symbol_ticker(symbol = symbol_stripped)
    last = float(last['price'])
    balance = client.get_asset_balance(symbol_tokens[1])
    balance = float(balance['free'])
    coin_size = str(last).split('.')
    coin_size = len(coin_size[0])
    # .9 to account for slippage and rounding errors. 
    quantity = (balance / last) * .9
    if(coin_size - 1) == 0:
        quantity = round(quantity) 
    else:
       quantity = round(quantity, coin_size-1) 
    return quantity



def get_sell_quantity(symbol_stripped, symbol_tokens):
    balanceS = client.get_asset_balance(symbol_tokens[0])
    balanceS = balanceS['free']
    balanceS = float(balanceS) 
    print(balanceS)
    last = client.get_symbol_ticker(symbol = symbol_stripped)
    last = float(last['price'])
    coin_size = str(last).split('.')
    coin_size = len(coin_size[0])
    print(coin_size)

    if coin_size == 1:
        balanceS = math.floor(balanceS)

    elif coin_size <= 3:
        coin_size -= 1
        n = 10**coin_size
        balanceS = math.floor(balanceS*n)/n


    elif int(coin_size) > 3:
        coin_size += 1
        print(coin_size)
        n = 10**coin_size
        balanceS = math.floor(balanceS*n)/n

    return balanceS



def buy_order(symbol_stripped, symbol_tokens):
    global client
    quantity = get_buy_quantity(symbol_stripped, symbol_tokens)
    try:
        
        order = client.create_order(symbol=symbol_stripped, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=quantity)
        price = order['fills'][0]['price']
        msg = "bought in at price %s " % str(price)
        sms_send(msg)
        return(order['fills'][0]['price'])

    except Exception as e:
        sms_send("an exception occured in buy order - {}".format(e))
        return False
    


def sell_limit(symbol_stripped, symbol_tokens, percent_take, price):
    quantity = get_sell_quantity(symbol_stripped, symbol_tokens)
    price += price*percent_take
    price = (f'{price:.6f}')
    print (price)
    print(quantity)
    try:
        order = client.create_order(
                symbol = symbol_stripped, 
                side = SIDE_SELL, 
                type = ORDER_TYPE_LIMIT, 
                timeInForce = TIME_IN_FORCE_GTC, 
                quantity = quantity, 
                price = price)
    except Exception as e:
        sms_send("an exception occured in sell limit order- {}".format(e))
        return False
    return order
    


def stop_limit_order(symbol_stripped, symbol_tokens, price, percent_take): 
    price = float(price)*float(percent_take)
    quantity = client.get_asset_balance(symbol_tokens[1])
    stopPrice = price - price*.06
    try:
        #print("sending order")
        sms_send("sending order")
        order = client.create_order(
            symbol = symbol_stripped, 
            side = SIDE_BUY, 
            type = ORDER_TYPE_STOP_LOSS_LIMIT, 
            timeInForce = TIME_IN_FORCE_GTC, 
            quantity = quantity, 
            price = price, 
            stopPrice = stopPrice)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False    
    return True



def cancel_and_close(symbol_stripped, symbol_tokens):
    global client
    client._delete('openOrders', True, data={'symbol': symbol_stripped})
    balance = get_sell_quantity(symbol_stripped, symbol_tokens)
    #balance = float(balance['free'])
    try:
        #print("sending order")
        sms_send("sending order")
        if len(client.get_open_orders()) == 0:
            order = client.create_order(symbol=symbol_stripped, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=balance)
        print(order)
    except Exception as e:
        #print("an exception occured - {}".format(e))
        sms_send("an exception occured - {}".format(e))
        return False

    sms_send('stop loss triggered at %s' % order['fills'][0]['price'])    
    return True



    
