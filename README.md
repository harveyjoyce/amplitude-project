# Amplitude Project 📥

<img align="right" alt="image" src="https://github.com/user-attachments/assets/4852ff96-0077-4905-a629-53d30982dd87" width="20%"/>

This project: 
- Retrieves website traffic data from the **[Amplitude Export API](https://amplitude.com/docs/apis/analytics/export)**
- Logs execution details, unzips the `.zip` and `.gz` files, then stores the downloaded data locally as timestamped JSON files
- Uploads them to an S3 bucket in **AWS** which connects to **Snowflake**
- **dbt** is used to parse out the raw JSON and create a view 

## Project Overview Diagram 🎨

<img width="1586" height="744" alt="image" src="https://github.com/user-attachments/assets/cd1349e2-55a9-4c1c-94e9-53453a5d2d67" />

## Setting up the Repository ⚙️

1. Clone this repository:

```bash
git clone https://github.com/yourusername/amplitude-project.git
```

2. Create a branch

```bash
git checkout -b your-branch-name
```

3. Create and activate a virtual environment:

```bash
python -m venv .venv
# Linux / Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

3. Install required packages

```bash
pip install -r requirements.txt
```

4. Add a .env file in the root of the project containing your Amplitude API and AWS credentials (After setting up an appropriate IAM User and S3 Bucket):

```
AMP_API_KEY = ' '
AMP_SECRET_KEY = ' '

AWS_ACCESS_KEY = ' '
AWS_SECRET_KEY = ' '
AWS_BUCKET = ' '
AWS_REGION = ' '
```

## Python Project Structure 👷‍♂️

```
├── zip_files/
│   └── YYYY-MM-DD HH-MM-SS.json
├── gzip_files/
│   └── YYYY-MM-DD HH-MM-SS.json
├── json_data/
│   └── YYYY-MM-DD HH-MM-SS.json
├── logs/
│   └── logs_YYYY-MM-DD HH-MM-SS.log
├── main.py
├── modules/
│   └── logging.py
│   └── extract.py
│   └── unzip.py
│   └── load.py
├── archive/
│   └── extract_api.py
│   └── load_amplitude.py
│   └── unzip_files.py
├── .env
└── README.md
```

## How It Works 🔨

**main.py**

This script automates a standard ETL (Extract, Transform, Load) pipeline designed to move data from the Amplitude Analytics API into an AWS S3 bucket.
Here is the breakdown of what it’s doing:
- Environment Preparation & Authentication: It initialises a local file system (creating folders for logs and raw data), calculates a 24-hour time window for "yesterday's" data, and securely retrieves API and AWS credentials from a `.env` file.
- Data Extraction & Processing: It calls the Amplitude API to download zipped data from the calculated timeframe (with a 3-attempt retry logic for reliability), then decompresses those files from `.zip` to `.gz` and finally into raw .json format, cleaning up the intermediate archives as it goes.
- Cloud Storage Loading: It establishes a connection to Amazon S3 using `boto3`, uploads the processed JSON files to a specified bucket, logs the entire process for auditability, and deletes the local files once the transfer is complete.

**logging.py**

This function serves as the central nervous system for the pipeline’s observability, ensuring that every action taken by the other functions is recorded with context.
Here is what it’s doing:
- Dynamic Log Generation: It uses a provided timestamp to create a unique filename (e.g., logs_YYYY-MM-DD HH-MM-SS.log) within a dedicated directory, preventing older logs from being overwritten and making it easier to audit specific runs.
- Standardised Formatting: It configures the global logging settings to include the exact time of the event, the severity level (INFO, WARNING, ERROR), and a descriptive message for every entry.
- Centralised Logger Instance: It initialises and returns a "logger" object that can be passed to other functions (like the extract or unzip functions), allowing them to report their status to that single, timestamped file.

**extract.py**

This function is the "Extract" phase of your pipeline, specifically handling the heavy lifting of pulling data from the Amplitude API.
Here is what this specific function is doing:
- Authenticated Data Retrieval: It sends an authorized GET request to the Amplitude API using Basic Auth (API/Secret keys) to fetch event data as a binary zip file.
- Intelligent Retry Logic: It manages network instability by checking status codes; if it hits a server error (500 range), it waits 10 seconds and retries (up to a set limit), but it immediately kills the script for client-side errors (like a 401 Unauthorized) to avoid infinite loops.
- File Persistence & Logging: Upon a successful 200 OK response, it writes the raw content to a local `.zip` file with a unique timestamp and simultaneously records every success or failure to a `.log` file for later troubleshooting.

**unzip.py**

This function handles the "Transform" stage of your pipeline, specifically dealing with the nested compression layers common in large data exports.
Here is what this function is doing:
- Two-Stage Decompression: It first unpacks a `.zip` archive to reveal a batch of compressed .gz files, and then it performantly streams those `.gz` files into a final readable format (JSON) using `shutil.copyfileobj`.
- Recursive File Traversal: It uses `os.walk` to dig through any subdirectories created during the initial unzip, ensuring it finds and processes every single data file regardless of how the API structured the folder hierarchy.
- Automatic Workspace Cleanup: To save disk space and keep the environment tidy, it immediately deletes the source `.zip` and intermediate `.gz` files the moment they have been successfully processed and moved to the next stage.

**load.py**

This final function is the "Load" phase of your pipeline, where the processed data is safely moved to permanent cloud storage.
Here is what it is doing:
- Targeted File Discovery: It scans your local directories specifically for files ending in `.json`, filtering out any stray logs or system files to ensure only actual data is sent to the cloud.
- Secure Cloud Migration: It uses the boto3 client to stream each JSON file into your specified AWS S3 bucket, effectively moving your data from a temporary local environment to a secure, scalable production environment.
- Success-Based Cleanup: It operates on a "delete-after-upload" logic—only removing the local file from your disk once the S3 upload is confirmed successful, which prevents data loss in case of a network failure.

## Logging 📝
Each script execution creates a log file containing:
- System status messages
- Successful downloads/uploads
- Warnings and errors
- Critical failures

Example log entry:
```
2026-01-27 13:38:03,186 - INFO - Uploading json_data\100011471_2026-01-26_11#0.json
2026-01-27 13:38:03,263 - INFO - Upload successful
```

## Configuring AWS 🟧 and Snowflake ❄️

To connect to Snowflake from AWS, you need to create an IAM Role and Storage Intergration. I have written a blog [here](https://www.thedataschool.co.uk/harvey-joyce/connecting-snowflake-and-aws-s3-storage-integration-and-procedures/) on how to set that up!

In Snowflake, I also created a pipe to handle automatic data loading from S3.

``` sql
create or replace pipe <name> auto_ingest = true as 
copy into raw_bike_point (raw_json, filename)
from 
(select  
    $1, 
    metadata$filename
from @bike_point_stage)
file_format = (
        type = 'JSON'
        strip_outer_array = TRUE
        )
```
After, if you query `show pipes` you will find your pipe's `notification_channel` code, it will look like this: `arn:aws:sqs:eu-west-2:...`.

If you got to your bucket in AWS, go to Properties and scroll down to Event Notifications, you can set up the pipe to run every time there is new data in the bucket.

## dbt Project Structure 🟠

```
├── analyses/             # SQL files for one-off exports or ad-hoc queries
├── macros/               # Reusable Jinja functions (like custom aggregations)
├── models/               # The heart of your project
│   ├── staging/          # Raw data cleaning (renaming, type casting)
│   │   └── amplitude/   # Organized by source system (e.g., stripe, hubspot)
│   │       ├── base/
│   │       │    └── base_amplitude__events.sql
│   │       ├── _amplitude__docs.yml # Write detailed, reusable explanations.
│   │       ├── _amplitude__models.yml # Test and describe your SQL models.
│   │       ├── _amplitude__sources.yml # Define raw, external data.
│   │       └── stg_amplitude__events.sql
│   ├── intermediate/     # Complex joins and business logic between staging/marts
│   │   └── amplitude/
│   │       ├── _amplitude__models.yml
│   │       └── int_amplitude__many_click_sessions.sql
│   └── marts/            # Final, "gold" tables for BI tools
│       └── amplitude/
│           ├── _amplitude__models.yml
│           └── amplitude__repeat_clicks.sql
├── seeds/                # Small, static CSV files (e.g., country codes)
├── snapshots/            # Files for tracking data changes over time (SCD Type 2)
├── tests/                # Custom data quality tests (singular tests)
├── dbt_project.yml       # The main configuration file for the whole project
├── packages.yml          # External dbt libraries (like dbt-utils)
├── profiles.yml          # Connection credentials (usually kept in ~/.dbt/)
└── README.md
```
## Data Model 🗺️

### int_amplitude__many_click_sessions: 
- Identifies "High-Intensity" Events: It scans the raw event logs to find specific instances where a user interacted with the same element or page more than twice within a single session.
- Isolates the Noise: It filters the entire dataset down to only these repetitive interactions, providing a clean "subset" of data for deeper analysis without the bulk of normal user behavior.

### amplitude__repeat_clicks 🏅
- Calculates Interaction Speed: It uses a `LAG` function to measure the exact number of seconds between each consecutive click, identifying how rapidly a user is repeating an action.
- Aggregates to a Unique Key: It rolls the data up into a final table with a unique Primary Key (`pkey`), calculating the average time between events and the total session duration for each specific interaction.

