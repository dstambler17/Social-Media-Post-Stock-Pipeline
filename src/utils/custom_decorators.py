import time
import logging

def time_func(func):
    logger = logging.getLogger(__name__)
    def inner(*args, **kwargs):
        t1 = time.time()
        f = func(*args, **kwargs)
        t2 = time.time()
        logger.info('Runtime for function {} took {} seconds'.format(func.__name__ ,str(t2-t1)))
        return f
    return inner