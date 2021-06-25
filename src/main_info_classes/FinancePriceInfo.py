import requests
import json
import time
import logging
from datetime import datetime
from src.items.Asset import Asset
from src.utils.utils import PostAssetMatch
from src.utils.trading_date_util import get_recent_trading_day
from src.utils.custom_decorators import time_func

ALPHA_VANTAGE_URL = "https://alpha-vantage.p.rapidapi.com/query"
logger = logging.getLogger(__name__)


class FinancePriceGetter:
    '''
    Gets Crypto and Stock price at a given time
    '''
    def __init__(self, url=ALPHA_VANTAGE_URL):
        self.url = url
        self.headers = {
            'x-rapidapi-key': "a2be0a9882msh3b935dcee5ea132p149e93jsn6ee345447ea0",
            'x-rapidapi-host': "alpha-vantage.p.rapidapi.com"
        }
    
    @time_func
    def get_current_crypto_price(self, ticker):
        querystring = {"from_currency":ticker,"function":"CURRENCY_EXCHANGE_RATE","to_currency":"USD"}
        response = requests.request("GET", self.url, headers=self.headers, params=querystring)
        return response.json()["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
    
    @time_func
    def get_current_stock_price(self, ticker):
        REAL_TIME_URL = "https://twelve-data1.p.rapidapi.com/quote"
        REAL_TIME_HEADERS = {
            'x-rapidapi-key': "a2be0a9882msh3b935dcee5ea132p149e93jsn6ee345447ea0",
            'x-rapidapi-host': "twelve-data1.p.rapidapi.com"
        }
        querystring = {"symbol":ticker,"interval":"1min","outputsize":"30","format":"json"}
        response = requests.request("GET", REAL_TIME_URL, headers=REAL_TIME_HEADERS, params=querystring)
        return response.json()['close']

    @time_func
    def _get_stock_prices_historic(self, ticker, created_at, is_full=False) -> dict:
        outputsize = "full" if is_full else "compact"
        querystring = {"function":"TIME_SERIES_DAILY","symbol":ticker, "outputsize": outputsize}

        response = requests.request("GET", self.url, headers=self.headers, params=querystring)
        last_trading_day = str(get_recent_trading_day(created_at)).split(" ")[0]

        if last_trading_day == datetime.today().strftime('%Y-%m-%d'):
            self.get_current_stock_price(ticker)

        return response.json()["Time Series (Daily)"][last_trading_day]["4. close"]

    @time_func
    def _get_crypto_prices(self, ticker, created_at) -> dict:
        querystring = {"market":"USD","symbol":ticker,"function":"DIGITAL_CURRENCY_DAILY"}

        if created_at == datetime.today().strftime('%Y-%m-%d'):
            return self.get_current_crypto_price(ticker, created_at)
        response = requests.request("GET", self.url, headers=self.headers, params=querystring)
        print(ticker)
        return response.json()["Time Series (Digital Currency Daily)"][created_at]["4b. close (USD)"]
    

    def get_asset_price(self, post_asset_matchs, req_num, dev_mode=False) -> dict:    
        #Rate limiting
        if req_num == 0:
            logger.info("Rate Limit hit. Sleeping for 60 seconds")
            time.sleep(60)
            req_num = 5

        res = []
        #Now get the price for each item in the list
        for item in post_asset_matchs:
            created_at = str(item.post.created_at).split(" ")[0]
            ticker, asset_type = item.asset.ticker, item.asset.asset_type
            
            if_full = True if dev_mode else False
            price = None
            print(item.asset.ticker, item.asset.asset_type, item.asset.asset_name)
            if asset_type.lower() == 'stock':
                time.sleep(20)
                price = self._get_stock_prices_historic(ticker, created_at, True)
            elif asset_type.lower() == 'cryptocurrency':
                time.sleep(20)
                price = self._get_crypto_prices(ticker, created_at)
            else:
                return req_num, None
            
            req_num -= 1
            #Rate limiting stuff
            
            new_item = PostAssetMatch(item.post, item.asset, item.word_match, price)
            res.append(new_item)
        return req_num, res