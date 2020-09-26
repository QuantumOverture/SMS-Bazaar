from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from twilio.twiml.messaging_response import Message, MessagingResponse


@csrf_exempt
def index(request):
    if request.method == 'GET':
        return HttpResponse("Go away.")
    elif request.method == 'POST':
        """account_sid = 'AC3dfc80e02f7e984afb857ba4900a0fcd'
        auth_token = '22a099b9d4f38e33c1b3bb12b6a9e3b9'
        client = Client(account_sid, auth_token)
        message = client.messages \
            .create(
                body=str(request.body),
                from_='+18772579727',
                to='+14156906522'
            )
        print(message.sid)"""
        """Respond to incoming calls with a simple text message."""
        # Start our TwiML response
        resp = MessagingResponse()

        # Add a message
        resp.message("The Robots are coming! Head for the hills!")

        return HttpResponse(str(resp))