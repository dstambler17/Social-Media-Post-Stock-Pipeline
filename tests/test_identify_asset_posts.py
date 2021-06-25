from src.utils.utils import PostAssetMatch
from src.items.Transaction import Transaction
from src.items.Asset import Asset
from src.items.Tweet import Tweet

from src.clients.postgresql_client import PostgreSQLClient

from src.reads.sql_reads import query_posts, query_posts_by_id

from src.main_info_classes.FinanceTextIdentifier import FinanceTextIdentifier
from src.main_info_classes.IdentifyAssetPosts import PostAssetExtractor

from src.utils.utils import PostAssetMatch, filter_uniq_items

def test_identify_asset_post():
    sql_client = PostgreSQLClient('ElonTweets', '127.0.0.1', 5432)
    fti = FinanceTextIdentifier(sql_client)

    posts = query_posts(sql_client, Tweet, 500)

    res = []
    for post in posts:
        items = PostAssetExtractor.extract_assets_from_post(post, sql_client, fti)
        res += items
    assert len(res) > 0

def test_identify_asset_post_with_ocr():
    sql_client = PostgreSQLClient('ElonTweets', '127.0.0.1', 5432)
    fti = FinanceTextIdentifier(sql_client)

    post = query_posts_by_id(sql_client, Tweet, 1366820931184717824)[0]
    post.images[0] = 'https://pbs.twimg.com/media/E1OEK8jVEAMEv5A?format=jpg&name=medium' #Set this image manually
    items = PostAssetExtractor.extract_assets_from_post(post, sql_client, fti)
    assert 'intend to use it for transactions' in items[0].post.post_text
        
