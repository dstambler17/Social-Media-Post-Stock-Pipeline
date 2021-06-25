from src.clients.postgresql_client import PostgreSQLClient
from src.clients.redis_client import RedisClient

from src.reads.sql_reads import query_posts
from src.main_info_classes.FinanceTextIdentifier import FinanceTextIdentifier
from src.main_info_classes.AssetManualFilter import AssetManualFilter
from src.main_info_classes.IdentifyAssetPosts import PostAssetExtractor
from src.items.Tweet import Tweet

def test_asset_manual_filter():    
    redis_client = RedisClient()
    sql_client = PostgreSQLClient('ElonTweets', '127.0.0.1', 5432)
    afm = AssetManualFilter(sql_client, redis_client)
    assert 'elonmusk' in afm.filter_rules

    fti = FinanceTextIdentifier(sql_client)
    tweets = query_posts(sql_client, Tweet, 500)

    filter_items_hit = False
    for tweet in tweets:
        items = PostAssetExtractor.extract_assets_from_post(tweet, sql_client, fti)
        filter_items = afm.apply_filter(items)
        if filter_items:
            filter_items_hit = True
    assert filter_items_hit