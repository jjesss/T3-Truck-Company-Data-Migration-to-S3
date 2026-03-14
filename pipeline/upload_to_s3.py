"""Upload parquet files to S3 dataset (append partitions)."""
import os
import awswrangler as wr  # pylint: disable=import-error
from create_parquet import partition_by_date
from logger import make_logger

logger = make_logger()


def upload_to_s3(dataframe, s3_path: str = None) -> None:
    """Write `dataframe` as a partitioned dataset to S3. Uses env var
    `S3_DATASET_PATH` if `s3_path` is not provided. Appends partitions.
    """
    path = s3_path or os.getenv(
        'S3_DATASET_PATH') or 's3://c22-jessh-food-truck-bucket/'

    wr.s3.to_parquet(
        df=dataframe,
        path=path,
        dataset=True,  # treat as a partitioned dataset
        partition_cols=['year', 'month', 'day', 'hour'],
        mode='append'
    )
    logger.info("Parquet files uploaded to %s (appended).", path)


if __name__ == "__main__":
    partition_by_date_df = partition_by_date(
        'data files/cleaned_truck_data.csv')
    upload_to_s3(partition_by_date_df)
