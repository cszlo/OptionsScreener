import json
import requests
import pprint as pp
import argparse
import sys
import datetime 
import ta
from dateutil.relativedelta import relativedelta

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    

def getCalls(CHAIN,symbol):
    CALLS = {}

    today = datetime.date.today()
    toDate = addMonths(addYears(today, 1), 1)
    
    url = f'https://api.tdameritrade.com/v1/marketdata/chains?apikey=6NNACDRDNHKYMBIXPLXZCZMZEGGI5W0V&symbol={symbol}&contractType=CALL&strikeCount=4&fromDate={today}&toDate={toDate}'
    resp = requests.get(url).json()

    pp.pprint(resp)

    underlyingPrice = resp['underlyingPrice']
    CALLS = resp['callExpDateMap']
    CALLS_EXP = CALLS.keys()

    for EXP in CALLS_EXP:
       for strike in CALLS[EXP]:
            mark = float(CALLS[EXP][strike][0]['mark'])
            delta = float(CALLS[EXP][strike][0]['delta'])
            volume = float(CALLS[EXP][strike][0]['totalVolume'])
            expiration = timestampToDate(CALLS[EXP][strike][0]['expirationDate'])

            # if mark > .01 and volume > 10 and delta < 0.9 and delta > 0.5:
            if True:
                date = EXP.split(':')[0]
                if EXP not in CHAIN.keys():
                    CHAIN[date] = [{
                        'description' : CALLS[EXP][strike][0]['description'],
                        'strike' : float(strike),
                        'delta' : float(CALLS[EXP][strike][0]['delta']),
                        'theta' : float(CALLS[EXP][strike][0]['theta']),
                        'mark' : float(CALLS[EXP][strike][0]['mark'])}]
                else:
                    CHAIN[date].append({
                        'description' : CALLS[EXP][strike][0]['description'],
                        'strike' : float(strike),
                        'delta' : float(CALLS[EXP][strike][0]['delta']),
                        'theta' : float(CALLS[EXP][strike][0]['theta']),
                        'mark' : float(CALLS[EXP][strike][0]['mark'])})

    # for option in CHAIN:
    #     if stringToDate(option) >= addYears(datetime.datetime.now().date(), 1):
                # print(datetime.datetime.now().date())     
                # print(option)     
        # print(datetime.datetime(datetime.datetime.now().date().year + 1, datetime.datetime.now().date().month, 1).date())


def stringToDate(date):
    return datetime.datetime.strptime(date, '%Y-%m-%d').date()

def frontMonth(LONGS, SHORTS, args, symbol):
    FRONT_MONTH_CALLS = {}
    front_url = f'https://api.tdameritrade.com/v1/marketdata/chains?apikey=6NNACDRDNHKYMBIXPLXZCZMZEGGI5W0V&symbol={symbol}&contractType=CALL&strikeCount=5&fromDate=2021-01-09&toDate=2022-06-01'
    front_month_response = requests.get(front_url).json()

    underlyingPrice = front_month_response['underlyingPrice']
    FRONT_MONTH_CALLS = front_month_response['callExpDateMap']

    FRONT_MONTH_CALLS_EXP = FRONT_MONTH_CALLS.keys()

    keys = SHORTS.keys()

    for EXP in FRONT_MONTH_CALLS_EXP:
        for strike in FRONT_MONTH_CALLS[EXP]:
            if FRONT_MONTH_CALLS[EXP][strike][0]['mark'] > .1 and FRONT_MONTH_CALLS[EXP][strike][0]['totalVolume'] > args.volume and FRONT_MONTH_CALLS[EXP][strike][0]['strikePrice'] > underlyingPrice :
                if EXP not in keys:
                    SHORTS[EXP] = [{
                                    'description' : FRONT_MONTH_CALLS[EXP][strike][0]['description'],
                                    'strike' : float(strike),
                                    'delta' : float(FRONT_MONTH_CALLS[EXP][strike][0]['delta']),
                                    'theta' : float(FRONT_MONTH_CALLS[EXP][strike][0]['theta']),
                                    'mark' : float(FRONT_MONTH_CALLS[EXP][strike][0]['mark'])}]
                else:
                    SHORTS[EXP].append({
                                    'description' : FRONT_MONTH_CALLS[EXP][strike][0]['description'],
                                    'strike' : float(strike),
                                    'delta' : float(FRONT_MONTH_CALLS[EXP][strike][0]['delta']),
                                    'theta' : float(FRONT_MONTH_CALLS[EXP][strike][0]['theta']),
                                    'mark' : float(FRONT_MONTH_CALLS[EXP][strike][0]['mark'])})

def findCalendarSpreads(LONGS, SHORTS, args, symbol):
    for long_exp in LONGS:
        for short_exp in SHORTS:
            for long_call in LONGS[long_exp]:
                for short_call in SHORTS[short_exp]:
                    cost = (long_call['mark'])*100

                    premium = short_call['mark']*100

                    width = (short_call['strike'] - long_call['strike'])*100

                    sweet_spot = bool(cost <= (((short_call['strike'] - long_call['strike'])*100)*.75))

                    worth_it = bool((short_call['mark']*100) >= (long_call['mark']*100*args.roi))

                    premium_covers_extrinsic = bool(width + premium > cost)

                    if sweet_spot and cost <= args.collateral and worth_it and premium_covers_extrinsic:
                        position = f'''{symbol}
    Buy:  {long_call['description']}\t${(long_call['mark']*100):.2f}
    Sell: {short_call['description']}\t${(short_call['mark']*100):.2f}'''
                        print(position)
                        print()
    
def timestampToDate(timestamp):
    return datetime.datetime.fromtimestamp(timestamp/1000).strftime('%Y-%m-%d')

def addYears(date, qty):
    return date + datetime.timedelta(days=qty)

def addMonths(date, qty):
    return date + relativedelta(months=qty)

def main():
    CHAIN = {}
    symbol = ''
    long_call = {}
    long_exp = ''
    args = {}

    symbols = ['KO', 'KDP', 'SPY', 'AAPL', 'ICLN', 'CWH', 'FIS', 'MSFT', 'COST', 'SHOP', 'ENPH', 'DRIV', 'CHWY', 'MARA', 'XPEV', 'RIOT', 'IDRV', 'ARKG', 'ARKK', 'TSLA', 'EDIT', 'LMND', 'TGT', 'BEAM', 'CRSP', 'TXG', 'JPM', 'GS', 'BAC', 'BA', 'F', 'GME', 'PLTR', 'SPCE', 'FB', 'SNAP', 'V', 'MA', 'SQ', 'WMT']
    # symbols = ['AAPL', 'SPY', 'QQQ', 'TSLA', 'NIO', 'IWM', 'AMD', 'MSFT', 'FB', 'SNAP']

    '''Parse command line arguments to determine proper path to take'''
    parser = argparse.ArgumentParser(description = "Schema uploader.")
    group = parser.add_mutually_exclusive_group()

    parser.add_argument("-$", "--symbol", type = str,
        metavar = "symbol", default = None, required = False,
        help = "Stock SYMBOL")

    parser.add_argument("-c", "--collateral", type = int,
        metavar = "collateral", default = 500, required = False,
        help = "Collateral/Max $$ for Debit")

    parser.add_argument("-v", "--volume", type = int,
        metavar = "volume", default = 200, required = False,
        help = "Total volume of options contract")

    parser.add_argument("-r", "--roi", type = float,
        metavar = "roi", default = .05, required = False,
        help = "Short call premium with regards to long call cost.")

    args = parser.parse_args() 

    symbol = args.symbol if args.symbol else 'AAPL'

    getCalls(CHAIN, symbol)

    # pp.pprint(CHAIN)

    # print(addOneMonth(datetime.date.today()))

    # for symbol in symbols:
    #     try:
    #         backMonth(CHAIN, args, symbol)
    #         frontMonth(LONGS, SHORTS, args, symbol)
    #         findCalendarSpreads(LONGS, SHORTS, args, symbol)
    #     except:
    #         print("Unexpected error:", sys.exc_info()[0])
    #         raise
        
    #     LONGS = {}
    #     SHORTS = {}


if __name__ == '__main__':
# Buy:\t{long_call['description']}\t{bcolors.FAIL}${(long_call['mark']*100):.2f}{bcolors.ENDC}
    main()


# TODO:
'''
Program should:
-Get entire options chain for a given symbol
given a "back month" start date, begin at that key and find all long call position that fit a certain criteria.
--This could be hardcoded or configured but has a default
-Add back month option to list
-Repeat for front month options.

Could write results to file
Could read file for config settings

'''