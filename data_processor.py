"""
This script process the dataset for survival analysis
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
    dp = DataProcessor()
    df_json_features = dp.extract_features_from_json()
    df_csv_features = dp.extract_features_from_csv()
    df = pd.merge(df_json_features, df_csv_features,
                  on='issuekey', how='outer')
    df = dp.reduce(df)

    path = "./output/apache_features.csv"
    df.to_csv(path, sep='\t', index=False)


class DataProcessor:
    """ Handles data processing.
    """

    def extract_features_from_json(self):
        """ Extract features from issues that are saved as individual json files.

        Returns:
            df: Dataframe containing issues as rows and features as columns
        """
        scraped_issues_dir = os.fsencode("./input/issues/")
        rows_list = []
        for filename in os.listdir(scraped_issues_dir):
            file_path = os.path.join(scraped_issues_dir, filename)
            issue = self.get_dict_from_JSON_file(file_path)
            issuekey = self.get_feature_issuekey(filename)
            days = self.get_feature_days(issue)
            death = self.get_feature_death(issue)
            priority = self.get_feature_priority(issue)
            issuetype = self.get_feature_issuetype(issue)

            row = {'issuekey': issuekey,
                   'days': days,
                   'death': death,
                   'priority': priority,
                   'issuetype': issuetype,
                   }
            rows_list.append(row)

        columns = ['issuekey', 'days', 'death', 'priority', 'issuetype']
        df = pd.DataFrame(rows_list, columns=columns)
        return df

    def extract_features_from_csv(self):
        """ Extract features from original paper csv dataset.

        Returns:
            df: Dataframe containing issues as rows and features as columns
        """
        original_dataset_path = "./input/original_dataset/apache_creation.csv"
        df = pd.read_csv(original_dataset_path)
        print(df.head())
        df = df.loc[:,
                    ['issuekey', 'reporterrep', 'no_fixversion',
                     'no_issuelink', 'no_affectversion']]
        return df

    def reduce(self, df):
        """ Reduce and modifiy some features in the dataset

        Example of operations include stratifying a feature's value into
        quartiles and grouping the values of a feature when not enough
        examples are included.

        Args:
            df: Dataframe issues as rows and features as columns
        Returns:
            df: Reduced dataframe.
        """
        # group features that contain too few examples
        df.loc[df['issuetype'] > 4, 'issuetype'] = 5
        df.loc[df['no_fixversion'] > 2, 'no_fixversion'] = 3
        df.loc[df['no_issuelink'] > 3, 'no_issuelink'] = 4
        df.loc[df['no_affectversion'] > 2, 'no_affectversion'] = 3

        # separate reporterrep into quartiles
        mask = (df['reporterrep'] >= 0) & (df['reporterrep'] <= 0.25)
        df.loc[mask, 'reporterrep'] = 1
        mask = (df['reporterrep'] > 0.25) & (df['reporterrep'] <= 0.5)
        df.loc[mask, 'reporterrep'] = 2
        mask = (df['reporterrep'] > 0.5) & (df['reporterrep'] <= 0.75)
        df.loc[mask, 'reporterrep'] = 3
        mask = (df['reporterrep'] > 0.75) & (df['reporterrep'] < 1)
        df.loc[mask, 'reporterrep'] = 4

        return df

    def get_feature_issuekey(self, issue_filename):
        """  Gets the issuekey from an issue's filename

        Args:
            issue_filename: Name of the JSON file containing an issue
        Returns:
            issue_key: Issuekey as a string
        """
        issue_key = str(issue_filename)[2:-1]
        return issue_key

    def get_feature_days(self, issue):
        """ Gets feature survival (in days) of an issue

        Args:
            issue: A dict containing an issue's data
        Returns:
            days: Number of days the issue survives as an int
        """
        opened_date = issue['fields']['created']
        resolutiondate = issue['fields']['resolutiondate']
        opened_date = parse(opened_date)
        if resolutiondate is None:
            print("Issue still open:" + issue['key'])
            current_datetime = datetime.now(timezone.utc)
            days = (current_datetime - opened_date).days
        else:
            resolutiondate = parse(resolutiondate)
            days = (resolutiondate - opened_date).days
        return days

    def get_feature_death(self, issue):
        """ Gets the feature event of an issue

        Value of death=0 means the issue is censored at the end of the
        observation whereas death=1 means the issue is dead at the end
        of the observation

        Args:
            issue: A dict containing an issue's data
        Returns:
            death: Int containing the death status
        """
        resolutiondate = issue['fields']['resolutiondate']
        if resolutiondate is None:
            death = 0
        else:
            death = 1
        return death

    def get_feature_priority(self, issue):
        """ Gets feature "priority" of an issue

        Args:
            issue: A dict containing an issue's data
        Returns:
            priority: Int containing the priority of the issue
        """
        priority = issue['fields']['priority']['id']
        return int(priority)

    def get_feature_issuetype(self, issue):
        """ Gets feature "issuetype" of an issue

        Args:
            issue: A dict containing an issue's data
        Returns:
            issuetype: Int containing the issuetype of the issue
        """
        issuetype = issue['fields']['issuetype']['id']
        return int(issuetype)

    def get_dict_from_JSON_file(self, path):
        """ Extracts an issue's data from a JSON file

        Args:
            path: path of a JSON file
        Returns:
            issue: Dict containing the issue's data
        """
        with open(path, 'r') as f:
            issue = json.load(f)
        return issue


if __name__ == '__main__':
    main()
