import logging.config
from src.MainProccess import make_investment_from_post
from src.Context import Context
from src.config import logging_config


def test_main_script_twitter():
    logging.config.dictConfig(logging_config)
    context = Context('conf/twitter_bot_local.json')

    account_names = context.account_names
    
    process_end = False
    for account in account_names:
        make_investment_from_post(context, account['source_id'], account['platform_name'], True, True)
        process_end = True
    assert process_end