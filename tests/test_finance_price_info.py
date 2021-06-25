from src.utils.utils import PostAssetMatch
from src.items.Transaction import Transaction
from src.items.Asset import Asset
from src.items.Tweet import Tweet
from src.main_info_classes.FinancePriceInfo import FinancePriceGetter

def test_finance_price_info_crypto():
    #sql_client = PostgreSQLClient('ElonTweets', '127.0.0.1', 5432)

    tweet = Tweet(**{'post_id': 12345, 'created_at': '2021-05-01', 'post_text':'HI BTC'})
    a = Asset(**{'asset_id':234567, 'ticker': 'BTC', 'asset_type':'cryptocurrency'})
    tams = [PostAssetMatch(tweet, a, 'BTC', None)]
    fpg = FinancePriceGetter()
    _, res = fpg.get_asset_price(tams, 5, True)
    crypto_price = float(res[0].price_at_time) // 1
    assert crypto_price == 57800

def test_finance_price_info_stock():
    tweet = Tweet(**{'post_id': 12345, 'created_at': '2021-05-01', 'post_text':'HI TESLA'})
    a = Asset(**{'asset_id':234567, 'ticker': 'TSLA', 'asset_type':'stock'})
    tams = [PostAssetMatch(tweet, a, 'TSLA', None)]
    fpg = FinancePriceGetter()
    _, res = fpg.get_asset_price(tams, 5, True)
    stock_price = float(res[0].price_at_time) // 1
    assert stock_price == 709

def test_get_current_prices():
    fpg = FinancePriceGetter()
    current_stock_price = fpg.get_current_stock_price('TSLA')

    assert current_stock_price is not None
    current_crypto_price = fpg.get_current_crypto_price('BTC')
    assert current_crypto_price is not None
    