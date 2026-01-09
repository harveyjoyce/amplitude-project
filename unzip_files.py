import os
import logging
import json
from datetime import datetime, timedelta

# Create directories if necessary 
logs_dir = 'unzip_logs'
if os.path.exists(logs_dir):
    pass
else:
    os.mkdir(logs_dir)
filename = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
log_filename = f"logs/{filename}.log"

dir = 'unzip_data'
if os.path.exists(dir):
    pass
else:
    os.mkdir(dir)
filepath = f'{dir}/{filename}.zip'

# Configure logs to retrieve INFO messages and higher
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_filename
)

logger = logging.getLogger()