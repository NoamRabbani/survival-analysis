"""
This script contains the functionality to parse JIRA issues in JSON format
and create a raw dataset in CSV format.

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
    dp = DataParser()

    df, discarded_issues = dp.extract_features_from_json("./issues/")
    df.to_csv("./dataset/apache_features_raw.csv", sep='\t', index=False)
    print("Discared {} malformed issues".format(discarded_issues))


class DataParser:
    """ Handles parsing of JSON issues.
    """

    def extract_features_from_json(self, scraped_issues_dir):
        """ Extract features from issues that are saved as individual json files.

        Args:
            scraped_issues_dir: Path to JSON issues
        Returns:
            df: Dataframe containing issues as rows and features as columns
        """
        rows_list = []
        discarded_issues = 0
        for filename in os.listdir(scraped_issues_dir):
            path = os.path.join(scraped_issues_dir, filename)
            with open(path, 'r') as f:
                issue = json.load(f)

            # features
            issuekey = self.get_feature_issuekey(issue)
            starttime = self.get_feature_starttime(issue)
            endtime = self.get_feature_endtime(issue)
            days = endtime - starttime
            death = self.get_feature_death(issue)
            priority = self.get_feature_priority(issue)
            issuetype = self.get_feature_issuetype(issue)
            fixversions = self.get_feature_fixversions(issue)
            issuelinks = self.get_feature_issuelinks(issue)

            # Discard issue if it's malformed
            if priority == -1 or issuetype == -1:
                discarded_issues += 1
            # Append issue to dataset if it's well formed
            else:
                row = {'issuekey': issuekey,
                       'starttime': starttime,
                       'endtime': endtime,
                       'days': days,
                       'death': death,
                       'priority': priority,
                       'issuetype': issuetype,
                       'fixversions': fixversions,
                       'issuelinks': issuelinks,
                       }
                rows_list.append(row)

        columns = ['issuekey', 'starttime', 'endtime', 'days', 'death',
                   'priority', 'issuetype', 'fixversions', 'issuelinks']
        df = pd.DataFrame(rows_list, columns=columns)
        return df, discarded_issues

    def get_feature_issuekey(self, issue):
        """  Gets the issuekey from an issue's filename

        Args:
            issue_filename: Name of the JSON file containing an issue
        Returns:
            issue_key: Issuekey as a string
        """
        issue_key = issue['key']
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
            current_datetime = datetime.now(timezone.utc)
            days = (current_datetime - opened_date).days
        else:
            resolutiondate = parse(resolutiondate)
            days = (resolutiondate - opened_date).days
        return days

    def get_feature_starttime(self, issue):
        """ Gets feature "starttime" of an issue

        Args:
            issue: A dict containing an issue's data
        Returns:
            days: Starting day measured in elapsed days after 2000/10/19
        """
        opened_date = parse(issue['fields']['created'])
        date_2000_10_19 = parse("2000/10/19").replace(tzinfo=timezone.utc)
        starttime = (opened_date - date_2000_10_19).days
        return starttime

    def get_feature_endtime(self, issue):
        """ Gets feature "endtime" of an issue

        Args:
            issue: A dict containing an issue's data
        Returns:
            days: Ending day measured in elapsed days after 2000/10/19
        """
        resolutiondate = issue['fields']['resolutiondate']
        date_2000_10_19 = parse("2000/10/19").replace(tzinfo=timezone.utc)

        if resolutiondate is None:
            current_datetime = datetime.now(timezone.utc)
            endtime = (current_datetime - date_2000_10_19).days
        else:
            resolutiondate = parse(resolutiondate)
            endtime = (resolutiondate - date_2000_10_19).days

        return endtime

    def get_feature_death(self, issue):
        """ Gets the feature "death" of an issue

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
        try:
            priority = int(issue['fields']['priority']['id'])
        except:
            priority = -1
        return priority

    def get_feature_issuetype(self, issue):
        """ Gets feature "issuetype" of an issue

        Args:
            issue: A dict containing an issue's data
        Returns:
            issuetype: Int containing the issuetype of the issue
        """
        issuetype = issue['fields']['issuetype']['id']
        return int(issuetype)

    def get_feature_fixversions(self, issue):
        """ Gets feature "fixversions" of an issue

        Args:
            issue: A dict containing an issue's data
        Returns:
            fixversions: Int containing number of fix versions
        """
        try:
            fixversions = len(issue['fields']['fixVersions'])
        except:
            fixversions = -1
        return fixversions

    def get_feature_issuelinks(self, issue):
        """ Gets feature "issuelinks" of an issue

        Args:
            issue: A dict containing an issue's data
        Returns:
            issuelinks: Int containing number of fix issuelinks
        """
        issuelinks = len(issue['fields']['issuelinks'])
        return issuelinks


if __name__ == '__main__':
    main()
