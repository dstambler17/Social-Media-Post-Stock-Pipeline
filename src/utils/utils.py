import re
from datetime import datetime
from collections import namedtuple

from nltk.corpus import stopwords
from src.constants import REGEX_PATTERNS
stop_words=set(stopwords.words('english'))
stop_words.update({'now', 'one', 'best', 'nice', 'regions', 'iii', 'jd', 'gps'}) #found these unheard of companies with common word names or tickers

PostAssetMatch = namedtuple('PostAssetMatch', ['post', 'asset', 'word_match', 'price_at_time'])

def convert_time_string(post_timestamp):
    new_datetime = datetime.strftime(datetime.strptime(post_timestamp,'%a %b %d %H:%M:%S +0000 %Y'), '%Y-%m-%d %H:%M:%S')
    return new_datetime

def convert_to_postgres_list(string_list):
    new_list = str(map(str, string_list))
    new_list = new_list.replace('[', '{').replace(']', '}').replace('\'', '\"')
    return new_list

def format_symbol_list(tweet_comps):
    return [symbol['text'] for symbol in tweet_comps]

def identify_retweet(text):
    if text.lower().startswith("rt @"):
        return True
    return False

def uniq(lst):
    last = ('BLAH')
    for item in lst:
        if item[0] == last[0]:
            continue
        yield item
        last = item

def regex_replace(text, item_to_replace):
    regex_pattern = REGEX_PATTERNS[item_to_replace]
    return regex_pattern.sub(r'', text)

def remove_stop_words(text):
    '''
    Removes generic words from body of text
    '''
    return " ".join(list(filter(lambda w: not w.lower() in stop_words, text.split())))

def print_class(params_dict, object_name):
    res = "%s : { "% object_name
    for k, v in params_dict.items():
        res += "{} : {}, ".format(k,v)
    res += '}'
    return res

def filter_uniq_items(asset_matches):
    #Filter logic
    filtered_set = set()
    filtered_list = []
    for tam in asset_matches:
        key = str(tam.post.post_id) + '-' + str(tam.asset.asset_id)
        if key not in filtered_set:
            filtered_set.add(key)
            filtered_list.append(tam)
    return filtered_set, filtered_list