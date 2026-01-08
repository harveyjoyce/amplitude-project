import os
import requests
import logging
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta

logs_dir = 'logs'
if os.path.exists(logs_dir):
    pass
else:
    os.mkdir(logs_dir)
filename = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
log_filename = f"logs/{filename}.log"

dir = 'data'
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


load_dotenv()

AMPLITUDE_API_KEY = os.getenv("AMP_API_KEY")
AMPLITUDE_SECRET_KEY = os.getenv("AMP_SECRET_KEY")
logger.info("AMP Environment Variables Read")

# error if can't find api keys

url = 'https://analytics.eu.amplitude.com/api/2/export'

yesterday = datetime.now() - timedelta(days=1)

start_date = yesterday.strftime('%Y%m%dT00')
end_date = yesterday.strftime('%Y%m%dT23')

params= {
        'start': start_date, 
        'end': end_date
        }
logger.info("API URL/Parameters Set")

response = requests.get(url, params=params, auth=(AMPLITUDE_API_KEY, AMPLITUDE_SECRET_KEY))
logger.info(f"API Call Response Code: '{response.status_code}'")

if response.status_code == 200:
    data = response.content 
    logger.info("Data retrieved successfully.")
    logger.info("Saving data to data.zip")
    with open(filepath, 'wb') as file:
        file.write(data)
    logger.info("Data saved to data.zip")
else:
    logger.error(f"API Call Error '{response.status_code}: {response.text}'")
    print(f'Error {response.status_code}: {response.text}')

logger.info("Process Finished")



