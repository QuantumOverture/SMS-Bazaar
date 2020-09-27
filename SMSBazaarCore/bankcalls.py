import requests
import json
from random import randint

"""
Message_Dict = {'SmsMessageSid': 'SM5f4fe87cab971ed997b9dcfd0babfb5b', 'NumMedia': '0',
                'SmsSid': 'SM5f4fe87cab971ed997b9dcfd0babfb5b',
                'SmsStatus': 'received', 'Body': 'M', 'To': '+14155238886', 'NumSegments': '1',
                'MessageSid': 'SM5f4fe87cab971ed997b9dcfd0babfb5b', 'AccountSid': 'ACce87bd19e386f76c3ac5b8412d1c9b26',
                'From': '+14156906522', 'ApiVersion': "2010-04-01'"}
"""
apiKey = ""

"""
* The first name field for customers is their number
* Each number/customer gets one savings account
* Savings account is asscociated with the number
* If user wants to make account -> ask them for city
* Notify system that you want to be a delivery person, you will get a response/message when someone in your area wants to buy something from a someone else
* Once delivery person  -> funds are released to everyone
* Customer's balance is checked before placing an order
"""


def CheckIfCustomer(Message_Dict):
    url = "http://api.reimaginebanking.com/customers?key={}".format(apiKey)
    Result = json.loads(requests.get(url).text)
    for i in Result:
        if i["first_name"] == Message_Dict["From"]:
            return True
    return False

# Number is string, e.g "+14156906522"
def CheckIfCustomerByNum(Number):
    url = "http://api.reimaginebanking.com/customers?key={}".format(apiKey)
    Result = json.loads(requests.get(url).text)
    for i in Result:
        if i["first_name"] == Number:
            return True
    return False

# Gives you account number associated with a number
def GetAccountNumber(Message_Dict):
    if CheckIfCustomer(Message_Dict):
        url = "http://api.reimaginebanking.com/customers?key={}".format(apiKey)
        Result = json.loads(requests.get(url).text)
        for i in Result:
            if i["first_name"] == Message_Dict["From"]:
                url = "http://api.reimaginebanking.com/customers/{}/accounts?key={}".format(i["_id"], apiKey)
                Result = json.loads(requests.get(url).text)[0]
                return Result["_id"]
    else:
        return "ERROR IN CHECK CUSTOMER"

# Gives you account number associated with a number but this you give a string phone number
def GetAccountNumberFromNumber(Number):
    if CheckIfCustomerByNum(Number):
        url = "http://api.reimaginebanking.com/customers?key={}".format(apiKey)
        Result = json.loads(requests.get(url).text)
        for i in Result:
            if i["first_name"] == Number:
                url = "http://api.reimaginebanking.com/customers/{}/accounts?key={}".format(i["_id"], apiKey)
                Result = json.loads(requests.get(url).text)[0]
                return Result["_id"]
    else:
        return "ERROR IN CHECK CUSTOMER"


def CreateCustomerAndAccount(Message_Dict):
    url = "http://api.reimaginebanking.com/customers?key={}".format(apiKey)
    CustomerInfo = {
        "first_name": Message_Dict['From'],
        "last_name": "NA",
        "address":
            {
                "street_number": "NA",
                "street_name": "NA",
                "city": "NA",
                "state": "NA",
                "zip": "12345"
            }

    }

    response = requests.post(
        url,
        data=json.dumps(CustomerInfo),
        headers={'content-type': 'application/json'},
    )
    if response.status_code == 201:
        CustomerNumberID = Message_Dict['From']
        NewID = json.loads(response.text)['objectCreated']['_id']
        NewAccount = {
            "type": "Savings",
            "nickname": CustomerNumberID,
            "rewards": 0,
            "balance": 0,
        }
        url = 'http://api.reimaginebanking.com/customers/{}/accounts?key={}'.format(NewID, apiKey)
        response = requests.post(
            url,
            data=json.dumps(NewAccount),
            headers={'content-type': 'application/json'},
        )
        if response.status_code == 201:
            BankID = json.loads(response.text)['objectCreated']["_id"]
            # Fields: Account Number(CustomerNumberID), CustomerID(NewID), AccountID(BankID)
            return BankID
        else:
            print("ACCOUNT ERROR")
            return "ACCOUNT ERROR"
    else:
        print("CUSTOMER CREATION ERROR")
        return "CUSTOMER CREATION ERROR"


def CheckBalance(Message_Dict):
    if CheckIfCustomer(Message_Dict):
        url = "http://api.reimaginebanking.com/accounts/{}?key={}".format(GetAccountNumber(Message_Dict), apiKey)
        return json.loads(requests.get(url).text)['balance']
    else:
        return "ERROR IN CHECK CUSTOMER"


def CheckBalanceByNum(Number):
    if CheckIfCustomerByNum(Number):
        url = "http://api.reimaginebanking.com/accounts/{}?key={}".format(GetAccountNumberFromNumber(Number), apiKey)
        return json.loads(requests.get(url).text)['balance']
    else:
        return "ERROR IN CHECK CUSTOMER"


def TransferFunds(To, From, Amount):
    # Assuming From is a message and To & Amount is a number taken from a database
    PayerAccountID = GetAccountNumber(From)
    PayeeAccountID = GetAccountNumberFromNumber(To)

    url = "http://api.reimaginebanking.com/accounts/{}/transfers?key={}".format(PayerAccountID, apiKey)

    if Amount > CheckBalance(From):
        return "Insufficient Funds :("

    TransactionInfo = {
        "medium": "balance",
        "payee_id": PayeeAccountID,
        "amount": Amount
    }

    response = requests.post(
        url,
        data=json.dumps(TransactionInfo),
        headers={'content-type': 'application/json'},
    )

    if response.status_code == 404:

        return "Payee not found"
    elif response.status_code == 400:
        return "zero"
    else:
        print(response.text)
        return PayeeAccountID


def CheckScratchCardCodeAndSetAsUsed(Code):
    # Call the database for scratch card codes and modify/update
    # Database fields: code  amount
    # Do quick and dirty way
    return 100  # If code exists -> set to used and output money amount else -> false (boolean)


def DepositScratchCardCode(Message_Dict, ScratchCardCodeAmount):
    if CheckIfCustomer(Message_Dict):
        url = "http://api.reimaginebanking.com/accounts/{}/deposits?key={}".format(GetAccountNumber(Message_Dict),
                                                                                   apiKey)

        DepositInfo = {
            "medium": "balance",
            "amount": ScratchCardCodeAmount
        }
        response = requests.post(
            url,
            data=json.dumps(DepositInfo),
            headers={'content-type': 'application/json'},
        )
        if response.status_code == 404:
            return "Desposit Failed"
        else:
            return "Transaction Successful"
    else:
        return "ERROR IN CHECK CUSTOMER"


def DepositScratchCardCodeNum(Number, ScratchCardCode):
    if CheckIfCustomerByNum(Number):
        url = "http://api.reimaginebanking.com/accounts/{}/deposits?key={}".format(GetAccountNumberFromNumber(Number),
                                                                                   apiKey)

        ScratchCodeResult = CheckScratchCardCodeAndSetAsUsed(ScratchCardCode)
        if not type(ScratchCodeResult) == int:
            return "FAKE CODE OR USED CODE!"

        DepositInfo = {
            "medium": "balance",
            "amount": ScratchCodeResult
        }
        response = requests.post(
            url,
            data=json.dumps(DepositInfo),
            headers={'content-type': 'application/json'},
        )
        if response.status_code == 404:
            return "Desposit Failed"
        else:
            return "Transaction Successful"
    else:
        return "ERROR IN CHECK CUSTOMER"


def TransferFundsNumToNum(To, From, Amount):
    PayerAccountID = GetAccountNumberFromNumber(From)
    PayeeAccountID = GetAccountNumberFromNumber(To)

    url = "http://api.reimaginebanking.com/accounts/{}/transfers?key={}".format(PayerAccountID, apiKey)

    if Amount > CheckBalanceByNum(From):
        return "Insufficient Funds :("

    TransactionInfo = {
        "medium": "balance",
        "payee_id": PayeeAccountID,
        "amount": Amount
    }

    response = requests.post(
        url,
        data=json.dumps(TransactionInfo),
        headers={'content-type': 'application/json'},
    )

    if response.status_code == 404:
        return "Payer not found"
    else:
        print(response.text)
        return "Transaction Successful"


def GenerateScratchCardCode():
    # Add this to the database -> keep a new table which has two fields code and amount
    # Print codes for use :)
    return "".join([str(randint(0, 9)) for i in range(10)])

# print(GenerateScratchCardCode())
# DepositScratchCardCodeNum("+14156906522","09301239231234")
# TransferFunds("+14078194455",Message_Dict,10)
# TransferFundsNumToNum("+14078194455",	"+14156906522",10)
# print(GetAccountNumberFromNumber("+14156906522"))
# print(CheckBalanceByNum("+14078194455"))
# print(CheckBalanceByNum("+14156906522"))
# print(GetAccountNumber(Message_Dict))
# CreateCustomerAndAccount(Message_Dict)

# CreateCustomerAndAccount(Message_Dict)
# CheckBalance(Message_Dict)
# TransferFunds(To,From)

# DepositScratchCardCode(Message_Dict)
# GenerateScratchCardCode()
