import os
import requests
import logging
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Create directories if necessary 
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

# Load .env
load_dotenv()

AMPLITUDE_API_KEY = os.getenv("AMP_API_KEY")
AMPLITUDE_SECRET_KEY = os.getenv("AMP_SECRET_KEY")
logger.info("AMP Environment Variables Read")

# error if can't find api keys

# Build url and create parameters for API

url = 'https://analytics.eu.amplitude.com/api/2/export'

yesterday = datetime.now() - timedelta(days=1)

start_date = yesterday.strftime('%Y%m%dT00')
end_date = yesterday.strftime('%Y%m%dT23')

params= {
        'start': start_date, 
        'end': end_date
        }
logger.info("API URL/Parameters Set")

# Request API

response = requests.get(url, params=params, auth=(AMPLITUDE_API_KEY, AMPLITUDE_SECRET_KEY))
response_code = response.status_code
logger.info(f"API Call Response Code: '{response_code}'")

count = 0
number_of_tries = 3

while count < number_of_tries:

    # If successful?

    if response_code == 200:
        data = response.content # because it .zips
        logger.info("Data retrieved successfully.")
        logger.info(f"Saving data to amp_events.zip")
        with open(f"data/amp_events.zip", 'wb') as file:
            file.write(data)
        logger.info(f"Data saved to amp_events.zip")
        break

    # If not sucessful?
    elif response_code>499 or response_code<200:
            # wait and retry
            time.sleep(10)
            count+=1
            logger.info(f"This is attempt {count}")
    else:
        logger.error(f"API Call Error '{response_code}: {response.text}'")
        print(f'Error {response_code}: {response.text}')
        break

    logger.info("Process Finished")



