# Amplitude Project 📥

<img align="right" alt="image" src="https://github.com/user-attachments/assets/4852ff96-0077-4905-a629-53d30982dd87" width="20%"/>

This project: 
- Retrieves website traffic data from the **[Amplitude Export API](https://amplitude.com/docs/apis/analytics/export)**
- Logs execution details, unzips the .zip and .gzip files, then stores the downloaded data locally as timestamped JSON files
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
│   └── YYYY-MM-DD HH-MM-SS.log
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

This script acts as the orchestrator for a data pipeline, moving BikePoint data to S3. Here is what it's doing:
- Environment & Setup: It loads secure credentials (AWS keys) from a .env file and initialises two distinct logging sessions—one for `extract` and one for `load`—using the current timestamp.
- Data Extraction: It triggers a process to fetch bike point data from the TfL API and passes the `extract_logger` to track the success or failure of that specific task.
- Cloud Loading: It takes the locally saved data from a data folder and uploads it to a specified AWS S3 bucket, using the `load_logger` to record the transfer details.

**logging.py**

This script sets up a reusable logging system in Python. Here is the breakdown of what it’s doing:
- Creates a Directory: It automatically generates a folder named after your prefix (if it doesn't already exist) to store your log files.
- Initialises a File Logger: It creates a specific .log file named with your timestamp and configures it to record messages at the INFO level.
- Prevents Duplication: It checks for existing "handlers" before adding new ones, ensuring your logs don't accidentally double-post the same message to the file.

**extract.py**

This script handles the extraction and storage phase of your pipeline with built-in error handling. Here is what’s happening:
- API Request with Retry Logic: It attempts to fetch data from the provided URL and is programmed to retry up to a specific number of times if it encounters server errors (status codes 500+) or connection issues.
- JSON File Management: Upon a successful "200 OK" response, it ensures a `data` directory exists and saves the API results as a local .json file named after the current timestamp.
- Success and Error Logging: It records the outcome of the attempt—logging a success message and a "😊" emoji to your log file if it works, or capturing the failure reason if the request hits a permanent error (like a 404).
- It will try 3 times in total, waiting 10 seconds each go (`time.sleep(10)`).

**load.py**

This script handles the loading and cleanup phase of your pipeline, moving local data to the cloud. Here is what it’s doing:
- File Discovery & Validation: It scans the `data` directory for all files ending in .json; if it doesn't find any, it logs an error and stops the process to prevent unnecessary cloud connections.
- S3 Cloud Upload: Using the `boto3` library, it establishes a connection to AWS and uploads each JSON file to your specified S3 bucket using the original filename.
- Cleanup & Error Logging: After a successful upload, it deletes the local file (`unlink`) to save space; if an upload fails due to AWS permissions or network issues, it catches the error and logs it without crashing the entire loop.

## Logging 📝
Each script execution creates a log file containing:
- System status messages
- Successful downloads/uploads
- Warnings and errors
- Critical failures

Example log entry:
```
2026-01-07 12:30:01 - INFO - Download successful at 2026-01-07 12-30-01 😊
2026-01-07 12:35:15 - INFO - Uploaded and deleted: 2026-01-07 12-30-01.json
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
│   │   └── bike_point/   # Organized by source system (e.g., stripe, hubspot)
│   │       ├── base/
│   │       │    └── base_bike_point__parsed.sql
│   │       ├── _bike_point__sources.yml
│   │       └── stg_bike_point__parsed.sql
│   ├── intermediate/     # Complex joins and business logic between staging/marts
│   └── marts/            # Final, "gold" tables for BI tools
│       └── bike_point/
│           ├── bike_point_gold.sql
│           ├── dim_bike_point.sql
│           └── fct_bike_point.sql
├── seeds/                # Small, static CSV files (e.g., country codes)
├── snapshots/            # Files for tracking data changes over time (SCD Type 2)
├── tests/                # Custom data quality tests (singular tests)
├── dbt_project.yml       # The main configuration file for the whole project
├── packages.yml          # External dbt libraries (like dbt-utils)
├── profiles.yml          # Connection credentials (usually kept in ~/.dbt/)
└── README.md
```
## Data Model 🗺️

<img width="3452" height="1323" alt="image" src="https://github.com/user-attachments/assets/a6f8f034-a4c4-4c2e-9a4f-61fd20569461" />

### fct_bike_point: 
- This is a fact table that records the number of bikes, docks, e-bikes at each BikePoint location
- We're not updating any existing data so we use an incremental append.

### dim_bike_point:
- This is a dimension table that has qualitative infomation about each BikePoint (e.g Name, Location etc)
- There are a few columns that we want to update but not record the history of changes (e.g removaldate). We can use a snapshot table to do this.

### bike_point_gold 🏅
- The API documentation mentions that if `nbdocks - (nbemptydocks + nbbikes)` is negative then that BikePoint has broken docks.
- This is a simple view that shows what BikePoints have broken docks and where they are located.

## License 🪪 

This project uses public TfL API data and is intended for educational and non-commercial use.
Please refer to TfL’s API terms and conditions for usage guidelines.

