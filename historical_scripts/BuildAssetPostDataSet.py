from src.clients.postgresql_client import PostgreSQLClient
from src.clients.redis_client import RedisClient

from src.reads.sql_reads import query_posts
from src.writes.sql_writes import write_finance_posts, write_asset_post_with_price

from src.main_info_classes.FinanceTextIdentifier import FinanceTextIdentifier
from src.main_info_classes.FinancePriceInfo import FinancePriceGetter
from src.main_info_classes.AssetManualFilter import AssetManualFilter
from src.main_info_classes.IdentifyAssetPosts import PostsAssetExtractor

from src.utils.utils import PostAssetMatch, filter_uniq_items
from src.items.Tweet import Tweet


if __name__ == "__main__":
    redis_client = RedisClient()
    sql_client = PostgreSQLClient('ElonTweets', '127.0.0.1', 5432)
    fti = FinanceTextIdentifier(sql_client)
    afm = AssetManualFilter(sql_client, redis_client)
    fpg = FinancePriceGetter()

    tweets = query_posts(sql_client, Tweet)
    req_num = 5

    final_res = []
    for tweet in tweets:
        items = PostAssetExtractor.extract_assets_from_post(tweet, sql_client, fti)
        if items:
            write_finance_posts(sql_client, items)
            print(tweet.post_id)
            filtered_set, filtered_list = filter_uniq_items(items)
            filtered_items = afm.apply_filter(filtered_list)
            
            req_num, res = fpg.get_asset_price(filtered_items, req_num, True)
            if res:
                write_asset_post_with_price(sql_client, res)

            final_res += res
    print(len(final_res))
