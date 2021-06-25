import logging
from src.utils.utils import PostAssetMatch
from src.items.Transaction import Transaction
from src.reads.sql_reads import query_holdings
from src.writes.sql_writes import write_transaction, insert_new_holdings_data, delete_holdings_data, update_holdings_data
from src.clients.postgresql_client import PostgreSQLClient

logger = logging.getLogger(__name__)

class Transactor:
    def __init__(self, sql_client):
        self.high_purchase_amount = 500 #HARDCODE FOR NOW
        self.mid_amount = 200 #HARDCODE FOR NOW
        self.holdings = query_holdings(sql_client)
        self.sql_client = sql_client


    def __calculate_shares_transacted(self, share_price, purchase_price):
        return purchase_price/share_price


    def __determine_transaction_amount(self, prediction: float) -> (int, bool):
        '''
        Based on the prediction, determine if we buy or sell, and how much
        '''
        if prediction >= 0.65:
            amount, buy = self.high_purchase_amount, True
        elif prediction >= 0.5 and prediction < 0.65:
            amount, buy = self.mid_amount, True
        elif prediction >= 0.35 and prediction < 0.5:
            amount, buy = self.mid_amount, False
        else:
            amount, buy = self.high_purchase_amount, False
        return amount, buy


    def __buy_holding(self, holdings_dict: dict, tran: Transaction):    
        
        shares_transacting, amount= holdings_dict['total_shares'], holdings_dict['total_holding']
        
        if holdings_dict['asset_id'] not in self.holdings:
            insert_new_holdings_data(self.sql_client, holdings_dict)
        else:
            holdings_dict['total_shares'] += float(self.holdings[holdings_dict['asset_id']]['total_shares']) #Add amount and shares
            holdings_dict['total_holding'] += float(self.holdings[holdings_dict['asset_id']]['total_holding']) #Add amount and shares

            update_holdings_data(self.sql_client, holdings_dict)
        tran.transaction_type = 'BUY'
        write_transaction(self.sql_client, tran)
        logger.info('BOUGHT %f shares of %s for %d' % (shares_transacting, holdings_dict['ticker'], amount))
    

    def __sell_holding(self, holdings_dict: dict, tran: Transaction):
        shares_transacting, amount= holdings_dict['total_shares'], holdings_dict['total_holding']

        if holdings_dict['asset_id'] in self.holdings:
            holding_amount = self.holdings[holdings_dict['asset_id']]['total_holding']

            if holdings_dict['total_holding'] >= holding_amount:
                holdings_dict['total_holding'] = holding_amount
                delete_holdings_data(self.sql_client, holdings_dict)
                logger.info('COMPLETELY SOLD OUT OF %s' % holdings_dict['ticker'])
            else:
                #Subtract amount and shares
                holdings_dict['total_shares'] = float(self.holdings[holdings_dict['asset_id']]['total_shares']) - holdings_dict['total_shares'] 
                holdings_dict['total_holding'] = float(self.holdings[holdings_dict['asset_id']]['total_holding']) -  holdings_dict['total_holding']
                update_holdings_data(self.sql_client, holdings_dict)

            tran.transaction_type = 'SELL'
            write_transaction(self.sql_client, tran)
            logger.info('SOLD %d shares of %s for %d' % (shares_transacting, holdings_dict['ticker'], amount))  

        else:
            logger.info('NO RECORD OF ASSET %s, id: %d, holdings will not update' % (holdings_dict['ticker'], holdings_dict['asset_id']))


    def __update_holdings(self, holdings_dict: dict, tran: Transaction, buy: bool):
        '''
        Updates the holdings table
        '''
        if buy:
            self.__buy_holding(holdings_dict, tran)
        else:
            self.__sell_holding(holdings_dict, tran)

    def make_purchase(self, ap: PostAssetMatch, prediction: float):
        '''
        Executes transaction. For sell transactions checks if the asset is held before selling
        If buying, put (fake) '$500' worth into the asset (for now, maybe later different prediction levels will result
        in more varried buy/sell stratagies, or even "shorts"),
        calculate how much of the asset you are buying, then write to two tables 1) Transactions, 2) Holdings
        '''
        
        amount, buy = self.__determine_transaction_amount(prediction)
        shares = self.__calculate_shares_transacted(float(ap.price_at_time), amount)

        holdings_dict = {'total_shares': shares, 'total_holding': amount,
                         'ticker': ap.asset.ticker, 'asset_id': ap.asset.asset_id}
        t = Transaction(**{'post_source_id': ap.post.post_id, 
                            'asset_id': ap.asset.asset_id, 'ticker' : ap.asset.ticker,
                            'transaction_type': None, 'transaction_date': ap.post.created_at, 
                            'transaction_amount': amount, 'shares': shares})
        
        self.__update_holdings(holdings_dict, t, buy)
        logger.info('TRANSACTION COMPLETE')
