import os
import logging
import json
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
import gzip
import shutil

# Create directories if necessary 
logs_dir = 'unzip_logs'
if os.path.exists(logs_dir):
    pass
else:
    os.mkdir(logs_dir)
filename = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
log_filename = f"unzip_logs/{filename}.log"

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

# Create a temporary directory for extraction
temp_dir = tempfile.mkdtemp()
logger.info("Environment Setup: beginning unzip process")

try:
    # Extract the main zip file into the temporary directory
    with zipfile.ZipFile("amp_events.zip", "r") as zip_ref:
        zip_ref.extractall(temp_dir)
        logger.info(f"amp_events.zip extracted to temp directory: {temp_dir} ")
except Exception as e:
    logger.error(f"Error extracting zip file: {str(e)}")
    raise

try:
    # Locate the day folder (assumed to be the numeric folder)
    day_folder = next(f for f in os.listdir(temp_dir) if f.isdigit())
    day_path = os.path.join(temp_dir, day_folder)
except Exception as e:
    logger.error(f"Error finding day folder: {str(e)}")
    raise

# Walk through the day folder and decompress each .gz file to the data directory
for root, _, files in os.walk(day_path):
    for file in files:
        if file.endswith('.gz'):
            try:
                gz_path = os.path.join(root, file)
                json_filename = file[:-3]  # Remove .gz extension
                output_path = os.path.join(dir, json_filename)

                with gzip.open(gz_path, 'rb') as gz_file, open(output_path, 'wb') as out_file:
                    shutil.copyfileobj(gz_file, out_file)
                
                logger.info(f"Successfully processed: {file} -> {json_filename}")
            except Exception as e:
                logger.error(f"Failed to process file {file}: {str(e)}")

try:
    # Delete the temporary directory
    shutil.rmtree(temp_dir)
    logger.info("Temp directory deleted")

except Exception as e:
    logger.error(f"Failed to delete temp directory: {str(e)}")

print("All files extracted to the 'data' directory!")