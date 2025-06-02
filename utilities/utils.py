import yfinance as yf
import os
import webbrowser
from urllib.parse import urlencode
import requests
import json
from datetime import datetime
from ta.trend import SMAIndicator

MIN_VOL = 250
MIN_OI = 20


def get_technical_indicators(symbol):
    data = yf.download(symbol, period="3mo", interval="1d", progress=False)
    close = data['Close'].squeeze()

    sma_series = SMAIndicator(close, window=50).sma_indicator()
    sma_50 = sma_series.iloc[-1]
    latest_price = close.iloc[-1]
    support = close.rolling(window=10).min().iloc[-1]
    resistance = close.rolling(window=10).max().iloc[-1]

    return {
        'latest_price': latest_price,
        'sma_50': sma_50,
        'support': support,
        'resistance': resistance
    }


def is_good_csp_opportunity(price, sma_50, support): return price > sma_50 and price <= support * 1.05


def is_good_cc_opportunity(price, sma_50, resistance): return price < sma_50 and price >= resistance * 0.95


def find_cc_candidates(options_chain, techs, min_dte, max_dte, symbol):
    cc_opportunities = []
    today = datetime.today()
    print(options_chain)

    for date_strike, options_at_strike in options_chain['callExpDateMap'].items():
        print("here")
        try:
            date_part = date_strike.split(":")[0]
            exp_date = datetime.strptime(date_part, "%Y-%m-%d")
            dte = (exp_date - today).days
            if not (min_dte <= dte <= max_dte):
                continue
        except ValueError:
            continue

        for strike_price_str, options_list in options_at_strike.items():
            strike = float(strike_price_str)
            opt = options_list[0]

            if strike > techs['resistance'] and techs['latest_price'] < techs['sma_50']:
                if 0.10 <= opt.get("delta", 0) <= 0.30:
                    iv = opt.get("volatility", 0)
                    if iv <= 100:
                        continue
                    cc_opportunities.append({
                    # entry ={
                        "symbol": opt.get("symbol", ""),
                        "strike": strike,
                        "bid": opt.get("bid"),
                        "ask": opt.get("ask"),
                        "mark": opt.get("mark"),
                        "last": opt.get("last"),
                        "iv": iv,
                        "delta": opt.get("delta"),
                        "dte": dte,
                        "expiration": date_part
                    })
                    
    return cc_opportunities


def find_csp_candidates_from_data(
    data,
    mark_price,
    min_oi=100,
    min_premium=0.5,
    min_delta=-0.25,
    max_delta=-0.20,
    min_days=3,
    max_days=14
):
    candidates = []
    symbol = data.get('symbol')
    underlying_price = data.get('underlyingPrice')
    put_map = data.get('putExpDateMap', {})
    if not put_map:
        return []

    for expiry, strikes in put_map.items():
        # try:
        #     dte = int(expiry.split(":")[1])
        # except (IndexError, ValueError):
        #     continue
        # if not (min_days <= dte <= max_days):
        #     continue

        for strike_str, options in strikes.items():
            strike = float(strike_str)
            if strike > mark_price:
                continue

            for option in options:
                bid = option.get("bid", 0)
                delta = option.get("delta", -1)
                oi = option.get("openInterest", 0)

                if (
                    bid >= min_premium and
                    min_delta <= delta <= max_delta and
                    oi >= min_oi and
                    option.get('totalVolume', 0) > MIN_VOL and
                    option.get('openInterest', 0) > MIN_OI and
                    option.get('volatility', 0) > 10
                ):
                    # roi = (bid / (strike * 100)) * (365 / dte) * 100
                    candidates.append({
                        "symbol": symbol,
                        "strike": strike,
                        "bid": bid,
                        "delta": delta,
                        # "dte": dte,
                        "openInterest": oi,
                        # "roi": round(roi, 2),
                        "mark": underlying_price,
                        "expiration": expiry.split(":")[0],
                        "volatility": option.get('volatility')
                    })
    # return sorted(candidates, key=lambda x: x["roi"], reverse=True)
    return sorted(candidates, key=lambda x: x["volatility"], reverse=True)

# def initializeTastyClient():

def tastytrade_login(scopes="read trade openid"):
    base_url = "https://my.tastytrade.com/auth.html"
    params = {
        "client_id": os.getenv("tasty_client_id"),
        "redirect_uri": os.getenv("TASTY_REDIRECT_URI"),
        "response_type": "code",
        "scope": scopes,
        # "state": "xyz123"  # optional: CSRF protection
    }

    full_url = f"{base_url}?{urlencode(params)}"
    print(f"[+] Launching browser for OAuth flow:\n{full_url}")
    webbrowser.open(full_url)

def get_aggregate_iv(symbol: str, session_token: str) -> float:
    url = f"https://api.tastytrade.com/market-metrics/QQQ"
    headers = {
        "Authorization": f"Bearer {session_token.strip()}"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    print(response.json())

    data = response.json()["data"]
    iv = float(data["implied-volatility"])
    print(iv)
    print(data)
    return iv


