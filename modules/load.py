import os

def loading_function(json_dir, s3_client, bucket_name, logger):
    '''
    Loops through and uploads all JSON files to s3, deleting the local files
    '''
    for root, _, files in os.walk(json_dir): # os.walk returns 3 values, _ means "ignore this variable"
        files = [file for file in files if file.lower().endswith('.json')] #filter list to only JSON files
        if len(files) > 0:
            for file in files:
                filepath = os.path.join(root, file)
                print(f'Uploading {filepath}')
                logger.info(f'Uploading {filepath}')
                try:
                    s3_client.upload_file(filepath, bucket_name, file)
                    print('Upload successful')
                    logger.info('Upload successful')
                    os.remove(filepath)
                    print(f'Local copy of {file} deleted')
                    logger.info(f'Local copy of {file} deleted')
                except Exception as e:
                    print(f'Error: {e}')
                    logger.error(f'Error: {e}')
        else:
            print('No JSON files to upload')
            logger.info('No JSON files to upload')