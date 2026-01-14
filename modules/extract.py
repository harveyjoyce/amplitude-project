import requests
import time

def extract_amplitude_data(max_attempts, url, params, API_KEY, SECRET_KEY, logger, data_dir, current_timestamp_str):
    '''
    Extracts data from Amplitude, writing it to a zip file, handling errors, and logging the outcome
    '''
    count = 0
    while count < max_attempts:
        response = requests.get(url, params=params, auth=(API_KEY, SECRET_KEY))

        #check for successful download
        if response.status_code == 200:
            print('Download successful')
            logger.info('Download successful')
            file_path = f'{data_dir}/amplitude_events_{current_timestamp_str}.zip'
            with open(file_path, 'wb') as file:
                file.write(response.content) # Because the response is zip files
            print(f'File written successfully to {file_path}')
            break

        #check for server error
        elif response.status_code < 200 or response.status_code >= 500:
            print('Server error')
            logger.warning('Server error')
            print(response.reason)
            logger.warning(response.reason)
            print('Retrying...')
            time.sleep(10)
            count += 1

        #check for non-server error
        else:
            print('Non-server error. Terminating script')
            logger.error('Non-server error. Terminating script')
            print(response.reason)
            logger.error(response.reason)
            break
