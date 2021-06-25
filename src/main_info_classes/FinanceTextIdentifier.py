import logging

from src.reads.sql_reads import query_asset_data, query_nick_name_data
from src.clients.postgresql_client import PostgreSQLClient
from src.utils.custom_decorators import time_func


#Should be a singleton class
class FinanceTextIdentifier():
    def __init__(self, client):
        asset_data = query_asset_data(client)

        #We will use two lists, because cryptos share the same tickers as some stocks
        crypto_data = list(filter(lambda x: x['asset_type'] == 'Cryptocurrency', asset_data))
        stock_data = list(filter(lambda x: x['asset_type'] != 'Cryptocurrency', asset_data))

        #Build in memory tries
        self.crypto_trie = self.__build_asset_trie(crypto_data)
        self.stock_trie = self.__build_asset_trie(stock_data)

        #Build in memory id based lookups
        self.asset_id_lookup_dict = self.__build_lookup_dict(asset_data)

        #Get the list of manual nicknames/meme names to offical names
        self.nickname_lookups = query_nick_name_data(client)
    
    def __build_asset_trie(self, asset_data):
        '''
        Private method to build trie from ticker and asset_names
        Saving asset id as key
        '''
        trie = {}
        for asset in asset_data:
            asset_id, ticker, asset_name = asset['asset_id'], asset['ticker'], asset['asset_name'].strip()
            trie = self.__add_to_trie(trie, ticker, asset_id, True)
            trie = self.__add_to_trie(trie, asset_name, asset_id, False)
        return trie

    def __add_to_trie(self, trie, item, asset_id, is_ticker):
        '''
        Private method that adds item to trie
        Adds '__*__' as an end key
        '''
        #only convert non ticker names to lower
        #if not is_ticker:
        #    item = item.title()
        #SPECIAL RULE FOR ALL THOSE TWO WORD TICKERS THAT ARE ALMOST NEVER USED TO MENTION COMPANY NAMES
        if is_ticker and len(item) <= 2:
            return trie

        orig_trie = trie
        for char in list(item):
            if char not in trie:
                trie[char] = {}
            trie = trie[char]
  
        trie['__*__'] = asset_id
        return orig_trie

    def __build_lookup_dict(self, asset_data):
        '''
        Private method that builds a dict from a list of asset dicts
        '''
        return {x['asset_id']: x for x in asset_data}

    def __trie_lookup(self, word, look_up_stock):
        '''
        private method that checks if word is in trie
        '''
        lookup_trie = self.stock_trie if look_up_stock else self.crypto_trie
        for char in list(word):
            if char not in lookup_trie:
                return None
            lookup_trie = lookup_trie[char]
        
        if '__*__' in lookup_trie:
            return lookup_trie['__*__']
            
    @time_func
    def identify_mentioned_assets(self, word_list):
        '''
        Takes in a word_list as input
        then for each words, checks each trie for a hit
        if there's a hit, adds mentioned company to result list
        '''

        mentioned_assets = []
        for word in word_list:
            original_word = word
            word = word if word not in self.nickname_lookups else self.nickname_lookups[word] #replace nickname word if exists

            stock_match = self.__trie_lookup(word, True)
            crypto_match = self.__trie_lookup(word, False)
            if stock_match and crypto_match:
                #NOTE: this means that both were hit, log this, unsure what to do, as hard to tell, which one they meant
                print('NEED TO THINK MORE ON THIS ONE')
            if stock_match:
                mentioned_assets.append({'asset_info': self.asset_id_lookup_dict[stock_match], 'word_match': original_word})
            if crypto_match:
                mentioned_assets.append({'asset_info': self.asset_id_lookup_dict[crypto_match], 'word_match': original_word})
        return mentioned_assets

