from twilio.rest import Client
import os
from config import *

account_sid = TWILIO_ACCOUNT
account_token = TWILIO_TOKEN
twill_client = Client(account_sid, account_token)

def sms_send(text):
    message = twill_client.messages \
                    .create(
                        body=text,
                        from_= TWILIO_NUMBER,
                        to='+19496834700'
                    )
    #print(message.sid)

