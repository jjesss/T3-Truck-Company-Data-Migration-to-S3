"""Helper functions for the Streamlit dashboard.
This module contains functions for loading data and queries to be used in the Streamlit dashboard.

Athena charges per query based on the amount of data scanned. 
So: 
- One SELECT * query = one charge, all data in memory
- Multiple specific queries = multiple charges
Currently the dataset size is quite small, so loading everything once and using pandas to filter/aggregate 
is a better approach - cheaper and faster since subsequent operations are in memory."""

import awswrangler as wr
import boto3
import streamlit as st


@st.cache_data(ttl=300, show_spinner=True)
def load_data_auto_cache():
    """Load data from Athena with automatic caching."""
    t3_data = wr.athena.read_sql_query(
        sql='SELECT * FROM "c22-jessh-food-truck-sales-db"."c22_jessh_food_truck_bucket";',
        database="c22-jessh-food-truck-sales-db",
        boto3_session=boto3.Session(region_name="eu-west-2"),
        s3_output="s3://c22-jessh-food-truck-bucket/athena-results/"
    )
    return t3_data
