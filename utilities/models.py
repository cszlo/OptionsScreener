from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

@dataclass
class OptionContract:
    putCall: str
    symbol: str
    strikePrice: float
    expirationDate: str
    daysToExpiration: int
    bid: float
    ask: float
    last: float
    mark: float
    volatility: float
    delta: float
    gamma: float
    theta: float
    vega: float
    openInterest: int
    volume: int
    inTheMoney: bool

@dataclass
class OptionChain:
    symbol: str
    status: str
    underlyingPrice: float
    numberOfContracts: int
    options: List[OptionContract] = field(default_factory=list)

@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: int
    datetime: datetime

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            volume=data["volume"],
            datetime=datetime.fromtimestamp(data["datetime"] / 1000)  # ms to seconds
        )

@dataclass
class ExtendedQuote:
    askPrice: float
    askSize: int
    bidPrice: float
    bidSize: int
    lastPrice: float
    lastSize: int
    mark: float
    quoteTime: int  # Unix timestamp (ms)
    totalVolume: int
    tradeTime: int  # Unix timestamp (ms)

@dataclass
class Fundamental:
    avg10DaysVolume: Optional[float]
    avg1YearVolume: Optional[float]
    declarationDate: Optional[datetime]
    divAmount: Optional[float]
    divExDate: Optional[datetime]
    divFreq: Optional[int]
    divPayAmount: Optional[float]
    divPayDate: Optional[datetime]
    divYield: Optional[float]
    eps: Optional[float]
    fundLeverageFactor: Optional[float]
    lastEarningsDate: Optional[datetime]
    nextDivExDate: Optional[datetime]
    nextDivPayDate: Optional[datetime]
    peRatio: Optional[float]

@dataclass
class QuoteData:
    # _52WeekHigh: float
    # _52WeekLow: float
    # askMICId: str
    # askPrice: float
    # askSize: int
    # askTime: int
    # bidMICId: str
    # bidPrice: float
    # bidSize: int
    # bidTime: int
    # closePrice: float
    # highPrice: float
    # lastMICId: str
    # lastPrice: float
    # lastSize: int
    # lowPrice: float
    mark: float
    # markChange: float
    # markPercentChange: float
    # netChange: float
    netPercentChange: float
    # openPrice: float
    # postMarketChange: float
    # postMarketPercentChange: float
    # quoteTime: int
    # securityStatus: str
    # totalVolume: int
    # tradeTime: int

@dataclass
class ReferenceData:
    cusip: str
    description: str
    exchange: str
    exchangeName: str
    htbQuantity: int
    htbRate: float
    isHardToBorrow: bool
    isShortable: bool

@dataclass
class RegularMarket:
    regularMarketLastPrice: float
    regularMarketLastSize: int
    regularMarketNetChange: float
    regularMarketPercentChange: float
    regularMarketTradeTime: int

@dataclass
class Quote:
    symbol: str
    # ssid: int
    # assetMainType: str
    # assetSubType: str
    # quoteType: str
    # realtime: bool
    # fundamental: Fundamental
    # extended: ExtendedQuote
    quote: QuoteData
    # reference: ReferenceData
    regular: RegularMarket
    # symbol: str
    # asset_main_type: str
    # asset_sub_type: str
    # avg_10_day_volume: Optional[float]
    # avg_1_year_volume: Optional[float]
    # dividend_yield: Optional[float]
    # dividend_amount: Optional[float]
    # dividend_ex_date: Optional[datetime]
    # next_div_ex_date: Optional[datetime]
    # eps: Optional[float]
    # pe_ratio: Optional[float]