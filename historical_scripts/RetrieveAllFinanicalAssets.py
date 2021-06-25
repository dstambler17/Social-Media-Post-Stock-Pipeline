'''
Ideally, this script will give you a list of all public comps and tickers
'''

import requests
import json
import logging

from clients.postgresql_client import PostgreSQLClient
from writes.sql_writes import write_asset_data_sql

logger = logging.getLogger(__name__)

def get_asset_data(page, last_page):
    '''
    Queries public company ticker symbol and name
    '''
    url = 'https://assetdash.herokuapp.com/assets?currentPage={}&perPage=200&typesOfAssets[]=Stock&typesOfAssets[]=ETF&typesOfAssets[]=Cryptocurrency'.format(page)
    response = requests.get(url)
    res = response.json()
    if last_page == float('inf'):
        last_page = res['pagination']['lastPage']
        logger.info(last_page)
    
    data = [(item['id'], item['ticker'], item['name'],  item['type'], item['rank'], item['currentMarketcap'],
                 item['currentPrice']) for item in res['data']]
    return last_page, data


def get_all_tradeable_asset_data(sql_client):
    '''
    Runs the 'get all data api throughout all pages in pagination dict'
    This gets all ETF, top 70 crypto, and all public US stock data
    '''
    current_page, last_page = 1, float('inf') #initalize to inf, so that the first time, we can get the actual last_page
    while current_page <= last_page:
        logger.info('Attempting Page {}'.format(current_page))
        last_page, data = get_asset_data(current_page, last_page)
        write_asset_data_sql(sql_client, data)
        current_page += 1



if __name__ == '__main__':
    sql_client = PostgreSQLClient('ElonTweets', '127.0.0.1', 5432)
    get_all_tradeable_asset_data(sql_client)