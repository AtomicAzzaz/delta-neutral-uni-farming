from APY import *
import requests
import time
import hmac
import hashlib

def openShortLimit(price, qty, currency="FTMUSDT"):
    url = "https://fapi.binance.com/fapi/v1/order?"

    payload = "symbol="+str(currency)+'&side=SELL&timeInForce=GTC&type=LIMIT&quantity='+str(qty)+'&price='+str(price)+'&timestamp='+str(int(time.time()*1000))

    signature = hmac.new(SECRET.encode('utf-8'), payload.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    payload += "&signature=" + signature
    headers = {'X-MBX-APIKEY' : API_KEY}
    data = requests.post(url, params = payload, headers=headers)
    print(data.text)


def closeShortLimit(price, qty, currency="FTMUSDT"):
    url = "https://fapi.binance.com/fapi/v1/order?"

    payload = "symbol="+str(currency)+'&side=BUY&timeInForce=GTC&type=LIMIT&quantity='+str(qty)+'&price='+str(price)+'&timestamp='+str(int(time.time()*1000))


    signature = hmac.new(SECRET.encode('utf-8'), payload.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    payload += "&signature=" + signature
    headers = {'X-MBX-APIKEY' : API_KEY}
    data = requests.post(url, params = payload, headers=headers)
    print(data.text)

def getPrice(currency="FTMUSDT"):
    url = "https://fapi.binance.com//fapi/v1/premiumIndex"

    payload = {'symbol': currency}
    data = requests.get(url=url, params=payload).json()
    print(data)
    return round(float(data['markPrice']),2)


def getOpenOrdersAmount(currency="FTMUSDT"):
    url = "https://fapi.binance.com/fapi/v1/openOrders?"

    payload = 'currency='+ currency +'&timestamp='+str(int(time.time()*1000))


    signature = hmac.new(SECRET.encode('utf-8'), payload.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    payload += "&signature=" + signature
    headers = {'X-MBX-APIKEY' : API_KEY}
    data = requests.get(url, params = payload, headers=headers).json()
    print(data)
    return len(data)

def closeAllOpenOrders(currency="FTMUSDT"):
    url = "https://fapi.binance.com/fapi/v1/allOpenOrders?"

    payload = 'symbol='+ currency +'&timestamp='+str(int(time.time()*1000))


    signature = hmac.new(SECRET.encode('utf-8'), payload.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    payload += "&signature=" + signature
    headers = {'X-MBX-APIKEY' : API_KEY}
    data = requests.delete(url, params = payload, headers=headers).json()
    print(data)
    


