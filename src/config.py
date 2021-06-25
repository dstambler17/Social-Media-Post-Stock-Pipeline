import os
from datetime import datetime

now = datetime.now()
log_file_name = 'application_%s.log' % (now.strftime("%m-%d-%Y_%H-%M-%S"))

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'default_handler': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': os.path.join('logs', log_file_name),
            'encoding': 'utf8'
        },
    },
    'loggers': {
        '': {
            'handlers': ['default_handler'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

if __name__ == "__main__":
    print(log_file_name)