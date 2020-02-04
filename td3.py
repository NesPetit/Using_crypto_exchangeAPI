import requests
import json
from requests.auth import AuthBase
import sqlite3
from datetime import datetime


class CoinbaseExchangeAuth(AuthBase):
    def __init__(self, api_key, secret_key, passphrase):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

    def __call__(self, request):
        timestamp = str(time.time())
        message = timestamp + request.method + request.path_url + (request.body or '')
        hmac_key = base64.b64decode(self.secret_key)
        signature = hmac.new(hmac_key, message, hashlib.sha256)
        signature_b64 = signature.digest().encode('base64').rstrip('\n')

        request.headers.update({
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        })
        return request


def getCrypto():
    c = requests.get('https://api.pro.coinbase.com/currencies')
    print(c.status_code)
    c_json = json.loads(c.text)
    for i in c_json:
        print("%s : %s" % (i['id'], i['name']))


def getDepth(direction, pair):
    rqt = 'https://api.pro.coinbase.com/products/' + pair + '/book'
    var = requests.get(rqt)
    var_json = json.loads(variable.text)
    if direction == 'ask':
        print('Ask : ',variable_json['asks'])
    elif direction == 'bid':
        print('Bids : ',variable_json['bids'])
    else :
        print("Erreur")

        
def getOrderBook(direction, pair):
    rqt = 'https://api.pro.coinbase.com/products/' + pair + '/book?level=3'
    var = requests.get(rqt)
    var_json = json.loads(var.text)
    t = var_json[direction]
    # The first ten are displayed
    for i in range(0,10):
        print(t[i])
        

def refreshDataCandle(pair,duration):
    duration = 60*int(duration)
    r = requests.get('https://api.pro.coinbase.com/products/' + pair + '/candles?granularity=' + str(duration))
    r_json = json.loads(r.text)
    if r_json != 'null':
        print("Candles read")
    return r_json


def create_sqlite_table(setTableName):

    conn = sqlite3.connect(setTableName)
    c = conn.cursor()

    tableCreationStatement = "CREATE TABLE IF NOT EXISTS " + setTableName + """(Id INTEGER PRIMARY KEY, date INT, low REAL, high REAL, open REAL, close REAL, volume REAL)"""
    c.execute(tableCreationStatement)

    print("Table successfully created !")
    c.close()
    conn.close()


def store_candle_in_db(setTableName, pair, duration):
    
    conn = sqlite3.connect(setTableName)
    c = conn.cursor()

    tableCreationStatement = "CREATE TABLE IF NOT EXISTS " + setTableName + """(Id INTEGER PRIMARY KEY, date INT, low REAL, high REAL, open REAL, close REAL, volume REAL)"""
    c.execute(tableCreationStatement)
    data = refreshDataCandle(pair, duration)
    if not data:
        exit()

    for i in range(0, len(data)):
        request = ("INSERT OR REPLACE INTO " + setTableName + """(Id, date, low, high, open, close, volume) VALUES(""" + str(i) + "," + str(data[i][0]) + "," + str(data[i][1]) + "," + str(data[i][2]) + "," + str(data[i][3]) + "," + str(data[i][4]) + "," + str(data[i][5]) + ")")
        print(request)
        c.execute(request)
        conn.commit()
    
    c.close()
    conn.close()


def refreshData(pair):
    api_url='https://api.pro.coinbase.com/products/' + str(pair) + '/trades'
    r = requests.get(api_url)
    r_json = json.loads(r.text)
    if(r_json != 'null'):
        print("Data read")
    print(r_json)
    return r_json


def store_data_sqlite(setTableName, pair):
    conn = sqlite3.connect(setTableName)
    c = conn.cursor()

    tableCreationStatement = "CREATE TABLE IF NOT EXISTS " + setTableName + """(Id INTEGER PRIMARY KEY, traded_btc REAL, price REAL, created_at_int INT, side TEXT)"""

    c.execute(tableCreationStatement)
    data = refreshData(pair)
    if not data:
        exit()

    for i in range(0, len(data)):
        request = ("INSERT OR REPLACE INTO " + setTableName + """(Id, traded_btc, price, created_at_int, side) VALUES(?,?,?,?,?);""")
        print("INSERT INTO " + setTableName + ":" + str(i) + "," + str(data[i]['trade_id']) + "," + str(data[i]['price']) + "," + str(data[i]['time']) + "," + str(data[i]['side']))
        
        c.execute(request,(str(i), str(data[i]['trade_id']), str(data[i]['price']), str(data[i]['time']), str(data[i]['side'])))
        conn.commit() 
    c.close()
    conn.close()


def createOrder(api_key,secret_key,passphrase,direction,price,amount,pair='BTC-USD_d',orderType='LimitOrder'):
    api_url = 'https://api.pro.coinbase.com/'
    auth = CoinbaseExchangeAuth(api_key, secret_key, passphrase)
    order = {
        'size': amount,
        'price': price,
        'side': direction,
        'product_id': pair,
        'type':orderType,}
    r = requests.post(api_url + 'orders', json=order, auth=auth)
    print('\nOrder created:', r.json())
    # Show orders
    r = requests.get('https://api-public.sandbox.pro.coinbase.com/orders', auth=auth)
    print('\nList of orders:', r.json())

def cancelOrder(api_key,secret_key,uuid,passphrase):
    api_url = 'https://api.pro.coinbase.com/orders/'
    auth = CoinbaseExchangeAuth(api_key, secret_key, passphrase)
    r = requests.delete(api_url +str(uuid), auth=auth)


c = 0
while c != 11:
    # Menu
    print("\nMini Projet : Alec GUESSOUS - Alexandre PEREZ\n")
    print("---------MENU---------\n")
    print("1) Get a list of all available cryptocurrencies and display it")
    print("2) Display the ’ask’ or ‘bid’ price of an asset")
    print("3) Get order book for an asset")
    print("4) Read agregated trading data (candles)")
    print("5) Create a sqlite table to store said data")
    print("6) Store candle data in the db")
    print("7) Extract all available trade data")
    print("8) Store the data in sqlite")
    print("9) Create order")
    print("10) Cancel order")
    print("11) Exit ")

    c = input("Choix : ")

    # Get a list of all available cryptocurrencies and display it
    if c == '1': 
        getCrypto()

    # Display the ’ask’ or ‘bid’ price of an asset.
    elif c == '2':
        prm = input("Please enter your search parameter \n")
        currency = input("Please enter your currency \n")
        getDepth(prm, currency)

    # Get order book for an asset
    elif c == '3':
        prm = input("Please enter your search parameter \n")
        currency = input("Please enter your currency \n")
        getOrderBook(prm, currency)

    # Read agregated trading data 
    elif c == '4':
        currency = input("Please select your currency \n")
        duration = input("Please enter your duration (in minute) \n")
        candles = refreshDataCandle(currency, duration)

    # Create a sqlite table
    elif c == '5':
        exchange_name = str(input("Can you enter a name of your table please ?\n"))
        duration = str(input("Please enter your duration (in minute) \n"))
        currency = str(input("Please enter your currency \n"))
        name_t = str(exchange_name + "" + currency.translate({ord('-'): None}) + "" + duration)
        create_sqlite_table(name_t)

    # Store candle data in the db
    elif c == '6':
        exchange_name = str(input("Can you enter a name of your table please ?\n"))
        duration = str(input("Please enter your duration (in minute) \n"))
        currency = str(input("Please enter your currency \n"))
        name_t = str(exchange_name + "" + currency.translate({ord('-'): None}) + "" + duration)
        store_candle_in_db(name_t, currency, duration)

    # Create a function to extract all available trade data
    elif c == '7':
        currency = input("Please enter your currency \n")
        refreshData(currency)

    # Store the data in sqlite
    elif c == '8':
        exchange_name = str(input("Can you enter a name of your table please ?\n"))
        duration = str(input("Please enter your duration (in minute) \n"))
        currency = str(input("Please enter your currency \n"))
        name_t = str(exchange_name + "" + currency.translate({ord('-'): None}) + "" + duration)
        store_data_sqlite(name_t, currency)

    # Create an order
    elif c == '9':
        print('API Key:')
        api_key = bytes(input(), encoding = 'utf-8')
        print('API Secret Key:')
        secret_key = bytes(input(), encoding = 'utf-8')
        print('Passphrase:')
        passphrase = bytes(input(), encoding = 'utf-8')
        prm = input("Please enter your search parameter \n")
        price = input("Please enter the price \n")
        amount = input("Please enter the amount \n")
        currency = input("Please enter your currency \n")
        #createOrder(api_key,secret_key,passphrase,direction,price,amount,currency,orderType='LimitOrder')

    # Cancel an order
    elif c == '10':
        print('API Key:')
        api_key = bytes(input(), encoding = 'utf-8')
        print('API Secret Key:')
        secret_key = bytes(input(), encoding = 'utf-8')
        print('Passphrase:')
        passphrase = bytes(input(), encoding = 'utf-8')
        #cancelOrder(api_key,secret_key,uuid,passphrase)

    # Exit
    elif c == '11':
        exit()
    else:
        print("Erreur")
        
