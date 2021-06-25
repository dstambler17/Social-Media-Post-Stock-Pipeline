import argparse
import logging.config
from src.config import logging_config
from src.clients.postgresql_client import PostgreSQLClient
from src.clients.redis_client import RedisClient
from src.Context import Context
from src.items.Tweet import Tweet

from src.reads.sql_reads import query_posts, query_posts_by_id
from src.writes.sql_writes import *
from src.writes.redis_writes import *

from src.main_info_classes.FinanceTextIdentifier import FinanceTextIdentifier
from src.main_info_classes.FinancePriceInfo import FinancePriceGetter
from src.main_info_classes.AssetManualFilter import AssetManualFilter
from src.main_info_classes.IdentifyAssetPosts import PostAssetExtractor
from src.main_info_classes.Transactor import Transactor

from src.utils.utils import PostAssetMatch, filter_uniq_items
from src.utils.custom_decorators import time_func
from src.machine_learning.SentimentAnalysis import SentimentAnalysis
from src.retrievers.Retrivers import get_latest_posts


def handle_price_identification_of_assets(sql_client: PostgreSQLClient, items: list, afm: AssetManualFilter, fpg: FinancePriceGetter, req_limit: int, no_writes: bool):
    '''
    Filters for unique assets in each identified post,
    then calls the api with the price
    calls the write functions and returns
    a tuple of the filtered items
    '''
    
    if not items:
        return None, req_limit

    if not no_writes:
        write_finance_posts(sql_client, items)

    #Apply filter
    filtered_list = afm.apply_filter(items)
    filtered_set, filtered_items = filter_uniq_items(filtered_list)
    
    req_limit, res = fpg.get_asset_price(filtered_items, req_limit, True)
    if res:
        if not no_writes:
            write_asset_post_with_price(sql_client, res)
        return (res, filtered_list), req_limit #Appends a tuple of unqiue words
    else:
        return None, req_limit

def match_assets_and_prices(posts, sql_client, redis_client, no_writes=False, price_api_request_limit=5):
    '''
    Steps 3 and 4 of the process
    Takes in a list of posts (ex: Tweets), matches keywords, applies filters,
    then gets the price
    returns a list of tuples :(list of matches, list of unique assets and price)
    '''
    fti = FinanceTextIdentifier(sql_client)
    afm = AssetManualFilter(sql_client, redis_client)
    fpg = FinancePriceGetter()
    logger = logging.getLogger(__name__)
    
    final_res = []
    for post in posts:
        items = PostAssetExtractor.extract_assets_from_post(post, sql_client, fti)
        res, price_api_request_limit = handle_price_identification_of_assets(sql_client, items, afm, fpg, price_api_request_limit, no_writes)
        if res is not None:
            final_res.append(res)

    logger = logging.getLogger(__name__)
    logger.info("Total Number of Posts with Asset names and prices: %d" % len(final_res))
    return final_res


def execute_transaction(sql_client, processed_items):
    """
    Takes in a list of tuples (asset_post_price list, filtered list)
    then for each one, gets the text and a list of keywords
    returns a prediction for each item
    """
    logger = logging.getLogger(__name__)
    logger.info('THESE ARE PROCESSED ITEMS')
    logger.info(processed_items)

    transactor = Transactor(sql_client)
    for item in processed_items:
        asset_prices, full_list = item
        for ap in asset_prices:
            keywords = [x.word_match for x in full_list if x.word_match == ap.word_match]
            prediction = SentimentAnalysis.analyze_text_sentiment(ap.post.post_text, keywords)
            if prediction is not None:
                transactor.make_purchase(ap, prediction) #Make the purchase

@time_func
def make_investment_from_post(context, source_id, platform_name, dev_mode, no_writes):
    '''
    LOGIC:
    1) Get last post date from redis (key being source_id)
        - If no result, query db for latest date, if still no, don't add any value
    2) Call tweet api logic, if data is returned, update redis (also write to db)
    3) Call "IdentifyPost Asset" to get the stock info on all posts
    4) For each result, get the unqiue tickers/asset types, then call the finance price api to get the price
        at the time the post was created
    5) for each post, call sentiment analysis logic (STILL NEEDS TO BE WRITTEN) to get pos or neg from post
    6) Either "BUY" or "SELL" (if you have that stock in the portfolio to begin with) (STILL NEEDS TO BE WRITTEN)
    '''

    sql_client, redis_client = context.sql_client, context.redis_client
    logger = logging.getLogger(__name__)

    post_list = get_latest_posts(context, source_id, platform_name, no_writes, dev_mode)
    if not post_list and not dev_mode:
        logger.info("NO NEW TWEETS, ENDING PROCESS")
        return
    if not post_list and dev_mode:
        post_list = query_posts_by_id(sql_client, Tweet, 1363021091086561285)
        logger.info(post_list)
        logger.info("Returning %d sample tweets for development" % len(post_list))

    #Save latest_date to redis    
    max_id = post_list[0].post_id
    if not no_writes:
        write_lastpost_username(redis_client, int(max_id), source_id)
    
    processed_items = match_assets_and_prices(post_list, sql_client, redis_client, no_writes=no_writes, price_api_request_limit=5)

    execute_transaction(sql_client, processed_items)
    logger.info('Finalizing Process')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dev_mode', action='store_true', help='Whether to run in debug dev mode or not')
    parser.add_argument('--no_writes', action='store_true', help='Whether to save to the DB or not')
    parser.add_argument('--conf_file', dest='config_file', help='Config file path')

    args=parser.parse_args()

    logging.config.dictConfig(logging_config)
    context = Context(args.config_file)

    account_names = context.account_names
    
    for account in account_names:
        make_investment_from_post(context, account['source_id'], account['platform_name'], args.dev_mode, args.no_writes)