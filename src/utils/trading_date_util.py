import calendar
import logging
from datetime import datetime
from pandas.tseries.offsets import BDay
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas import bdate_range
import pandas_market_calendars as mcal

nyse = mcal.get_calendar('NYSE')
logger = logging.getLogger(__name__)

#buisness day utils
def is_trading_day(date):
    month, year = date.month, date.year
    last_date_of_month = calendar.monthrange(year, month)[1] #getlast_date of month
    start = "%d-%d-01" % (year, month)
    end =  "%d-%d-%d" % (year, month, last_date_of_month)

    trading_days = nyse.schedule(start_date=start, end_date=end)
    trading_days = [str(x).split(" ")[0] for x in trading_days['market_open']]#clean the list
   
    return str(date).split(" ")[0] in trading_days


def is_business_day(date):
    return bool(len(bdate_range(date, date)))

def get_recent_trading_day(date_str):
    format = "%Y-%m-%d"
    dt_object = datetime.strptime(date_str, format)
    
    if not is_business_day(dt_object):
        dt_object = dt_object - BDay(1)
    
    if is_trading_day(dt_object):
        #logger.info(dt_object)
        return dt_object
    else:
        #logger.info(dt_object - BDay(1))
        return dt_object - BDay(1)


#if __name__ == "__main__":
#    get_recent_trading_day('2021-09-06')