from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from twilio.twiml.messaging_response import Message, MessagingResponse
import json
import datetime
import re

from SMSBazaarCore.bankcalls import *
from .models import Nonuser, Scratch, Item


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
        Response_DICT[i[:i.index("=")]] = i[i.index("=") + 1:].replace("%2B", "+").replace("whatsapp%3A", "")
    return Response_DICT


@csrf_exempt
def index(request):
    if request.method == 'GET':
        return HttpResponse("Go away.")
    elif request.method == 'POST':
        Response_DICT = DictParse(str(request.body))
        """

        'buy' -> customer enters buy "item" "city" "directions to address" -> we give list of such items and their descriptions in their city, they choose an item by entering buy "item" # from list
        'sell' -> vendor enters sell "item" "description" "city" "directions to address" "amount for delivery person" "amount of item-> gets sent to database of the specific item class and city
        'setupdeliv' -> person sets their city and gets list of possible deliveries they can make and they choose where to go -> they choose an item by entering buy "item" # from list

        vendor cancel -> resets customer address and number in database doesn't work once okay_deliv == TRUE
        'deposit' -> 'deposit' code -> checks code and deposits money into account


        'okay_deliv' -> delivery person enters this when they accept their item => check occurs here
        once all three are sent out -> then release the transfer of money :
            * money from customer go to vendor
            * vendor money go to delivery

        Database:  
        *  [set to nulls]okay_deliv_done_or_not/City[Vendor]/Item[Vendor]/WhatsAppNumber[Vendor]/Description[Vendor]/[ both addresss and number intialized to be null->changes when customer decides to buy -> Customer Address] &Customer number[Customer]/Vendor Address[Vendor]/price of item[Vendor]/price of delivery[Vendor] database => for buy and sell
        *  Scratch Code/Amount database-> for deposit command

        * generate scratch codes 

        """
        resp = MessagingResponse()
        if CheckIfCustomerByNum(Response_DICT['From']):
            Body_List = re.split('\++', Response_DICT["Body"].strip("+"))
            if Body_List[0].lower() == "balance":
                resp.message("Your balance is " + str(CheckBalance(Response_DICT)) + " PKR.")
            elif Body_List[0].lower() == "transfer":
                if "whatsapp" not in str(request.body):
                    resp.message("You cannot initiate transfers by SMS. Kindly use WhatsApp")
                elif len(Body_List) == 3:
                    try:
                        Amount = int(Body_List[2])
                    except ValueError:
                        resp.message("The amount you entered is not a number. Kindly try again.")
                        return HttpResponse(str(resp))
                    message = TransferFunds("+" + Body_List[1], Response_DICT, Amount)
                    if message == "Insufficient Funds :(":
                        resp.message("You have insufficient funds for this transaction.")
                    elif message == "Payee not found":
                        resp.message("There is no associated account with the number you provided.")
                    elif message == "zero":
                        resp.message("Amount must be greater than zero.")
                    else:
                        resp.message("The transaction was successful!")
                else:
                    resp.message("Usage: Transfer ToNumber Amount")
            elif Body_List[0].lower() == "scratch":
                if "whatsapp" not in str(request.body):
                    resp.message("You cannot claim scratchcard codes by SMS. Kindly use WhatsApp")
                elif len(Body_List) == 2:
                    try:
                        s = Scratch.objects.get(pk=Body_List[1])
                    except Scratch.DoesNotExist:
                        resp.message("Code failed.")
                        return HttpResponse(str(resp))
                    DepositScratchCardCode(Response_DICT, s.amount)
                    resp.message(str(s.amount) + " PKR were deposited into your account.")
                    s.delete()
                else:
                    resp.message("Usage: Scratch XXXXXXXXXX")
            elif Body_List[0].lower() == "sell":
                if "whatsapp" not in str(request.body):
                    resp.message("You cannot initiate transfers by SMS. Kindly use WhatsApp")
                else:
                    Sell_List = re.split('\+*%7C\+*', Response_DICT["Body"].strip("+"))
                    if len(Sell_List) != 6:
                        resp.message("Usage: Sell | Item Name | Item Description | City Where Product is Based | "
                                     + "Address Where Product is Based | Price'")
                        resp.message(str(Sell_List))
                    else:
                        try:
                            n = Item.objects.get(pk=Sell_List[1])
                            resp.message("Sorry the product name already exits.")
                        except:
                            n = Item(item_name=Sell_List[1], description=Sell_List[2], city=Sell_List[3],
                                     address=Sell_List[4], price=int(Sell_List[5]),
                                     vendor_ph_num=Response_DICT["From"])
                            n.save()
                            resp.message("Your product was successfully uploaded to SMS Bazaar")
            elif Body_List[0].lower() == 'buy':
                if "whatsapp" not in str(request.body):
                    resp.message("You cannot initiate transfers by SMS. Kindly use WhatsApp")
                else:
                    Buy_List = re.split('\+*%7C\+*', Response_DICT["Body"].strip("+"))
                    resp.message(str(Item.objects.filter(item_name__icontains=Buy_List[1], city__icontains=Buy_List[2]))[18:-3].replace('<Item: ', '').replace('>,', '\n').replace('+', ' ').replace('%27', "'"))
            else:
                resp.message("Available commands are Balance, Transfer, Scratch, and Sell.")

            # 1) Check if their commands is part of our lexicon
            # 2) Execute the command
            # 3) Tell user that command was successfuly recieved
        else:
            try:
                n = Nonuser.objects.get(pk=Response_DICT["From"])
            except Nonuser.DoesNotExist:
                n = Nonuser(phone_number=Response_DICT["From"])
                n.save()
                resp.message("Do you want to create an account? (reply yes/no)")
                return HttpResponse(str(resp))
            if Response_DICT["Body"].lower().strip() == "yes":
                BankID = CreateCustomerAndAccount(Response_DICT)
                resp = MessagingResponse()
                if BankID != "ACCOUNT ERROR" or BankID != "CUSTOMER CREATION ERROR":
                    resp.message("Your account was successfully created!")
                else:
                    resp.message("There was an error creating your account. Kindly call our helpline.")
            else:
                resp.message("Your account was not created. Kindly send another message if you wanted "
                             + "to create an account. Be sure to reply only 'yes' when asked to do so.")
            n.delete()
            # send menu/help command list
        return HttpResponse(str(resp))
        # Start our TwiML response
        resp = MessagingResponse()
        # Add a message
        resp.message("Message Received! Current Time Received: " + str(datetime.datetime.now()))

        return HttpResponse(str(resp))
