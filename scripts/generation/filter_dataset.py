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
import sys


def main():

    if len(sys.argv) < 2:
        print("Must specify project to scrape")
        exit()

    project = sys.argv[1]

    input_paths = {"raw_dataset": "./datasets/{}/survsplit.csv".format(project),  # noqa
                   "outliers": "./artifacts/{}/outliers.csv".format(project)}  # noqa
    output_paths = {"filtered_dataset": "./datasets/{}/filtered.csv".format(project)}  # noqa

    df = pd.read_csv(input_paths["raw_dataset"], sep='\t')
    initial_issue_count = df["issuekey"].nunique()

    f = Filter()
    # df = f.filter_outliers(df, input_paths["outliers"])
    df = f.censor_observations(df, 365)

    final_issue_count = df["issuekey"].nunique()
    delta_issue_count = initial_issue_count-final_issue_count
    print("Filtered {} out of {} issues ({:.2f}%)".format(
        delta_issue_count, initial_issue_count,
        delta_issue_count/initial_issue_count*100))

    df.to_csv(output_paths["filtered_dataset"], sep='\t', index=False)


class Filter:
    """ Handles filtering of raw CSV dataset containing JIRA issues.
    """

    def filter_feature(self, df, feature, threshold):
        """ Removes issues that contains a feature above a threshold

        Args:
            df: Dataframe issues as rows and features as columns
            feature: String of the feature to consider
            threshold: Cutoff threshold
        Returns:
            df: Filtered dataframe.
        """
        issues = set(df.loc[df[feature] > threshold]["issuekey"].values)
        df = df[~df['issuekey'].isin(issues)]

        return df

    def filter_outliers(self, df, which_influence_path):
        """ Removes issues overly influential observations

        Based on the output of which.influence in R

        Args:
            df: Dataframe issues as rows and features as columns
            which_influence_path: Path of df containing overly influential
                                     observations
        Returns:
            df: Filtered dataframe.
        """
        which_influence_df = pd.read_csv(which_influence_path)
        rows = sorted(list(set(which_influence_df.iloc[:, 0])))
        print(max(rows))
        issues = set(df.iloc[rows, 0])
        df = df[~df['issuekey'].isin(issues)]

        return df

    def censor_observations(self, df, days):
        """ Right censor observations in the dataset

        Removes rows where end > days

        Args:
            df: Dataframe issues as rows and features as columns
            days: Cutoff point in days
        Returns:
            df: Filtered dataframe.
        """
        df = df.drop(df[df.end > days].index)
        return df


if __name__ == '__main__':
    main()
