#!/usr/bin/python

# ~~~~~==============   HOW TO RUN   ==============~~~~~
# chmod +x bot.py
# while true; do ./bot.py; sleep 1; done

from __future__ import print_function
import random
import sys
import socket
import json
#import thread
import time
# ~~~~~============== CONFIGURATION  ==============~~~~~
# replace REPLACEME with your team name!
team_name="Strawberry"
# This variable dictates whether or not the bot is connecting to the prod
# or test exchange. Be careful with this switch!
test_mode = False

# This setting changes which test exchange is connected to.
# 0 is prod-like
# 1 is slower
# 2 is empty
test_exchange_index=0
prod_exchange_hostname="production"

port=25000 + (test_exchange_index if test_mode else 0)
exchange_hostname = "test-exch-" + team_name if test_mode else prod_exchange_hostname

# ~~~~~============== NETWORKING CODE ==============~~~~~
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((exchange_hostname, port))
    return s.makefile('rw', 1)

def write_to_exchange(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read_from_exchange(exchange):
    return json.loads(exchange.readline())


# ~~~~~============== MAIN LOOP ==============~~~~~

def buy(security, numSecurities):
    write_to_exchange(exchange, {"type": "add", "order_id": security["bidID"], "symbol": security["code"], "dir": "BUY", "price": security["offer"] , "size": numSecurities})
    while True:
        r = read_from_exchange(exchange)
        if r["type"] == "ack":
            #print(">>>>>>>>>>>>>>>>>>>response:",r,file=sys.stderr)

            break
        elif r["type"] == "reject":

            break

        elif r["type"] == "error":
            print(r["error"])
            break
    security["position"] += 1

def sell(security, numSecurities):

    write_to_exchange(exchange, {"type": "add", "order_id": security["bidID"], "symbol": security["code"], "dir": "SELL", "price": security["offer"] , "size": numSecurities})
    while True:
        r = read_from_exchange(exchange)
        if r["type"] == "ack":
            print(">>>>>>>>>>>>>>>>>>>response:",r,file=sys.stderr)
            break
        elif r["type"] == "reject":
            print("help")
            break
        elif r["type"] == "error":
            print(r["error"])
            break

    security["position"] -= 1

def cancel(id):
    if id == None: return
    write_to_exchange(exchange, {"type": "cancel", "orderID": id})

def pnl(securities, usd):
    pnl = 0
    for x in securities:
       pnl += ((x["offer"] - x["bid"]) / 2) * x["position"]
    print("PNL: " + str(pnl))


# Define a function for the thread
#def checkFill( threadName):
   # while True:
        #r = read_from_exchange(exchange)
        #if r["type"] == "fill":
            #print(">>>>>>>>>>>>>>>>>>>response:",r,file=sys.stderr)


def main():

    write_to_exchange(exchange, {"type": "hello", "team": team_name.upper()})
    hello_from_exchange = read_from_exchange(exchange)
    # A common mistake people make is to call write_to_exchange() > 1
    # time for every read_from_exchange() response.
    # Since many write messages generate marketdata, this will cause an
    # exponential explosion in pending messages. Please, don't do that!

    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)

    r = read_from_exchange(exchange)
    print("the exchange replied:",r,file=sys.stderr)

    for y in hello_from_exchange["symbols"]:
        print(y)

    usd = hello_from_exchange["symbols"][3]["position"]
    print(">>>>>>"+str(usd))


    securities = [
            { "code": "BOND",  "bid": 0, "bidID": None, "offer": 0, "offerID": None },
            { "code": "VALBZ", "bid": 0, "bidID": None, "offer": 0, "offerID": None },
            { "code": "VALE",  "bid": 0, "bidID": None, "offer": 0, "offerID": None },
            { "code": "GS",    "bid": 0, "bidID": None, "offer": 0, "offerID": None },
            { "code": "MS",    "bid": 0, "bidID": None, "offer": 0, "offerID": None },
            { "code": "WFC",   "bid": 0, "bidID": None, "offer": 0, "offerID": None },
            { "code": "XLF",   "bid": 0, "bidID": None, "offer": 0, "offerID": None }
    ]
    if r["type"] == "open":

        i = 0

        while True:

            r = read_from_exchange(exchange)
            if r["type"] == "book":

               for x in securities:
                  #print(r["symbol"] + " " +  x["code"])
                  if r["symbol"] == x["code"]:
                        if len(r["buy"]) > 0 and x["bid"] != r["buy"][0][0]:
                            cancel(x["bidID"])
                            x["bid"] = r["buy"][0][0]
                            x["bidID"] = i
                            buy(x,1)
                            i += 1
                        if len(r["sell"]) > 0 and x["offer"] != r["sell"][0][0]:
                            cancel(x["offerID"])
                            x["offer"] = r["sell"][0][0]
                            x["offerID"] = i
                            sell(x,1)
                            i += 1
                        break

                  print(x)
                  print(">>>>>>"+str(usd))
                  print(str(pnl(securities,usd)))
            #if r["type"] == "open":
             #   print(r)
            #if r["type"] == "open":
             #   print(r)

        #while True:
        #    r = read_from_exchange(exchange)
        #    if r["type"] == "fill":
        #        print(">>>>>>>>>>>>>>>>>>>response:",r,file=sys.stderr)



exchange = connect()
main()






