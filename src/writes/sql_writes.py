import logging
from src.clients.postgresql_client import PostgreSQLClient

logger = logging.getLogger(__name__)

def write_post_data_sql(client, post_data):
    if not post_data:
        return
    sql = '''
        INSERT INTO 
        posts (post_id, created_at, post_text, symbols, username, images, truncated, is_retweet, post_type) 
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    client.execute_many_writes_sql(sql, post_data)
    logger.info("WROTE %d new Post records" % len(post_data))

def write_asset_data_sql(client, stock_data):
    sql = '''
        INSERT INTO
        tradeable_assets (asset_id, ticker, asset_name, asset_type, current_rank, current_market_cap, current_price)
        VALUES(%s, %s, %s, %s, %s, %s, %s)
    '''
    client.execute_many_writes_sql(sql, stock_data)

def write_finance_posts(client, data):
    write_data = [(item.post.post_id, item.asset.asset_id, item.word_match) for item in data]
    sql = '''
        INSERT INTO
        finance_posts(post_id, asset_id, matched_word)
        VALUES(%s, %s, %s)
    '''
    client.execute_many_writes_sql(sql, write_data)
    logger.info("WROTE %d new Finance Match records" % len(data))

def write_asset_post_with_price(client, data):
    write_data = [(
                    item.post.post_id,
                    item.asset.asset_id,
                    item.word_match,
                    item.price_at_time,
                    item.post.created_at,
                    True
                  ) for item in data]

    sql = '''
        INSERT INTO
        identified_asset_post_with_price
        (post_id, asset_id, matched_word, asset_price_at_time, post_date, is_last_market_close_price)
        VALUES(%s, %s, %s, %s, %s, %s)
    '''
    client.execute_many_writes_sql(sql, write_data)
    logger.info("WROTE %d new matched asset price records" % len(data))


def write_transaction(client, transaction):
    write_data = (
                    transaction.post_source_id,
                    transaction.asset_id,
                    transaction.ticker,
                    transaction.transaction_type,
                    transaction.transaction_date,
                    transaction.transaction_amount,
                    transaction.shares
                  )
    sql = '''
        INSERT INTO
        transactions
        (post_source_id, asset_id, ticker, transaction_type, transaction_date, transaction_amount, shares)
        VALUES(%s, %s, %s, %s, %s, %s, %s)
    '''
    client.execute_write_sql(sql, write_data)
    logger.info("WROTE one new transaction records")


def insert_new_holdings_data(client : PostgreSQLClient, entry : dict):
    sql = '''
        INSERT INTO
        holdings
        (asset_id, ticker, total_holding, total_shares)
        VALUES(%s, %s, %s, %s)
    '''
    insert_data = (entry['asset_id'], entry['ticker'], entry['total_holding'], entry['total_shares'])
    client.execute_write_sql(sql, insert_data)
    logger.info("ADDED new holding record for ticker: %s" % entry['ticker'])


def delete_holdings_data(client : PostgreSQLClient, entry : dict):
    sql = '''
        DELETE FROM
        holdings
        Where asset_id = %s and ticker = %s 
    '''
    remove_data = (entry['asset_id'], entry['ticker'])
    client.execute_write_sql(sql, remove_data)
    logger.info("DELETED holding record for ticker: %s" % entry['ticker']) 


def update_holdings_data(client : PostgreSQLClient, entry : dict):
    sql = '''
        UPDATE
        holdings
        SET total_holding = %s, total_shares = %s
        WHERE asset_id = %s and ticker = %s 
    '''
    update_data = (entry['total_holding'], entry['total_shares'], entry['asset_id'], entry['ticker'])
    client.execute_write_sql(sql, update_data)
    logger.info("UPDATED holding record for ticker: %s" % entry['ticker'])

