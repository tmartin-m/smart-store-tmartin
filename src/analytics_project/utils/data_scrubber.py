# src/analytics_project/utils/data_scrubber.py

import pandas as pd


class DataScrubber:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def remove_duplicate_records(self):
        """
        Removes duplicate rows from the DataFrame.
        Keeps the first occurrence of each duplicate.
        """
        return self.df.drop_duplicates()
