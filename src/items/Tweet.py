
import re
from src.items.Post import Post

class Tweet(Post):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__get_reply_user_name()

    def __get_reply_user_name(self):
        '''
        Checks if tweet is a reply and then gets reply username
        '''
        regex_pattern = re.compile(pattern = r'^@(.*?)\s', flags=re.IGNORECASE)
        res = regex_pattern.findall(self.post_text)
        if len(res) > 0:
            self.is_reply = True
            self.replying_to_handle = res[0]
        else:
            self.is_reply = False
            self.replying_to_handle = None

        
    