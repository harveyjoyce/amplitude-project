import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import boto3
from modules.logging import logging_function
from modules.extract import extract_function
from modules.unzip import unzipping_function
from modules.load import loading_function

#create directories for data and logs if they don't already exist
logs_dir = 'logs'
zip_files = 'zip_files'
gzip_files = 'gzip_files'
json_data = 'json_data'

dirs = [logs_dir, zip_files, gzip_files, json_data]
for dir in dirs:
    os.makedirs(dir, exist_ok=True)

#create timestamps (used for file names and api call)
current_timestamp = datetime.now()
yesterday_timestamp = current_timestamp - timedelta(days=1)

current_timestamp_str = current_timestamp.strftime('%Y-%m-%d_%H-%M-%S')
yesterday_timestamp_str = yesterday_timestamp.strftime('%Y-%m-%d_%H-%M-%S')

request_start = f'{yesterday_timestamp_str.replace('-', '')[:8]}T00'
request_end = f'{yesterday_timestamp_str.replace('-', '')[:8]}T23'

#set up logging
logger = logging_function(timestamp=current_timestamp_str)

#load secrets
load_dotenv()

AMP_API_KEY = os.getenv('AMP_API_KEY')
AMP_SECRET_KEY = os.getenv('AMP_SECRET_KEY')

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
AWS_BUCKET = os.getenv('AWS_BUCKET')

#api information
url = 'https://analytics.eu.amplitude.com/api/2/export'
params = {
    'start': request_start,
    'end': request_end
}

#define retry logic
max_attempts = 3

#extract data, implementing retry logic and logging the outcome
extract_function(
    max_attempts=max_attempts,
    url=url,
    params=params,
    API_KEY=AMP_API_KEY,
    SECRET_KEY=AMP_SECRET_KEY,
    logger=logger,
    data_dir=zip_files,
    current_timestamp_str=current_timestamp_str
)

#Extract zip files, creating gzip files. Remaining zip files are deleted
#Extract gzips, outputting json files. The remaining gzip files are deleted

unzipping_function(
    zip_dir=zip_files, 
    gzip_dir=gzip_files, 
    output_dir=json_data, 
    logger=logger
)

#connect to s3
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY
)

#loop through and upload all JSON files to s3, deleting the local copies
loading_function(
    json_dir=json_data,
    s3_client=s3_client,
    bucket_name=AWS_BUCKET,
    logger=logger
)