from src.constants import ESSENTIAL_KEYS
from src.utils.utils import print_class

class Post:
    '''
    The parent object of all post classes include Tweets, Reddit Posts, YT_Comments etc
    '''
    def __init__(self, **kwargs):
        """
        post_id, created_at, post_text, symbols, username, images, is_truncated, is_retweet
        """
        self.__dict__.update(kwargs) #gives tweet object more flexibility
        self.__check_essential_types()
        #self.__convert_types()

    def __check_essential_types(self):
        '''
        Checks that the right types entered the dict
        '''
        for key in ESSENTIAL_KEYS:
            if key not in self.__dict__:
                raise ValueError("ERROR: Make sure the sql table has the following columns {}".format(", ".join(ESSENTIAL_KEYS)))

    def __convert_types(self):
        '''
        Converts decimal id to regular int id
        '''
        self.post_id = int(float(self.post_id))
    
    def __str__(self):
        return print_class(self.__dict__, self.__class__.__name__)