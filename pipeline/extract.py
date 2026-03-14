""" 1. Extraction script that downloads data from the RDS and saves it locally
It accesses .env to get the RDS credentials,
connects to the database,
runs a SQL query to retrieve the data,
and saves it as a CSV file for later use in transformation and loading steps."""

import os
import re
import datetime
from typing import Optional
import boto3
from dotenv import load_dotenv
import pymysql
import pandas as pd
from logger import make_logger

logger = make_logger()

load_dotenv()
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT")) if os.getenv("DB_PORT") else None
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def connect_to_rds(host, port, db_name, user, password):
    """ Connect to the RDS database and return a connection object """
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=db_name,
        )
    except Exception as exc:
        logger.error("Failed to connect to RDS: %s", exc)
        return None

    return connection


def download_data(connection, last_timestamp=None):
    """ Download the data from the RDS database and return it as a DataFrame """
    try:
        if last_timestamp is not None and not pd.isna(last_timestamp):
            last_str = last_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            query = f"""
                        SELECT * FROM FACT_Transaction
                        JOIN DIM_Truck USING (truck_id)
                        JOIN DIM_Payment_Method USING (payment_method_id)
                        WHERE `at` > '{last_str}'
                    """
        else:
            query = """
                        SELECT * FROM FACT_Transaction
                        JOIN DIM_Truck USING (truck_id)
                        JOIN DIM_Payment_Method USING (payment_method_id)
                        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            df = pd.DataFrame(data, columns=columns)
    except Exception as exc:
        logger.error("Failed to run query: %s", exc)
        return None

    return df


def get_last_timestamp_from_s3() -> Optional[datetime.datetime]:
    """Check S3 dataset for last timestamp by scanning partition folders (year/month/day/hour).
    Returns naive datetime (UTC assumed) or None on failure."""
    s3_path = os.getenv("S3_DATASET_PATH", "s3://c22-jessh-food-truck-bucket/")
    if not s3_path.startswith("s3://"):
        logger.warning("S3_DATASET_PATH not a valid s3 uri: %s", s3_path)
        return None

    # Get everything after "s3://", then split into bucket and prefix
    _, _, rest = s3_path.partition("s3://")
    bucket, _, prefix = rest.partition("/")
    if prefix and not prefix.endswith("/"):
        prefix += "/"

    s3 = boto3.client("s3", region_name=os.getenv(
        "AWS_DEFAULT_REGION", "eu-west-2"))
    # S3 paginator to handle large number of objects if needed
    paginator = s3.get_paginator("list_objects_v2")

    # Regex to extract year/month/day/hour from partition keys
    pattern = re.compile(
        r"year=(\d{4})/month=(\d{1,2})/day=(\d{1,2})/hour=(\d{1,2})")
    # max_dt can either be datetime or None
    max_dt: Optional[datetime.datetime] = None
    try:
        # AWS API (S3) limit up to 1000 objects per page
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj.get("Key", "")

                match = pattern.search(key)
                if not match:
                    continue
                year, month, day, hour = map(int, match.groups())
                # Build datetime
                try:
                    dt = datetime.datetime(year, month, day, hour)
                except ValueError:
                    continue
                # Track max timestamp across all partitions
                if max_dt is None or dt > max_dt:
                    max_dt = dt
    except Exception as exc:
        logger.warning("Error listing S3 objects for timestamp: %s", exc)
        return None

    logger.info("Last timestamp from S3 dataset (by partition): %s", max_dt)
    return max_dt


def extract():
    """ Main function to execute the extraction process """
    connection = None
    try:
        connection = connect_to_rds(
            DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)

        if connection is None:
            logger.error("Database connection failed. Exiting extraction.")
            return None

        # Checking S3 dataset for last timestamp when configured
        last_ts = get_last_timestamp_from_s3()

        data = download_data(connection, last_timestamp=last_ts)
        if data is None:
            logger.error("Query failed.")
            return None

        if data.empty:
            logger.info("No new rows extracted from RDS.")
            return None

        out_path = "data files/extracted_truck_data.csv"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        data.to_csv(out_path, index=False)
        logger.info("Extracted %d rows to %s", len(data), out_path)

        return out_path
    except Exception as exc:
        logger.error("Extraction failed: %s", exc)
        return None
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    extract()
