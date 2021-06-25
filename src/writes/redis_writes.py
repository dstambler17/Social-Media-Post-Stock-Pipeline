import pickle
from src.clients.redis_client import RedisClient
from src.constants import TUPLE_SPLIT_CHARS, TWEET_SPLIT_CHARS

def write_all_tweets_redis(client, username, tweets):
    new_list = [TUPLE_SPLIT_CHARS.join([str(y) for y in x]) for x in tweets]
    serialized_list = TWEET_SPLIT_CHARS.join(new_list)
    client.write(username, serialized_list)

def write_lastpost_username(client, post_id, username):
    client.write(username, post_id)

def write_filter_rules(client, key, filter_rules):
    p_mydict = pickle.dumps(filter_rules)
    client.write(key, p_mydict)