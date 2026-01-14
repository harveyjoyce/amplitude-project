# Single JSON file upload to S3 with KMS key

# Load libraries
import boto3
import os
from dotenv import load_dotenv
from pathlib import Path
from botocore.exceptions import BotoCoreError, ClientError
from datetime import datetime
import logging

# Create directories if necessary 
logs_dir = 'load_logs'
if os.path.exists(logs_dir):
    pass
else:
    os.mkdir(logs_dir)
filename = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
log_filename = f"load_logs/{filename}.log"

# Configure logs to retrieve INFO messages and higher
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_filename
)

logger = logging.getLogger()


# Load .env file
load_dotenv()

# Read .env file
# aws_access_key=os.getenv('AWS_ACCESS_KEY')
# aws_secret_key=os.getenv('AWS_SECRET_KEY')
# aws_bucket_name=os.getenv('AWS_BUCKET')
# logger.info("Environment Variables Read")

# 1. Create a session using your specific profile name
session = boto3.Session(profile_name='default') 
# 2. Create an S3 client from that session 
s3 = session.client('s3')

data_dir = Path('unzip_data')

# Find JSON files
json_files = list(data_dir.glob('*.json'))

# Error if no files exist
if not json_files:
    logger.error("No JSON files found")
    raise FileNotFoundError(f"No JSON files found in '{data_dir}'")

for json_file in json_files:
    try:
        # Upload the file to the specified S3 bucket
        s3.upload_file(
            str(json_file),  # File path as a string
            aws_bucket_name,     # S3 bucket name
            json_file.name   # Name of the file in S3
        )

        # Delete the local file after successful upload
        json_file.unlink()
        logger.info(f"Uploaded and deleted: {json_file.name}")

    # Handle known AWS errors
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to upload {json_file.name}: {e}")

    # Handle any other unexpected errors
    except Exception as e:
        logger.error(f"Unexpected error with {json_file.name}: {e}")