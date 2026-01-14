import logging
import os
from datetime import datetime

def logging_function(prefix, timestamp):
    '''
    Designed for logging
    
    :param prefix: For folder name of lof
    :param timestamp: for name of log files
    '''

    dir = f'{prefix}_logs'
    os.makedirs(dir, exist_ok=True)

    log_filename = f"{dir}/{timestamp}.log"

    # Configure logs to retrieve INFO messages and higher
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        filename=log_filename
    )

    return logging.getLogger()