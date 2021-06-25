from src.clients.postgresql_client import PostgreSQLClient
from src.main_info_classes.FinanceTextIdentifier import FinanceTextIdentifier

def test_finance_price_info_crypto():
    sql_client = PostgreSQLClient('ElonTweets', '127.0.0.1', 5432)
    fti = FinanceTextIdentifier(sql_client)
    flagged_assets = fti.identify_mentioned_assets(['Tesla', 'AAVE', 'aapl', 'test comp', 'inc incorporated', 'Apple', 'ether', 'gamestonks'])

    res = [x['asset_info']['ticker'] for x in flagged_assets]
    assert len(res) == 5
    assert 'TSLA' in res
    assert 'AAVE' in res
    assert 'AAPL' in res
    assert 'GME' in res
    assert 'ETH' in res

    