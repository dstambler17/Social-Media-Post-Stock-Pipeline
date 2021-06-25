import re
from collections import namedtuple

#Chars by which to split the tweet
TUPLE_SPLIT_CHARS = '****'
TWEET_SPLIT_CHARS = '||||'

#Number of consecutive times the bot is willing to retry querying tiwtter before exiting
TWITTER_API_RETRY_TIME = 3 #

#List of tickers to exclude
#Sometimes we don't want to include companies like Tesla
EXCLUDE_TICKERS = ['TSLA']

#Essential tweet keys
#These are needed to be present in the SQL tweet table for
#the tweet object to materialize
ESSENTIAL_KEYS = ['post_id', 'created_at', 'post_text']

#Contains compiled regex patterns
REGEX_PATTERNS = {
    'emojis' : re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags from iOS
                           "]+", flags = re.UNICODE),
    'retweets' : re.compile(pattern = "^RT @.*?:", flags = re.IGNORECASE),
    'urls' : re.compile(pattern = r'https?:\/\/.*[\r\n]*', flags=re.MULTILINE),
    'replies' : re.compile(pattern = r'@.*?\s', flags=re.MULTILINE),
    'punctuation' : re.compile(pattern= r'[\.,!?]+?', flags=re.MULTILINE)
}
