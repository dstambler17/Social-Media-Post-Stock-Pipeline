import tweepy
import json
import logging

from src.utils.utils import *
from src.utils.custom_decorators import time_func

logger = logging.getLogger(__name__)

class TwitterAPIClient:
    def __init__(self, twitter_keys):
        self._client = self.handle_auth(twitter_keys)

    def handle_auth(self, twitter_keys):
        auth = tweepy.OAuthHandler(twitter_keys['CONSUMER_KEY'], twitter_keys['CONSUMER_SECRET'])
        auth.set_access_token(twitter_keys['ACCESS_KEY'], twitter_keys['ACCESS_SECRET'])
        api = tweepy.API(auth)
        #help(api)
        return api

    def update_status(self, text):
        '''
        test method
        '''
        self._client.update_status(text)
    
    def get_user(self, user='elonmusk'):
        '''
        Gets user info
        '''
        res = self._client.get_user(user)
        logger.info(json.dumps(res._json))
    
    @time_func
    def get_user_tweets(self, user='elonmusk', first_id=None, get_tweets_before=True):
        '''
        Gets user timeline and list of tweets
            reference: https://developer.twitter.com/en/docs/tweets/timelines/api-reference/get-statuses-user_timeline
            allowed_param: 'id', 'user_id', 'screen_name', 'since_id',
                      'max_id', 'count', 'include_rts', 'trim_user',
                      'exclude_replies'

        relevant results: created_at, id, full_text, entities/symbols, images, 
        '''
        res = []
        if get_tweets_before:
            tweepy_cusor = tweepy.Cursor(self._client.user_timeline, screen_name=user, tweet_mode="extended", count=200, max_id = first_id).items()
        else:
            tweepy_cusor = tweepy.Cursor(self._client.user_timeline, screen_name=user, tweet_mode="extended", count=200, since_id = first_id).items()

        for status in tweepy_cusor:
            logger.info("%d id create time: %s" % (status.id, status.created_at))
            images = []
            if 'media' in status.entities:
                for media in status.extended_entities['media']:
                    logger.info(media)
                    images.append(media['media_url'])
            tweet_obj = (status.id, datetime.strftime(status.created_at, '%Y-%m-%d %H:%M:%S'), status.full_text, 
                            format_symbol_list(status.entities['symbols']), user, 
                            images, status.truncated, identify_retweet(status.full_text), 'Tweet')
            res.append(tweet_obj)
                
        return res
