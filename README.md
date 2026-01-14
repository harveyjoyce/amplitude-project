# Amplitude to S3 ETL Pipeline
This repository contains a Python-based ETL (Extract, Transform, Load) pipeline that automates the process of exporting event data from the Amplitude Export API, processing the compressed files, and uploading the resulting JSON data to an Amazon S3 bucket.

## 🚀 Features

- Automated Extraction: Pulls data from the Amplitude Export API for the previous day's events.

- Two-Stage Decompression: Handles nested compression by extracting `.zip` archives and subsequently decompressing internal `.gz` files.

- S3 Integration: Automatically uploads processed JSON files to a specified AWS S3 bucket.

- Robust Logging: Detailed logging of every stage (extraction, decompression, and upload) with unique timestamps.

- Error Handling: Includes retry logic for server-side API errors and exception handling during file processing.

## 📂 Project Structure
```
.
├── main.py              # Entry point: Orchestrates the ETL workflow
├── modules/
│   ├── extract.py       # Handles API requests to Amplitude
│   ├── unzip.py         # Manages zip extraction and gzip decompression
│   ├── load.py          # Handles AWS S3 uploads and local cleanup
│   └── logging.py       # Configures the logging instance
├── logs/                # Local storage for runtime logs
├── zip_files/           # Temporary storage for downloaded zips
├── gzip_files/          # Intermediate storage for extracted gzips
└── json_data/           # Final processed JSON files ready for upload
```
## 🛠️ Setup and Installation

1. Prerequisites
- Python 3.x
- An Amplitude project with API/Secret keys.
- An AWS account with S3 bucket access.

2. Environment Variables
Create a `.env` file in the root directory and populate it with your credentials:

```
AMP_API_KEY=your_amplitude_api_key
AMP_SECRET_KEY=your_amplitude_secret_key
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_BUCKET=your_s3_bucket_name
```

3. Install Dependencies
```
pip install requests boto3 python-dotenv
```
## ⚙️ How It Works

### Extraction: 

- The script calculates a time range for the previous day. It calls the Amplitude Export API, downloading the data as a .zip file into the `zip_files` folder.

### Transformation:

- The .zip file is extracted into gzip_files.

- All .gz files found within are decompressed into raw JSON files in `json_data`.

- Source compressed files are deleted after successful extraction to save space.

### Loading: 

- The script connects to AWS S3 and uploads every file found in json_data. Once uploaded, the local JSON copy is deleted.

## 📝 Logging

- Logs are generated for every run and stored in the `/logs` directory. Files are named using the format `logs_YYYY-MM-DD_HH-MM-SS.log` to ensure history is preserved and easily searchable.
