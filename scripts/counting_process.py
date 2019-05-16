"""
This script contains the functionality to parse JIRA issues in JSON format
and create a CSV dataset in the counting process format.

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
import bisect


def main():
    cp = CountingProcess()
    issues_dir = "issues_hbase/"
    output_dir = "./dataset/hbase_features_raw.csv"

    cp.generate_dataset(issues_dir, output_dir)
    # rows = cp.process_issue("issues_hbase/HBASE-18110")


class CountingProcess:
    """ Handles parsing of JSON issues and transformation to counting process.
    """

    def generate_dataset(self, issues_dir, output_dir):
        """ Generates the dataset in the counting process format

        Args:
            issues_dir: Directory containing issues as separate JSON files
            output_dir: Directory to output the CSV dataset
        """
        rows = []
        for filename in os.listdir(issues_dir):
            path = os.path.join(issues_dir, filename)
            rows.extend(self.process_issue(path))

        columns = ["issuekey",
                   "start",
                   "end",
                   "is_dead",
                   "priority",
                   "is_assigned",
                   "issuetype",
                   "has_priority_change",
                   "has_desc_change"
                   ]
        df = pd.DataFrame(rows, columns=columns)
        df.to_csv(output_dir, sep="\t", index=False)

    def process_issue(self, issue_path, max_observation_time=None):
        """ Extracts features from an issue that has been saved as JSON file

        Processes a JSON file containing an issue's data to extract relevant
        features. Every issue will result in N rows (0 < N < inf) that contain
        the issue's features and how they change over time. This format is
        known as the counting process format for survival analysis.

        Args:
            issue_path: Path to the JSON file containing the issue data
        Returns:
            rows: list of rows containing an issues features in couting process
        """
        with open(issue_path, "r") as f:
            issue = json.load(f)

        issue_states = {"dates": []}
        rows = []
        dates = issue_states["dates"]

        self.append_state_at_resolution_time(
            issue, issue_states)
        self.append_states_from_changelog(issue, issue_states)
        self.append_state_at_creation_time(issue, issue_states)

        self.add_count_features(issue, issue_states)

        # Ignore issues that have been open for more than max_observation_time
        if max_observation_time:
            opening_date = dates[0]
            resolution_date = dates[-1]
            if (resolution_date - opening_date).days > max_observation_time:
                return []

        # two pointer approach to building a counting process dataset
        curr_idx, nxt_idx = 0, 1
        creation_date = dates[0]
        while nxt_idx < len(dates):
            curr_date, nxt_date = dates[curr_idx], dates[nxt_idx]
            issuekey = issue_states[curr_date]["issuekey"]
            start = (curr_date - creation_date).days
            end = (nxt_date - creation_date).days
            is_dead = issue_states[nxt_date]["is_dead"]
            priority = issue_states[curr_date]["priority"]
            is_assigned = issue_states[curr_date]["is_assigned"]
            issuetype = issue_states[curr_date]["issuetype"]
            has_priority_change = (
                issue_states[curr_date]["has_priority_change"])
            has_desc_change = issue_states[curr_date]["has_desc_change"]
            row = {"issuekey": issuekey,
                   "start": start,
                   "end": end,
                   "is_dead": is_dead,
                   "priority": priority,
                   "is_assigned": is_assigned,
                   "issuetype": issuetype,
                   "has_priority_change": has_priority_change,
                   "has_desc_change": has_desc_change,
                   }
            rows.append(row)
            curr_idx += 1
            nxt_idx += 1

        return rows

    def append_state_at_resolution_time(self, issue, issue_states):
        """ Appends the state of an issue at its resolution time

        Args:
            issue: Dict that contains the issue's data
            issue_states: Dict containg the states of the issue at the dates
                          of interest
        """
        if issue["fields"]["resolutiondate"] is None:
            date = datetime.now(timezone.utc).date()
            is_dead = 0
        else:
            date = parse(issue["fields"]["resolutiondate"]).date()
            is_dead = 1

        issuekey = issue["key"]
        priority = self.get_feature_priority(issue)
        is_assigned = self.get_feature_is_assigned(issue)
        issuetype = self.get_feature_issuetype(issue)
        desc = self.get_feature_desc(issue)

        state = {"issuekey": issuekey,
                 "is_dead": is_dead,
                 "priority": priority,
                 "is_assigned": is_assigned,
                 "issuetype": issuetype,
                 "desc": desc
                 }

        bisect.insort(issue_states["dates"], date)
        issue_states[date] = state

    def append_states_from_changelog(self, issue, issue_states):
        """ Extract states from an issue's changelog in reverse chronogical order

        Args:
            issue: Dict that contains the issue's data
            issue_states: Dict containg the states of the issue at the dates
                          of interest
        """
        for change in reversed(issue["changelog"]["histories"]):
            date = parse(change["created"]).date()
            for item in change["items"]:
                if item["field"] == "priority":
                    self.append_state_at_priority_change(
                        issue, item, date, issue_states)
                if item["field"] == "assignee":
                    self.append_state_at_assignee_change(
                        issue, item, date, issue_states)
                if item["field"] == "issuetype":
                    self.append_state_at_issuetype_change(
                        issue, item, date, issue_states)
                if item["field"] == "description":
                    self.append_state_at_desc_change(
                        issue, item, date, issue_states)

    def append_state_at_creation_time(self, issue, issue_states):
        """ Appends the state of an issue at its creation time

        Args:
            issue: Dict that contains the issue's data
            issue_states: Dict containg the states of the issue at the dates
                          of interest
        """
        date = parse(issue["fields"]["created"]).date()

        if date in issue_states["dates"]:
            return
        else:
            state = self.infer_state(date, issue_states)

        bisect.insort(issue_states["dates"], date)
        issue_states[date] = state

    def add_count_features(self, issue, issue_states):
        dates = issue_states["dates"]
        has_priority_change = 0
        has_desc_change = 0
        for date in dates:
            if issue_states[date].get("previous_priority"):
                has_priority_change = 1
            if issue_states[date].get("previous_desc"):
                has_desc_change = 1
            issue_states[date]["has_priority_change"] = has_priority_change
            issue_states[date]["has_desc_change"] = has_desc_change

    def append_state_at_priority_change(self, issue, item, date, issue_states):
        """ Appends the state of an issue when the priority changes

        Args:
            issue: Dict that contains the issue's data
            item: Dict that contains the item that was changed
            date: Datetime on which the change occured
            issue_states: Dict containg the states of the issue at the dates
                          of interest
        """
        dates = issue_states["dates"]
        resolution_date = dates[-1]
        if date > resolution_date:
            return

        if date in dates:
            issue_states[date]["previous_priority"] = int(item["from"])
        else:
            state = self.infer_state(date, issue_states)
            state["previous_priority"] = int(item["from"])
            bisect.insort(issue_states["dates"], date)
            issue_states[date] = state

    def append_state_at_assignee_change(self, issue, item, date, issue_states):
        """ Appends the state of an issue when the assignee changes

        Args:
            issue: Dict that contains the issue's data
            item: Dict that contains the item that was changed
            date: Datetime on which the change occured
            issue_states: Dict containg the states of the issue at the dates
                          of interest
        """
        dates = issue_states["dates"]
        resolution_date = dates[-1]
        if date > resolution_date:
            return

        if item["from"] is None:
            previous_is_assigned = 0
        else:
            previous_is_assigned = 1

        if date in dates:
            issue_states[date]["previous_is_assigned"] = previous_is_assigned
        else:
            state = self.infer_state(date, issue_states)
            state["previous_is_assigned"] = previous_is_assigned
            bisect.insort(issue_states["dates"], date)
            issue_states[date] = state

    def append_state_at_issuetype_change(self, issue, item, date,
                                         issue_states):
        """ Appends the state of an issue when the issuetype changes

        Args:
            issue: Dict that contains the issue's data
            item: Dict that contains the item that was changed
            date: Datetime on which the change occured
            issue_states: Dict containg the states of the issue at the dates
                          of interest
        """
        dates = issue_states["dates"]
        resolution_date = dates[-1]
        if date > resolution_date:
            return

        if date in dates:
            issue_states[date]["previous_issuetype"] = int(item["from"])
        else:
            state = self.infer_state(date, issue_states)
            state["previous_issuetype"] = int(item["from"])
            bisect.insort(issue_states["dates"], date)
            issue_states[date] = state

    def append_state_at_desc_change(self, issue, item, date,
                                    issue_states):
        """ Appends the state of an issue when the issuetype changes

        Args:
            issue: Dict that contains the issue's data
            item: Dict that contains the item that was changed
            date: Datetime on which the change occured
            issue_states: Dict containg the states of the issue at the dates
                          of interest
        """
        dates = issue_states["dates"]
        resolution_date = dates[-1]
        if date > resolution_date:
            return

        if date in dates:
            issue_states[date]["previous_desc"] = item["fromString"]
        else:
            state = self.infer_state(date, issue_states)
            state["previous_desc"] = item["fromString"]
            bisect.insort(issue_states["dates"], date)
            issue_states[date] = state

    def infer_state(self, date, issue_states):
        """  Infers the state of an issue at a given point in time

        Args:
            issue: Dict that contains the issue's data
        Returns:
            state: Issuekey as a string
        """
        idx = bisect.bisect(issue_states["dates"], date)
        next_date = issue_states["dates"][idx]

        is_dead = 0
        reference_state = issue_states[next_date]
        issuekey = reference_state.get("issuekey")

        if reference_state.get("previous_priority") is None:
            priority = issue_states[next_date]["priority"]
        else:
            priority = issue_states[next_date]["previous_priority"]

        if reference_state.get("previous_is_assigned") is None:
            is_assigned = issue_states[next_date]["is_assigned"]
        else:
            is_assigned = issue_states[next_date]["previous_is_assigned"]

        if reference_state.get("previous_issuetype") is None:
            issuetype = issue_states[next_date]["issuetype"]
        else:
            issuetype = issue_states[next_date]["previous_issuetype"]

        if reference_state.get("previous_desc") is None:
            desc = issue_states[next_date]["desc"]
        else:
            desc = issue_states[next_date]["previous_desc"]

        state = {"issuekey": issuekey,
                 "is_dead": is_dead,
                 "priority": priority,
                 "is_assigned": is_assigned,
                 "issuetype": issuetype,
                 "desc": desc
                 }

        return state

    def get_feature_priority(self, issue):
        """ Gets feature "priority" of an issue

        Args:
            issue: A dict containing an issue's data
        Returns:
            priority: Int containing the priority of the issue
        """
        if issue["fields"]["priority"].get("id"):
            priority = int(issue["fields"]["priority"]["id"])
        else:
            priority = -1
            print("Malformed issue: " + issue["key"])
        return priority

    def get_feature_is_assigned(self, issue):
        """ Gets feature "is_assigned" of an issue

        Args:
            issue: A dict containing an issue's data
        Returns:
            is_assigned: Int (0,1) indicating if wether there's an assignee
        """
        if issue["fields"]["assignee"]:
            is_assigned = 1
        else:
            is_assigned = 0
        return is_assigned

    def get_feature_issuetype(self, issue):
        """ Gets feature "issuetype" of an issue

        Args:
            issue: A dict containing an issue's data
        Returns:
            issuetype: Int containing the issuetype of the issue
        """
        if issue["fields"]["issuetype"].get("id"):
            issuetype = int(issue["fields"]["issuetype"]["id"])
        else:
            issuetype = -1
            print("Malformed issue: " + issue["key"])
        return issuetype

    def get_feature_desc(self, issue):
        """ Gets feature "desc" of an issue

        Args:
            issue: A dict containing an issue's data
        Returns:
            desc: String containing the description of an issue
        """
        if issue["fields"].get("description"):
            desc = issue["fields"]["description"]
        else:
            desc = ""
        return desc


if __name__ == "__main__":
    main()
