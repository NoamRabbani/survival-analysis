"""
This script contains the functionality to map and reduce a raw CSV dataset
of JIRA issues and output a filtered CSV dataset.

Copyright (C) 2019  Noam Rabbani
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
Email: hello@noamrabbani.com
"""


import unittest
import json
import os
import datetime
import pandas as pd
import numpy as np
from dateutil.parser import parse
from copy import deepcopy
from datetime import datetime, timezone


def main():
    dataset_input_path = "./dataset/hbase_features_raw.csv"
    dataset_output_path = "./dataset/hbase_features_filtered.csv"

    data_filter = DataFilter()
    df = pd.read_csv(dataset_input_path, sep='\t')
    df = data_filter.map_df(df)
    df, discarded_rows = data_filter.reduce_df(df)
    print("Filtered {} rows".format(discarded_rows))

    df.to_csv(dataset_output_path, sep='\t', index=False)


class DataFilter:
    """ Handles filtering of raw CSV dataset containing JIRA issues.
    """

    def map_df(self, df):
        """ Maps features in the dataset from one value to another

        Args:
            df: Dataframe issues as rows and features as columns
        Returns:
            df: Mapped dataframe.
        """

        # Group sparse issuetype categories ( < 1%)
        df.loc[df['issuetype'] == 13, 'issuetype'] = 5
        df.loc[df['issuetype'] == 14, 'issuetype'] = 5

        # Add one to comment counts
        # df['comment_count'] += 1

        return df

    def reduce_df(self, df):
        """ Reduce rows in the dataset

        Args:
            df: Dataframe issues as rows and features as columns
        Returns:
            df: Reduced dataframe.
        """
        initial_len = len(df)

        # Remove issues that survive more than 3 years
        # df = df[df.days < 1095]

        discarded_rows = initial_len - len(df)

        return df, discarded_rows


if __name__ == '__main__':
    main()
