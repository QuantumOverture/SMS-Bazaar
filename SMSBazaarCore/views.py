from django.shortcuts import render
from django.http import HttpResponse
from twilio.rest import Client



def index(request):
    if request.method == 'GET':
        return HttpResponse("Go away.")
    elif request.method == 'POST':
        account_sid = 'AC3dfc80e02f7e984afb857ba4900a0fcd'
        auth_token = 'e36aab7c7237ee2c0e149f2de034c944'
        client = Client(account_sid, auth_token)
        message = client.messages \
            .create(
                body=str(request.body),
                from_='+18772579727',
                to='+14156906522'
            )
        print(message.sid)