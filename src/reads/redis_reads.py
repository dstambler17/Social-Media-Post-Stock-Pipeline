import pickle
from src.clients.redis_client import RedisClient
from src.constants import TUPLE_SPLIT_CHARS, TWEET_SPLIT_CHARS

def read_all_tweets_redis(client, key):
    serialized_list = client.read(key)
    new_list = serialized_list.decode('utf-8').split(TWEET_SPLIT_CHARS)
    new_str_list = [x.split(TUPLE_SPLIT_CHARS) for x in new_list]
    #convert id object to int and str list to list
    for item in new_str_list:
        item[0] = int(item[0])
        item[3] = eval(item[3]) #eval converts stringified list to normal list
    return new_str_list

def read_lastpost_from_username(client, username):
    return client.read(username)

def read_filter_rules(client, key):
    filter_rules = client.read(key)
    if filter_rules is not None:
        filter_rules = pickle.loads(filter_rules)
    return filter_rules