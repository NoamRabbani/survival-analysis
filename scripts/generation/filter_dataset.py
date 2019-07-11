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
    df = pd.read_csv(dataset_input_path, sep='\t')
    initial_row_count = df.shape[0]

    f = Filter()
    df = f.filter_out_issues(df, "comment_count", 30)
    df = f.filter_out_issues(df, "end", 100)

    final_row_count = df.shape[0]
    print("Filtered out {} rows".format(initial_row_count-final_row_count))
    df.to_csv(dataset_output_path, sep='\t', index=False)


class Filter:
    """ Handles filtering of raw CSV dataset containing JIRA issues.
    """

    def filter_out_issues(self, df, feature, threshold):
        """ Reduce rows in the dataset

        Args:
            df: Dataframe issues as rows and features as columns
        Returns:
            df: Reduced dataframe.
        """

        issues = set(df.loc[df[feature] > threshold]["issuekey"].values)
        df = df[~df['issuekey'].isin(issues)]

        return df


if __name__ == '__main__':
    main()
