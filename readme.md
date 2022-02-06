Crypto Trading Bot
*************************
@author Cameron Zuziak

DESCRIPTION: This is a crypto trading bot that trades crypto currency based off RSI. 
The user can set certain thresholds, such as the RSI buy in level, percent stop loss, and percent take.
Once RSI dips below a buy threshold, the bot will wait for a retracement in RSI to enter a position.
When a the bot enters a postion with a succesful market buy order, it will immeadiately submit a limit
sell order at a set percentage price above the entry price.
*************************

Set Up: 

1. Binance Account:
  This program requires a Binance or BinanceUS account, as well as associated API keys. 
  Setting up an account on either platform is fairly straight forward. Information on creating binance
  API keys can be found at https://www.binance.com/en/support/faq/360002502072 
  Once API keys are generated, paste them into the config file, or set them up 
  as environment variables (this will require editing binance_handler.py to reflect this change). 
  
2. Twilio Account:
  In order to recieve text message updates on trades, this program utilizes the Twilio API. 
  You can set a free account at Twilio.com and generate a phone number and account tokens on the website.
  For more information on this process see https://www.twilio.com/docs/iam/keys/api-key 
  Add API information and Twilio phone number to their respective variables in the config file. 
  
3. Optional step is to set up a virtual environment.  
        python3 -m venv venv
   activate the environment in MacOS/Linux with:
        source venv/bin/activate
   and on windows:
        ./venv/Scripts/activate
  
4. TA-Lib
  Installing TA-lib can be a bit tricky depending on what OS you are on. For instructions on installing TA-Lib
  see https://github.com/mrjbq7/ta-lib 
  
  
5. Install requirements. 
    pip3 install -r requirements.txt
  
6. Set variables in bot.py:

  symbol = "VET/USDT"     # Defualt is Vechain. This is your coinpairing to be traded, 
                          # represented as the asset ticker then '/' and then the denomination.
                        
  RSI_BUY = 30            # This is the RSI threshold for entering a position

  STOP_LOSS_PERCENT = .02 # Percentage in price change to trigger stop loss, default 2 percent.

  PROFIT_TAKE = .01       # This is the profit take percentage, when in a position, the bot will exit 
                          # exit the position at 1% profit. Change accordingly. 
  
7. Run bot
  python3 bot.py
