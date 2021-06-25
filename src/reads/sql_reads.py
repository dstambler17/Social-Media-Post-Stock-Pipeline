import logging
from src.clients.postgresql_client import PostgreSQLClient

logger = logging.getLogger(__name__)

def sql_columns_to_post_obj(client, table_name, records, cls):
    '''
    Takes in a table name, a list of tuple records and a post_object (like Post)
    Then converts the records to the appropriate post object
    '''
    columns = client.execute_query("""
        SELECT column_name
        FROM information_schema.columns
        where table_name   = '%s';
    """ % table_name)
    columns = [column[0] for column in columns]
    new_records = [list(zip(columns, entry)) for entry in records]

    post_obj = [cls(**dict(item)) for item in new_records]
    return post_obj

def query_posts_by_id(client, cls, post_id):
    sql = """
            select * from posts
            where post_id = %s
            and post_type = '%s'
        """ % (post_id, cls.__name__)
    res = client.execute_query(sql)
    post_list = sql_columns_to_post_obj(client, 'posts', res, cls)
    return post_list


def query_posts(client, cls, limit=None):
    '''
    Queries posts and converts them to the passed in object
    '''

    if limit is None:
        sql = """
            select * from posts
            where post_type = '{}'
        """.format(cls.__name__)
    else:
        sql = """
            select * from posts
            where post_type = '{}'
            order by created_at desc
            limit {}
        """.format(cls.__name__, limit)

    res = client.execute_query(sql)
    post_list = sql_columns_to_post_obj(client, 'posts', res, cls)

    return post_list


def query_asset_data(client):
    sql = '''
        select asset_id, ticker, asset_name, asset_type from  tradeable_assets
    '''
    res_tuple = client.execute_query(sql)
    return [{'asset_id': x[0], 'ticker': x[1], 'asset_name' :x[2].strip(),
            'asset_type': x[3]} for x in res_tuple]


def query_nick_name_data(client):
    sql = '''
        select ta.asset_name, n.nick_name from stock_nicknames n
            join tradeable_assets ta on ta.asset_id = n.asset_id
    '''
    res_tuple = client.execute_query(sql)
    return {asset_nick_name[1].strip() : asset_nick_name[0].strip() for asset_nick_name in res_tuple}


def query_filter_rules_sql(client):
   sql =  '''select username, 
            json_agg(
                    json_build_object('asset_ticker',asset_ticker, 'asset_type',asset_type)
            ) as filter_rules from manual_filter_rules
		group by username
        '''
   res_tuple = client.execute_query(sql)
   res = {x[0] : x[1] for x in res_tuple}
   return res


def get_latest_post_id(client, username):
    '''
    Given a username, get the latest post id
    '''
    sql = '''
        select post_id from posts order by created_at desc limit 1
    '''
    res_tuple = client.execute_query(sql)
    
    try:
        last_id = res_tuple[0][0]
    except:
        last_id = None
        logger.info('ERROR, NO post RECORD EXISTS FOR %s' % username)
    finally:
        return last_id

def query_holdings(client):
    sql = '''
        select asset_id, ticker, total_holding, total_shares
        from holdings
    '''
    res_tuple = client.execute_query(sql)
    return {x[0]: { 'ticker': x[1], 'total_holding' :x[2], 'total_shares': x[3]} for x in res_tuple}