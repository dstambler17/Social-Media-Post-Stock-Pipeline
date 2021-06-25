from src.reads.redis_reads import read_filter_rules
from src.writes.redis_writes import write_filter_rules
from src.reads.sql_reads import query_filter_rules_sql

class AssetManualFilter:
    def __init__(self, sql_client, redis_client):
        self.filter_rules = self.__get_filter_rules(sql_client, redis_client)

    def __get_filter_rules(self, sql_client, redis_client):
        '''
        Hit redis, if not exists, then hit SQL and write to redis
        '''
        rules = read_filter_rules(redis_client, 'filter_rules')
        if rules is None or not rules:
            rules = query_filter_rules_sql(sql_client)
            write_filter_rules(redis_client, 'filter_rules', rules)
        return rules
    
    def __check_if_filters_hit(self, user_rules, ticker, asset_type):
        for rule in user_rules:
            if rule['asset_ticker'] == ticker and rule['asset_type'] == asset_type:
                return True
        return False

    def apply_filter(self, items):
        '''
        Applies custom filters to the retrived assets
        Ex: exclude TSLA for elon musk
        '''
        if not items:
            return []
        filtered_list = []
        for item in items:
            username = item.post.username
            ticker, asset_type = item.asset.ticker, item.asset.asset_type
            if username not in self.filter_rules:
                filtered_list.append(item)
                continue

            user_rules = self.filter_rules[username]
            if not self.__check_if_filters_hit(user_rules, ticker, asset_type):
                filtered_list.append(item)
        return filtered_list
