import logging
from src.Context import Context
from src.reads.redis_reads import read_lastpost_from_username
from src.writes.redis_writes import *
from src.clients.twitter_client import TwitterAPIClient
from src.writes.sql_writes import write_post_data_sql
from src.reads.sql_reads import sql_columns_to_post_obj, get_latest_post_id
from src.items.Tweet import Tweet

logger = logging.getLogger(__name__)


class PostRetriver:
    '''
    Handles the retriever calls for each different post retriver
    (So far we only have 1, Twitter, but can add others like Redis)
    '''
    @staticmethod
    def get_latest_tweets(sql_client, redis_client, username, twitter_keys, no_writes, dev_mode):
        '''
        Gets last tweet id from redis then tries SQL
        Gets all latest tweets, and writes them to SQL
        '''
        latest_post_id = None #int(read_lastpost_from_username(redis_client, username))
        
        if latest_post_id is None:
            latest_post_id = get_latest_post_id(sql_client, username)#Call SQL

        #If no data in SQL, we will just get the latest 200 tweets
        twitter_client = TwitterAPIClient(twitter_keys)
        tweet_batch = twitter_client.get_user_tweets(username, latest_post_id, False) if not dev_mode else []
        if tweet_batch and latest_post_id is not None:
            tweet_batch = tweet_batch[1:]
        
        if not no_writes:
            write_post_data_sql(sql_client, tweet_batch)
        print('TWEET BATCH')
        print(len(tweet_batch))
        tweet_batch = sql_columns_to_post_obj(sql_client, 'posts', tweet_batch, Tweet)

        logger.info("RETURNING %s new tweets", len(tweet_batch))
        return tweet_batch
    
def get_latest_posts(ctx : Context, source_id: str, platform_name: str, no_writes: bool, dev_mode: bool):
    if platform_name == 'twitter':
        print(platform_name)
        logger.info('Getting Latest Tweets from %s account' % source_id)
        if 'twitter_keys' not in ctx.config_file:
            raise ValueError("ERROR, Missing Curcial Config File info")
        return PostRetriver.get_latest_tweets(ctx.sql_client, ctx.redis_client, source_id, ctx.config_file['twitter_keys'], no_writes, dev_mode)
    else:
        logger.error('CANNOT RECOGNIZE NAME %s' % platform_name)
        return []