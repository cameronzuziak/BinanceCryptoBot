import websocket, json, pprint, talib, numpy
import twilio_handler
import binance_handler
import datetime
import math
import sys

# adjust coin pairing as desired. 
symbol = "VET/USDT"
symbol_stripped = str(symbol).replace('/','')
symbol_tokens = symbol.split('/')
# The socket streams 1min candles, if you desire a different candle period, 
# change kline_1m to kline_3m, kline_5m, or kline_15m
SOCKET = "wss://stream.binance.com:9443/ws/%s@kline_1m" % symbol_stripped.lower() 
PERIOD = 14
RSI_BUY = 30
closes =[]
entry_price = 0
in_position = False

# dont adjust this value for stop loss
stop_loss = 0

# adjust below value to percentage stop loss you desire. 
# default is 2 percent
STOP_LOSS_PERCENT = .02

# adjust below for given profit percent take
# default is 1 percent take
PROFIT_TAKE = .01


# on websocket connection, text user that websocket stream is open
def on_open(ws):
    print("socket open")
    twilio_handler.sms_send("socket open")


# Method for TA analysis / trade logic on every message received
def on_message(ws, message):
    global entry_price
    global stop_loss
    global in_position
    json_message = json.loads(message)
    candle = json_message['k']
    candle_closed = candle['x']
    close = candle['c']
    last = candle['l']

    # check stop loss
    if in_position:
        # if price below stop loss, then exit and close open orders
        if float(last) <= stop_loss:
            # exit with market sell
            binance_handler.cancel_and_close(symbol_stripped, symbol_tokens)
            in_position = False

    # on candle close, calculate RSI and check for buy conditions
    if candle_closed:
        closes.append(float(close))

        # check if number of candles is enough to calculate RSI
        # if so, calculate RSI
        if len(closes) > PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, PERIOD)
            last_rsi = rsi[-1]
            prev_rsi = rsi[-2]
            print(last_rsi)

            #check if RSI is below entry threshold
            if last_rsi < RSI_BUY or prev_rsi < RSI_BUY:
                # see if you are already in position by
                # checking if your limit sell was filled or not
                if len(binance_handler.client.get_open_orders()) == 0:
                    in_position = False
                # check for retracement in RSI 
                if not in_position and last_rsi > prev_rsi:
                    # send buy order
                    x = binance_handler.buy_order(symbol_stripped, symbol_tokens)
                    # if market buy order succesful, send limit sell given take profit percentage
                    if not x == False:
                        entry_price = float(x)
                        # set stop loss
                        stop_loss = entry_price - entry_price*STOP_LOSS_PERCENT
                        binance_handler.sell_limit(symbol_stripped, symbol_tokens, PROFIT_TAKE, entry_price)
                        in_position = True
                    else:
                        twilio_handler.sms_send("uknown error occured")


def on_close(ws):
    print("socket closed")
    twilio_handler.sms_send("Socket Closed")

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
