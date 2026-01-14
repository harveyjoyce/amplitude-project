import requests
import time
import os

def extract_function(url, number_of_tries, params, AMP_API_KEY, AMP_SECRET_KEY, logger, timestamp):
    '''
    Docstring for extract_function
    
    :param url: Description
    :param number_of_tries: Description
    :param params: Description
    :param AMP_API_KEY: Description
    :param AMP_SECRET_KEY: Description
    :param logger: Description
    :param timestamp: Description
    '''
    count = 0

    while count < number_of_tries:

        response = requests.get(url, params=params, auth=(AMP_API_KEY, AMP_SECRET_KEY))
        response_code = response.status_code

        dir = 'data'
        if os.path.exists(dir):
            pass
        else:
            os.mkdir(dir)

        filepath = f'{dir}/{filename}.zip'

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
