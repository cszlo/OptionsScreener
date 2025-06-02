from typing import Dict, Any, Optional
from utilities.models import OptionContract, OptionChain, Quote, QuoteData, RegularMarket, ReferenceData, Fundamental, ExtendedQuote
from datetime import datetime

def parse_option_chain(data: Dict[str, Any]) -> OptionChain:
    symbol = data.get("symbol")
    status = data.get("status")
    underlying_price = data.get("underlyingPrice")
    number_of_contracts = 0
    options = []

    # The option data is nested under callExpDateMap for calls
    # (similar for putExpDateMap for puts)
    call_exp_date_map = data.get("callExpDateMap", {})

    for expiration_date, strikes in call_exp_date_map.items():
        for strike_price, contracts in strikes.items():
            for contract in contracts:
                option = OptionContract(
                    putCall=contract.get("putCall"),
                    symbol=contract.get("symbol"),
                    strikePrice=contract.get("strikePrice"),
                    expirationDate=contract.get("expirationDate"),
                    daysToExpiration=contract.get("daysToExpiration"),
                    bid=contract.get("bid"),
                    ask=contract.get("ask"),
                    last=contract.get("last"),
                    mark=contract.get("mark"),
                    volatility=contract.get("volatility"),
                    delta=contract.get("delta"),
                    gamma=contract.get("gamma"),
                    theta=contract.get("theta"),
                    vega=contract.get("vega"),
                    openInterest=contract.get("openInterest"),
                    volume=contract.get("totalVolume"),
                    inTheMoney=contract.get("inTheMoney"),
                )
                options.append(option)
                number_of_contracts += 1

    return OptionChain(
        symbol=symbol,
        status=status,
        underlyingPrice=underlying_price,
        numberOfContracts=number_of_contracts,
        options=options
    )



def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    if dt_str:
        return datetime.fromisoformat(dt_str.replace("Z", ""))
    return None

def parse_quote(symbol: str, data: dict) -> Quote:
    return Quote(
        symbol=symbol,
        # assetMainType=data["assetMainType"],
        # assetSubType=data["assetSubType"],
        # ssid=data["ssid"],
        # quoteType=data["quoteType"],
        quote=data["quote"],
        # realtime=data["realtime"],
        # fundamental=Fundamental(**data["fundamental"]),
        # quote=QuoteData(
        #     _52WeekHigh=data["quote"]["52WeekHigh"],
        #     _52WeekLow=data["quote"]["52WeekLow"],
        #     **{k: v for k, v in data["quote"].items() if k not in ["52WeekHigh", "52WeekLow"]}
        # ),
        # extended=ExtendedQuote(**data["extended"]),
        # reference=ReferenceData(**data["reference"]),
        regular=RegularMarket(**data["regular"])
    )