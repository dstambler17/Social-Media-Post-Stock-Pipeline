import time
import requests
import json
import random
import logging
import os 

from src.config import logging_config
from clients.twitter_client import TwitterAPIClient
from clients.redis_client import RedisClient
from clients.postgresql_client import PostgreSQLClient

from writes.sql_writes import write_post_data_sql

from src.utils.utils import uniq
from src.constants import TWITTER_API_RETRY_TIME

logger = logging.getLogger(__name__)

def handle_tweet_writes(username, data):
    '''
    Writes tweets to different services
    '''
    logger = logging.getLogger(__name__)

    logger.info(data)
    logger.info('Writing Tweets between {} and {}'.format(data[0][1], data[-1][1]))
    sql_client = PostgreSQLClient('ElonTweets', '127.0.0.1', 5432)
    write_post_data_sql(sql_client, data)


def handle_tweet_api_timeouts_retry(tweet_batch, retry_time):
    '''
    Checks if proper number of results were returned
    '''
    logger = logging.getLogger(__name__)

    request_blocked = False
    if len(tweet_batch) < 5:
        logger.info("less than batch, trying again")
        retry_time -= 1
        time.sleep(14)
        request_blocked = True
    return request_blocked, retry_time
        
    

def get_all_user_tweets(twitter_client):
    '''
    gets around the api query size limit by
    sending multiple requests with since id.
    Sleeps to avoid being rate limited
    '''
    logger = logging.getLogger(__name__)
    EARLIEST_YEAR = 2018 #set this to tell it when to stop
    isRunning, max_id, retry =  True, None, TWITTER_API_RETRY_TIME
    while isRunning:
        tweet_batch = twitter_client.get_user_tweets('elonmusk', max_id, True)
        #To avoid writing dups in the DB
        if max_id is not None:
            tweet_batch = tweet_batch[1:]

        #Get around twitter api sometimes returning no results (to block bots like this one)
        request_blocked, retry = handle_tweet_api_timeouts_retry(tweet_batch, retry)
        if request_blocked:
            if retry <= 0:
                break
            continue
    
        retry = TWITTER_API_RETRY_TIME #reset retry time
        handle_tweet_writes('elonmusk', tweet_batch)

        date_str, max_id = tweet_batch[-1][1], tweet_batch[-1][0]
        if int(date_str.split('-')[0]) < EARLIEST_YEAR:
            isRunning = False
        else:
            logger.info('Sleeping')
            time.sleep(100)

    #res =  list(uniq(sorted(res, key=lambda x: x[1]))) #remove duplicates
    '''
    Note for fixing this tweet retriver:
        Write each tweet batch one at a time (to postgres), instead of all at once (then we would know which batch fails)
        That way, we can get to end of 2017 batch
    '''


if __name__ == "__main__":
    logging.config.dictConfig(logging_config)
    twitter_keys = {
        "CONSUMER_KEY": os.environ.get('CONSUMER_KEY'),
        "CONSUMER_SECRET" : os.environ.get('CONSUMER_SECRET'),
        "ACCESS_KEY" : os.environ.get('ACCESS_KEY'),
        "ACCESS_SECRET" : os.environ.get('ACCESS_SECRET')
    }
    twitter_client = TwitterAPIClient(twitter_keys)
    get_all_user_tweets(twitter_client)
    
    #twitter_client.get_user_tweets()
