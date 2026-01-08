# Amplitude Daily Export Script

## Overview

This Python script retrieves event data from the **Amplitude Export API** for the previous day and saves it locally as a compressed `.zip` file. It also generates timestamped log files to track execution details, API responses, and errors.

The script is intended to be run once per day, either manually or via a scheduler such as cron or Task Scheduler.

---

## Features

* Fetches **yesterday’s data** from Amplitude automatically
* Saves exported data as a `.zip` file with a timestamped filename
* Creates `logs/` and `data/` directories if they do not exist
* Logs execution steps, API responses, and errors
* Retries failed API calls up to **3 times**
* Uses environment variables for secure API credential storage

---

## Requirements

* Python 3.8+
* An Amplitude account with API access
* Python packages:

  * `requests`
  * `python-dotenv`

Install dependencies with:

```bash
pip install requests python-dotenv
```

---

## Environment Variables

Create a `.env` file in the project root directory with the following contents:

```env
AMP_API_KEY=your_amplitude_api_key
AMP_SECRET_KEY=your_amplitude_secret_key
```

These credentials are required to authenticate with the Amplitude Export API.

---

## How the Script Works

1. Loads API credentials from the `.env` file
2. Creates `logs/` and `data/` directories if they do not already exist
3. Determines yesterday’s date range (00:00–23:00)
4. Sends a request to the Amplitude Export API
5. If the request is successful:

   * Saves the response as a `.zip` file in the `data/` directory
6. If the request fails:

   * Retries up to 3 times with a 10-second delay between attempts
7. Logs all actions and outcomes to a timestamped log file

---

## Output

### Data Files

* Directory: `data/`
* Filename format:

  ```
  YYYY-MM-DD HH-MM-SS.zip
  ```

### Log Files

* Directory: `logs/`
* Filename format:

  ```
  YYYY-MM-DD HH-MM-SS.log
  ```

---

## API Endpoint

```
https://analytics.eu.amplitude.com/api/2/export
```

> This script is configured for the **EU Amplitude endpoint**.
> If your Amplitude project is hosted in a different region, update the URL accordingly.

---

## Running the Script

Run the script with:

```bash
python your_script_name.py
```

For automation, schedule it using:

* `cron` (Linux/macOS)
* Windows Task Scheduler
* A workflow orchestration tool (e.g., Airflow, Prefect)

---

## Error Handling

* Logs HTTP response codes from the API
* Retries on server or unexpected errors
* Stops execution on unrecoverable API errors

---

## Notes

* The script does not currently validate whether API keys are missing—this can be added for robustness.
* The exported file is saved as raw API output without transformation.
* Logging level is set to `INFO`.

---

## License

Free to use and modify for personal, internal, or commercial projects.
