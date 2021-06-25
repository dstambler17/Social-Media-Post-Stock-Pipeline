from src.utils.utils import print_class

class Asset:
    def __init__(self, **kwargs):
        '''asset_id, ticker, asset_name, asset_type'''
        self.__dict__.update(kwargs) #gives asset object more flexibility
    
    def __str__(self):
        return print_class(self.__dict__, self.__class__.__name__)