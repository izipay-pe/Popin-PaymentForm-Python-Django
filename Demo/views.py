from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import base64
import json
import requests
import hashlib
import hmac
from django.http import HttpResponse
from Keys.keys import keys


def index(request):
    return render(request,'Demo/index.html')

def checkout(request):
    #URL de Web Service REST
    url = 'https://api.micuentaweb.pe/api-payment/V4/Charge/CreatePayment'

    #Encabezado Basic con concatenación de "usuario:contraseña" en base64
    auth = 'Basic ' + base64.b64encode(f"{keys["USERNAME"]}:{keys["PASSWORD"]}".encode('utf-8')).decode('utf-8')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': auth,
    }

    data = {
        "amount": int(float(request.POST['amount']) * 100),
        "currency": request.POST['currency'],
        "orderId": request.POST['orderId'],
        "customer": {
            "email": request.POST['email'],
            "firstName": request.POST['firstName'],
            "lastName": request.POST['lastName'],
            "phoneNumber": request.POST['phoneNumber'],
            "identityType": request.POST['identityType'],
            "identityCode": request.POST['identityCode'],
            "address": request.POST['address'],
            "country": request.POST['country'],
            "state": request.POST['state'],
            "city": request.POST['city'],
            "zipCode": request.POST['zipCode'],    
        }
    }

    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()

    if response_data['status'] != 'SUCCESS':
        raise Exception
    
    token = response_data['answer']['formToken']
    return render(request, 'Demo/checkout.html', {'token': token, 'publickey': keys['PUBLIC_KEY']})

@csrf_exempt
def result(request):
    if not request.POST: 
        raise Exception("No post data received!")

    #Validación de firma
    if not checkHash(request.POST, keys["HMACSHA256"]) : 
        raise Exception("Invalid signature")

    answer_json = json.loads(request.POST['kr-answer'])
    krAnswerData = json.dumps(answer_json, indent=2)
    postData = json.dumps(request.POST, indent=4)

    answer_json["orderDetails"]["orderTotalAmount"] = answer_json["orderDetails"]["orderTotalAmount"] / 100

    return render(request, 'Demo/result.html', {'answer': answer_json, 'postData': postData, 'krAnswerData': krAnswerData})

@csrf_exempt
def ipn(request):
    if not request.POST: 
        raise Exception("No post data received!")

    #Validación de firma en IPN
    if not checkHash(request.POST, keys["PASSWORD"]) : 
        raise Exception("Invalid signature")
    
    answer = json.loads(request.POST['kr-answer']) 
    transaction = answer['transactions'][0]

    #Verificar orderStatus: PAID / UNPAID
    orderStatus = answer['orderStatus']
    orderId = answer['orderDetails']['orderId']
    transactionUuid = transaction['uuid']

    return HttpResponse(status=200, content=f"OK! OrderStatus is {orderStatus} ")

def checkHash(response, key):

    answer = response['kr-answer'].encode('utf-8')

    calculateHash = hmac.new(key.encode('utf-8'), answer, hashlib.sha256).hexdigest()

    return calculateHash == response['kr-hash']