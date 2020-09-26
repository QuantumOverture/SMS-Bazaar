from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from twilio.twiml.messaging_response import Message, MessagingResponse
import json
import datetime
import re

def DictParse(POSTString):
    """
    Dict Format:
    {'SmsMessageSid': 'SM5f4fe87cab971ed997b9dcfd0babfb5b', 'NumMedia': '0', 'SmsSid': 'SM5f4fe87cab971ed997b9dcfd0babfb5b',
     'SmsStatus': 'received', 'Body': 'M', 'To': '+14155238886', 'NumSegments': '1',
    'MessageSid': 'SM5f4fe87cab971ed997b9dcfd0babfb5b', 'AccountSid': 'ACce87bd19e386f76c3ac5b8412d1c9b26',
     'From': '+14156906522', 'ApiVersion': "2010-04-01'"}
    """
    POSTString = POSTString[2:]
    Response = POSTString.split("&")
    Response_DICT = {}
    for i in Response:
        Response_DICT[i[:i.index("=")]] = i[i.index("=") + 1:].replace("%2B", "+").replace("whatsapp%3A","")
    return Response_DICT



@csrf_exempt
def index(request):
    if request.method == 'GET':
        return HttpResponse("Go away.")
    elif request.method == 'POST':
        Response_DICT = DictParse(str(request.body))
        # Start our TwiML response
        resp = MessagingResponse()
        # Add a message
        resp.message("Message Received! Current Time Received: "+str(datetime.datetime.now()))

        return HttpResponse(str(resp))