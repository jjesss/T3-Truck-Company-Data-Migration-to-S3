from extract import extract
from transform import transform
from create_parquet import partition_by_date
from upload_to_s3 import upload_to_s3
from logger import make_logger

logger = make_logger()


def run_pipeline():
    """Extract -> Transform -> Partition -> Upload"""
    logger.info("===Starting ETL pipeline.")
    extracted_path = extract()
    if not extracted_path:
        logger.error("No extraction output. Exiting pipeline.")
        return

    cleaned_path = transform(extracted_path)
    if not cleaned_path:
        logger.error("No cleaned output. Exiting pipeline.")
        return

    # Load
    df = partition_by_date(cleaned_path)
    if df is None:
        logger.error("Partition step failed. Exiting pipeline.")
        return

    upload_to_s3(df)
    logger.info("===ETL pipeline completed successfully.\n")


if __name__ == "__main__":
    run_pipeline()
