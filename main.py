from modules.logging import logging_function
from modules.extract import extract_function
from modules.load import load_function
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

AMP_API_KEY = os.getenv("AMP_API_KEY")
AMP_SECRET_KEY = os.getenv("AMP_SECRET_KEY")

aws_access_key_id = os.getenv('aws_access_key_id')
aws_secret_access_key = os.getenv('aws_secret_access_key')
bucket_name = os.getenv('bucket_name')

timestamp = datetime.now().strftime('%Y-%m-%d %H-%M-%S')

url = 'https://analytics.eu.amplitude.com/api/2/export'

yesterday = datetime.now() - timedelta(days=1)

start_date = yesterday.strftime('%Y%m%dT00')
end_date = yesterday.strftime('%Y%m%dT23')

params= {
        'start': start_date, 
        'end': end_date
        }

extract_logger = logging_function('extract',timestamp)

extract_function(url,3, extract_logger, timestamp)

load_logger = logging_function('load',timestamp)

load_function(Path('data'), aws_access_key_id, aws_secret_access_key, bucket_name, load_logger)
