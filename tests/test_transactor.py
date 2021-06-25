from src.utils.utils import PostAssetMatch
from src.items.Transaction import Transaction
from src.items.Asset import Asset
from src.items.Tweet import Tweet
from src.clients.postgresql_client import PostgreSQLClient
from src.main_info_classes.Transactor import Transactor

def _test_buy_sell_holdings(transactor, tam, prediction):
    transactor.make_purchase(tam, prediction)

def test_transactor():
    sql_client = PostgreSQLClient('ElonTweets', '127.0.0.1', 5432)

    tweet = Tweet(**{'post_id': 12345, 'created_at': '2021-05-01', 'post_text':'HIIII'})
    a = Asset(**{'asset_id':234567, 'ticker': 'DOGE'})
    tam = PostAssetMatch(tweet, a, 'Dogefather', 0.42)
    transactor = Transactor(sql_client)

    _test_buy_sell_holdings(transactor, tam, 0.95) #Test buy a lot
    _test_buy_sell_holdings(transactor, tam, 0.55) #Test buy a little
    _test_buy_sell_holdings(transactor, tam, 0.45) #Test sell a little
    _test_buy_sell_holdings(transactor, tam, 0.2) #Test sell a lot