from src.utils.utils import print_class

class Transaction:
    def __init__(self, **kwargs):
        '''post_source_id, asset_id, ticker,
        transaction_type, transaction_date transaction_amount shares'''
        self.__dict__.update(kwargs) #gives transaction object more flexibility
    
    def __str__(self):
        return print_class(self.__dict__, self.__class__.__name__)