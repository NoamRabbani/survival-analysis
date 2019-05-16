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
from dateutil.parser import parse
from copy import deepcopy
from datetime import datetime, timezone


def main():
    data_filter = DataFilter()

    df = pd.read_csv("./dataset/apache_features_raw.csv", sep='\t')

    df = data_filter.map_df(df)
    df, discarded_rows = data_filter.reduce_df(df)

    print("Filtered {} rows".format(discarded_rows))
    df.to_csv("./dataset/apache_features_filtered.csv", sep='\t', index=False)


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

        # # Group priority_change_count into two categories (0, 1+)
        # df.loc[df['priority_change_count'] == 2, 'priority_change_count'] = 1
        # df.loc[df['priority_change_count'] == 3, 'priority_change_count'] = 1
        # df.loc[df['priority_change_count'] == 4, 'priority_change_count'] = 1

        # Map priority integers to labels
        # df.loc[df['priority'] == 1, 'priority'] = 'blocker'
        # df.loc[df['priority'] == 2, 'priority'] = 'critical'
        # df.loc[df['priority'] == 3, 'priority'] = 'major'
        # df.loc[df['priority'] == 4, 'priority'] = 'minor'
        # df.loc[df['priority'] == 5, 'priority'] = 'trivial'

        # Map issuetype integers to labels
        # df.loc[df['issuetype'] == 1, 'issuetype'] = 'bug'
        # df.loc[df['issuetype'] == 2, 'issuetype'] = 'newfeature'
        # df.loc[df['issuetype'] == 3, 'issuetype'] = 'task'
        # df.loc[df['issuetype'] == 4, 'issuetype'] = 'improvement'
        # df.loc[df['issuetype'] == 5, 'issuetype'] = 'other'

        # Raise the minimum survival time to 1 day
        # df.loc[df['starttime'] == df['endtime'], 'endtime'] += 1
        # df.loc[df['days'] == 0, 'days'] = 1

        return df

    def reduce_df(self, df):
        """ Reduce rows in the dataset

        Args:
            df: Dataframe issues as rows and features as columns
        Returns:
            df: Reduced dataframe.
        """
        initial_len = len(df)

        # Remove 14,993 CASSANDRA issues because their priority does not
        # conform to the 1-5 scale
        df = df[~df.issuekey.str.contains('CASSANDRA')]

        # Remove issues that survive more than 3 years
        df = df[df.days < 1095]

        discarded_rows = initial_len - len(df)

        return df, discarded_rows


if __name__ == '__main__':
    main()
