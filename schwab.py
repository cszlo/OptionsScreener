import schwabdev as sd
import dotenv
from utilities.tasty_trade_auth import TastytradeClient
import os
import pprint as pp
import argparse
import json
import yfinance as yf
import pandas as pd
import logging as log
from ta.trend import SMAIndicator

from utilities import models as m, parsers as parse, utils, library as lib

args = {}

class StockQuote:
    symbol: str
    quote: str

def get_args():
    """
    Parse command-line arguments for the schema uploader script.

    Returns:
        argparse.Namespace: Parsed arguments with the following attributes:
            - symbol (str or None): Single stock symbol, specified with -$ or --symbol.
            - symbols (list[str] or None): List of stock symbols, specified with --symbols.
            - function (str or None): Function mode to run, e.g., "OPTION" or "STOCK", specified with -fn or --function.
            - dte (list[int] or None): Two integers representing minimum and maximum days to expiration, specified with -dte or --dte.

    Notes:
        - The `--symbol` and `--symbols` arguments are mutually exclusive.
        - The `--dte` argument expects exactly two integer values.
    """
    parser = argparse.ArgumentParser(description="Schema uploader.")
    group = parser.add_mutually_exclusive_group()

    parser.add_argument("-$", "--symbol", type=str, metavar="symbol", default=None, required=False, help="Stock SYMBOL")
    parser.add_argument('--symbols', nargs='+', help='Performs various functions based off of --symbols provided', required=False)
    parser.add_argument("-fn", "--function", type=str, metavar="function", default=None, required=False, help="(OPTION|STOCK)")
    parser.add_argument("-dte", "--dte", type=int, nargs=2, metavar=("MIN_DTE", "MAX_DTE"), required=False, help="Specify min and max DTE, e.g. --dte 7 10")
    parser.add_argument("-interval", "--interval", type=str, nargs=1, required=False, help="Proce history interval i.e. 1d, 4h, 1h...")


    return parser.parse_args()

def initialize_client():
    """Initialize the Schwab client with environment variables and error handling."""
    try:
        app_key = os.getenv("app_key")
        app_secret = os.getenv("app_secret")
        redirect_uri = "https://127.0.0.1"

        if not app_key or not app_secret:
            raise ValueError("Missing required environment variables: app_key or app_secret.")

        client = sd.Client(app_key, app_secret, redirect_uri)
        log.info("Schwab client initialized successfully.")
        return client

    except Exception as e:
        log.error(f"Failed to initialize Schwab client: {e}")
        return None

def process_function(function, symbols, client, parse, utils, min_dte=7, max_dte=15):
    """
    Execute different processing logic based on the specified function argument.

    Args:
        function (str or None): The mode of operation. Expected values include
            "OPTIONS", "OPTION", "OPT", "OPTS" (all mapped to options processing),
            or "STOCK" for stock data processing. If None, runs default analysis.
        symbols (list[str]): List of stock symbols to process.
        client: API client instance with methods price_history(), quote(), and option_chains().
        parse: Module with a parse_quote() function to parse quote data.
        utils: Module with helper functions:
            - get_technical_indicators(symbol)
            - is_good_csp_opportunity(price, sma_50, support)
            - is_good_cc_opportunity(price, sma_50, resistance)
            - find_cc_candidates(options_chain, techs, min_dte, max_dte)
        min_dte (int): Minimum days to expiration for options filtering.
        max_dte (int): Maximum days to expiration for options filtering.

    Behavior:
        - For OPTIONS function variants, prints a placeholder message.
        - For STOCK, downloads and saves stock price history, quote data, and option chains for each symbol.
        - If function is None, runs technical analysis and finds covered call candidates.

    Returns:
        None
    """

    # OPTIONS | OPTION | OPTS | OPT
    def OPTIONS():
        print("You selected case A")
        # Get options chain
        # filter options by IV, vol, delta, etc.

    # Generates the following JSON files:
    # - <symbol>_price_history.json
    # - <symbol>_quote_data.json
    def STOCK():
        for symbol in symbols:
            rawStockPriceHistory = client.price_history(symbol=symbol, periodType="day")

            rawStockPriceHistoryFilename = f"./quotes/{symbol}_price_history.json"
            with open(rawStockPriceHistoryFilename, "w") as f:
                json.dump(rawStockPriceHistory.json(), f, indent=4)

            rawStockQuoteData = client.quote(symbol_id=symbol, fields="all")

            # Mark price print
            mark = parse.parse_quote(symbol=symbol, data=rawStockQuoteData.json()[symbol]).quote['mark']
            print(symbol)
            print(mark)

            rawStockQuoteDataFilename = f"./quotes/{symbol}_quote_data.json"
            with open(rawStockQuoteDataFilename, "w") as f:
                json.dump(rawStockQuoteData.json(), f, indent=4)

            rawOptionsChain = client.option_chains(symbol=symbol, contractType="CALL", strike=130, strikeCount=30).json()
            rawOptionsChainFilename = f"./quotes/{symbol}_options_chain.json"
            with open(rawOptionsChainFilename, "w") as f:
                json.dump(rawOptionsChain, f, indent=4)

    def default_case():
        report_contents = []
        for symbol in symbols:
            # Analyze Support Levels
            techs = utils.get_technical_indicators(symbol)
            # print("Checking " + symbol + "...")
            # Fetch Historical Price
            rawStockQuoteData = client.quote(symbol_id=symbol, fields="all")
            # print(techs)
            mark_price = parse.parse_quote(symbol=symbol, data=rawStockQuoteData.json()[symbol]).quote['mark']
            
            # Fetch Options Data
            # rawOptionsChain = client.option_chains(symbol=symbol, contractType="PUT", strike=130, strikeCount=20).json()

            # Analyze Trend
            # Analyze Volatility
            # Screen Options Contracts
            # Write Something To File
            # Next->
            

            if utils.is_good_csp_opportunity(techs['latest_price'], techs['sma_50'], techs['support']):
                # print("Potential CSP for ")
                # print(symbol)
                rawOptionsChain = client.option_chains(symbol=symbol, contractType="PUT", strike=130, strikeCount=20).json()
                candidates = []
                candidates = utils.find_csp_candidates_from_data(rawOptionsChain, mark_price)
                if candidates:
                    str1 = f"Potential CSP trade for {symbol}:\t\t50SMA: {techs['sma_50']:.2f}\t\tResistance: {techs['resistance']:.2f}\t\tSupport: {techs['support']:.2f}"
                    report_contents.append(str1)
                    for candidate in candidates:
                        formatted = (
                            f"\t\t{candidate['symbol']} ${candidate['strike']} PUT @ ${candidate['bid']}\t| "
                            # f"Delta: {candidate['delta']:.2f}\t| ROI: {candidate['roi']*100:.1f}%\t| Volatility: {candidate['volatility']:.2f}\t"
                            f"Delta: {candidate['delta']:.2f}\t| Volatility: {candidate['volatility']:.2f}\t|"
                            # f"OI: {candidate['openInterest']}\t| DTE: {candidate['dte']}\t| Exp: {candidate['expiration']}\t| "
                            f"OI: {candidate['openInterest']}\t| Exp: {candidate['expiration']}\t| "
                            f"Mark: ${candidate['mark']}"
                        )
                        report_contents.append(formatted)
                        
            # if utils.is_good_cc_opportunity(techs['latest_price'], techs['sma_50'], techs['resistance']):
            #     print(f"CC setup likely for {symbol} — price near resistance.")



            # candidates = find_csp_candidates_from_data(rawOptionsChain, mark_price)
            # if candidates:
            #     print("Potential Cash Secured Put Candidate(s):")
            #     for c in candidates[:5]:
            #         print(c)

            # # utils.find_cc_candidates(rawOptionsChain, techs, min_dte, max_dte, symbol)
            # cc_candidates = utils.find_cc_candidates(rawOptionsChain, techs, min_dte, max_dte, symbol)
            # ccDataFilename = f"./CC/{symbol}_cc_data.json"
            
            # if cc_candidates:
            #     print("candidates")
            #     with open(ccDataFilename, "w") as f:
            #         json.dump(cc_candidates, f, indent=4)
            #     print("Potential Covered Call Candidate(s):")
            #     for c in cc_candidates:
            #         print(c)
            #         json.dump(c, f, indent=4)
            #     print()
        # print(report_contents)
        with open("./report.txt", "w") as f:
            for line in report_contents:
                f.write(line + "\n")
    switch = {
        "OPTIONS": OPTIONS,
        "OPTION": OPTIONS,
        "OPT": OPTIONS,
        "OPTS": OPTIONS,
        "STOCK": STOCK,
    }

    if function is not None:
        switch.get(function, default_case)()
    else:
        default_case()

"""Entry point: parses CLI args, loads env, initializes client, and runs processing."""
if __name__ == "__main__":
    args = get_args()

    if args.symbols:
        symbols = args.symbols
    else:
        symbols = lib.TICKERS

    if args.function:
        function = args.function
    else:
        function = None

    if args.dte:
        min_dte, max_dte = args.dte
    else:
        min_dte = 7
        max_dte = 15

    if args.interval:
        interval = args.interval
    else:
        interval = '1d'

    dotenv.load_dotenv()

    schwabClient = initialize_client()
    if schwabClient is None:
        # Handle client not being initialized
        pass

    
    # tClient = TastytradeClient(
    #     client_id=os.getenv("tasty_client_id"),
    #     client_secret=os.getenv("tasty_secret"),
    #     redirect_uri="http://localhost:8080/callback"
    # )

    # auth_code = tClient.get_auth_code()
    # token_data = tClient.exchange_code_for_token(auth_code)
    # tClient.start_token_refresh_daemon()

    # Use client.access_token to make authenticated requests
    # print("Access Token:", tClient.access_token)



    process_function(function, symbols, schwabClient, parse, utils, min_dte, max_dte)






    







