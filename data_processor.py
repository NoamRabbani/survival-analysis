"""
This script parses JSON issues and creates a csv data set
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
Email: contact@noamrabbani.com
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

    def extract_features_from_json(self):
        """ Extract features from JIRA issues and returns them as a dataframe
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
        """ Extract features from original paper csv dataset and return them as a dataframe
        """
        original_dataset_path = "./input/original_dataset/apache_creation.csv"
        df = pd.read_csv(original_dataset_path)
        print(df.head())
        df = df.loc[:,
                    ['issuekey', 'reporterrep', 'no_fixversion', 'no_issuelink', 'no_affectversion']]
        return df

    def reduce(self, df):
        """ Reduce and modifiy some features in the dataset
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
        """ Return the feature issuekey of the issue as a string
        """
        return str(issue_filename)[2:-1]

    def get_feature_days(self, issue):
        """ Return the feature survival (in days) of the issue as an int
        """
        opened_date = issue['fields']['created']
        resolutiondate = issue['fields']['resolutiondate']
        opened_date = parse(opened_date)
        if resolutiondate == None:
            print("Issue still open:" + issue['key'])
            current_datetime = datetime.now(timezone.utc)
            days = (current_datetime - opened_date).days
        else:
            resolutiondate = parse(resolutiondate)
            days = (resolutiondate - opened_date).days
        return days

    def get_feature_death(self, issue):
        """ Return the feature event of the issue as an int
            death=0 means the issue is alive, death=1 means the issue is dead
        """
        resolutiondate = issue['fields']['resolutiondate']
        if resolutiondate == None:
            death = 0
        else:
            death = 1
        return death

    def get_feature_priority(self, issue):
        """ Return the feature priority of the issue as a int
        """
        priority = issue['fields']['priority']['id']
        return int(priority)

    def get_feature_issuetype(self, issue):
        """ Return the feature issuetype of the issue as an int
        """
        issuetype = issue['fields']['issuetype']['id']
        return int(issuetype)

    def get_dict_from_JSON_file(self, path):
        """ Return a dict containing an issue's data
        """
        with open(path, 'r') as f:
            issue = json.load(f)
        return issue


if __name__ == '__main__':
    # unittest.main(exit=False)
    main()
