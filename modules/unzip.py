import os
import gzip
import shutil
from zipfile import ZipFile


def unzipping_function(zip_dir, gzip_dir, output_dir, logger):
    """
    Extract zip files containing folders of gzip files,
    then decompress all .gz files to output_dir.
    """

    for zip_name in os.listdir(zip_dir):
        if not zip_name.endswith(".zip"):
            continue

        zip_path = os.path.join(zip_dir, zip_name)
        logger.info(f"Processing {zip_name}")

        try:
            # 1. Unzip
            with ZipFile(zip_path) as zf:
                zf.extractall(gzip_dir)

            logger.info(f"{zip_name} extracted")
            os.remove(zip_path)
            logger.info(f"{zip_name} deleted")

            # 2. Walk extracted content and decompress gz files
            for root, _, files in os.walk(gzip_dir): # os.walk returns 3 values, _ means "ignore this variable"
                for file in files:
                    if not file.endswith(".gz"):
                        continue

                    gz_path = os.path.join(root, file)
                    output_path = os.path.join(output_dir, file[:-3])

                    with gzip.open(gz_path, "rb") as gz_file, \
                         open(output_path, "wb") as out_file:
                        shutil.copyfileobj(gz_file, out_file)

                    logger.info(f"{file} decompressed")
                    os.remove(gz_path)
                    logger.info(f"{file} deleted")

        except Exception as e:
            logger.exception(f"Failed processing {zip_name}: {e}")
