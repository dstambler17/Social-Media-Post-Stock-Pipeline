import os
from src.clients.twitter_client import TwitterAPIClient

def test_main_script_twitter():
    twitter_keys = {
        "CONSUMER_KEY": os.environ.get('CONSUMER_KEY'),
        "CONSUMER_SECRET" : os.environ.get('CONSUMER_SECRET'),
        "ACCESS_KEY" : os.environ.get('ACCESS_KEY'),
        "ACCESS_SECRET" : os.environ.get('ACCESS_SECRET')
    }
    twitter_client = TwitterAPIClient(twitter_keys)
    res = twitter_client.get_user_tweets('elonmusk', None, True)
    assert len(res) > 0
