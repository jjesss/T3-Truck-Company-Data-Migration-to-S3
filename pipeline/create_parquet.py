"""File to partition data by year/month/day and save as parquet file 
for efficient querying in Athena
create parquet file from csv file
"""

import os
import pandas as pd
from logger import make_logger
# import pyarrow

logger = make_logger()


def partition_by_date(csv_path) -> pd.DataFrame:
    """Read csv, convert to datetime, and extract year/month/day for partitioning"""
    try:
        df = pd.read_csv(csv_path)

        df['at'] = pd.to_datetime(df['at'])
        # Extract year, month, day for partitioning the parquet file
        df['year'] = df['at'].dt.year
        df['month'] = df['at'].dt.month
        df['day'] = df['at'].dt.day
        # also partition by hour for 3-hour batch intervals
        df['hour'] = df['at'].dt.hour
        # write partitioned parquet to disk
        out_dir = "data files/parquet/"
        os.makedirs(out_dir, exist_ok=True)
        df.to_parquet(
            out_dir,
            index=False,
            partition_cols=['year', 'month', 'day', 'hour']
        )
        logger.info("Wrote parquet partitions to %s", out_dir)
        return df
    except Exception as e:
        logger.error("Error processing file %s: %s", csv_path, e)
        return None


if __name__ == "__main__":
    truckdf = partition_by_date('data files/cleaned_truck_data.csv')
    if truckdf is not None:
        # parquet is already written by partition_by_date function
        pass
