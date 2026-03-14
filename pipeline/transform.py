"""Transformation: clean extracted CSV and write cleaned, deduplicated CSV.

Functions are small and return the output path for pipeline orchestration.
"""

import os
import pandas as pd
from logger import make_logger

logger = make_logger()


def transform(input_csv: str = "data files/extracted_truck_data.csv",
              output_csv: str = "data files/cleaned_truck_data.csv") -> str:
    """Read `input_csv`, clean records, and write `output_csv`.
    Replaces (does not merge with) existing cleaned data. Returns `output_csv` path.
    """
    if not os.path.exists(input_csv):
        logger.error("No extracted file found at %s", input_csv)
        return None

    df = pd.read_csv(input_csv)

    # Basic parsing and type fixes
    if 'at' in df.columns:
        df['at'] = pd.to_datetime(df['at'], errors='coerce')

    if 'total' in df.columns:
        # stored in cents, convert to dollars
        df['total'] = pd.to_numeric(df['total'], errors='coerce') / 100

    # Normalize boolean column
    if 'has_card_reader' in df.columns:
        df['has_card_reader'] = df['has_card_reader'].fillna(
            0).astype(int).astype(bool)

    # Fill or tag common missing fields
    if 'payment_method' in df.columns:
        df['payment_method'] = df['payment_method'].fillna('unknown')

    # Drop rows missing essential keys (timestamp or transaction id)
    essential = []
    if 'at' in df.columns:
        essential.append('at')
    if 'transaction_id' in df.columns:
        essential.append('transaction_id')
    if essential:
        df = df.dropna(subset=essential)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)
    logger.info("Wrote cleaned data (%d rows) to %s",
                len(df), output_csv)
    return output_csv
