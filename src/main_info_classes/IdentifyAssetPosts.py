import logging

from src.items.Asset import Asset
from src.items.Post import Post

from src.utils.utils import regex_replace, remove_stop_words, PostAssetMatch
from src.main_info_classes.FinanceTextIdentifier import FinanceTextIdentifier
from src.machine_learning.OCR import OCR
from src.clients.postgresql_client import PostgreSQLClient
from src.utils.custom_decorators import time_func

class PostAssetExtractor():
    '''
    This class does the following things to a post:
        1) Cleans the post text
        2) Generates different text varients of the post
        3) Tries to caption images/extract text from images (OPTIONAL)
        4) Passes all text through the FinanceTextIdentifier
        5) Excludes certain stock mentions (like TSLA, manually added here)
    '''
    @staticmethod
    def __sliding_window_words(word_list, window_size=3):
        '''
            gets all pairs of words within a 
            list based on the sliding window size
        '''
        i, j = 0, 1
        res = []
        while i < len(word_list):
            while j <= i + window_size and j <= len(word_list):
                word_combo = ' '.join(word_list[i:j])
                res.append(word_combo)
                j += 1
            i += 1
            j = i + 1
        return res

        
    @staticmethod    
    def __generate_text_variant(post_text):
        '''
            generates list of text combos (of up to five words)
            using a sliding window of sorts
        '''
        lines = post_text.split #split on new line as company/currency names will not be mentioned in different lines
        lines = post_text.split('\n')
        variants = []
        for line in lines:
            line = line.strip()
            if len(line) > 0:
                words = line.split(' ') #TODO: Replace with re.splits
                res = PostAssetExtractor.__sliding_window_words(words)
                variants += res
        return variants

        
    @staticmethod
    def __clean_text(text):
        '''
        remove images links, symbols, and @reply from post
        removes emojis
        removes generic words
        '''

        clean_text = regex_replace(
            regex_replace(
                regex_replace(
                    regex_replace(
                        regex_replace(text, 'emojis')
                    , 'urls')
                , 'retweets')
            , 'replies')
        , 'punctuation')
       
        clean_text_no_stop = remove_stop_words(clean_text)
        return clean_text_no_stop.strip()
    
    @staticmethod
    def handle_symbol_matches(symbols: list, fti : FinanceTextIdentifier):
        '''
        For each symbol, match it to the right asset (cause each symbol is a stock)
        '''
        res =  fti.identify_mentioned_assets(symbols)
        return res
    
    @staticmethod
    @time_func
    def __add_image_text(post):
        '''
        If the post object has image urls, then process them through OCR
        Then tack on the results (if any) to the post text
        '''
        if 'images' not in post.__dict__:
            return post
        
        for image_url in post.images:
            ocr_text = OCR.get_text_from_image(image_url)
            if ocr_text is not None:
                post.post_text = post.post_text + '\n' + ocr_text
        return post
    
    @staticmethod
    @time_func
    def extract_assets_from_post(post : Post, sql_client : PostgreSQLClient, fti : FinanceTextIdentifier):
        '''
        identifies assets mentioned in the post
        '''
        post = PostAssetExtractor.__add_image_text(post)
        post_text = PostAssetExtractor.__clean_text(post.post_text)
        word_combos = PostAssetExtractor.__generate_text_variant(post_text)
        
        res = fti.identify_mentioned_assets(word_combos)
        res += PostAssetExtractor.handle_symbol_matches(post.symbols, fti)

        return [PostAssetMatch(post, Asset(**item['asset_info']), item['word_match'], None) for item in res]

