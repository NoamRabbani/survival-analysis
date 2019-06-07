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
import bisect
import logging
import pandas as pd
from dateutil.parser import parse
from copy import deepcopy
from datetime import datetime, timezone


def main():
    logging.basicConfig(level=logging.INFO, filename="log", filemode='w')
    cp = CountingProcess()
    issues_dir = "issues_hbase/"
    output_path = "./dataset/hbase_features_raw.csv"

    cp.generate_dataset(issues_dir, output_path)
    # rows = cp.process_issue("issues_hbase/HBASE-16609")


class CountingProcess:
    """ Handles parsing of JSON issues and transformation to counting process.
    """

    def generate_dataset(self, issues_dir, output_path):
        """ Generates the dataset in the counting process format

        Args:
            issues_dir: Directory containing issues as separate JSON files
            output_path: Path to output the CSV dataset
        """
        rows = []
        for filename in os.listdir(issues_dir):
            path = os.path.join(issues_dir, filename)
            issue_rows = self.process_issue(path)
            rows.extend(issue_rows)

        columns = ["issuekey",
                   "start",
                   "end",
                   "is_dead",
                   "priority",
                   "is_assigned",
                   "issuetype",
                   "has_priority_change",
                   "has_desc_change",
                   "comment_count",
                   "link_count"
                   ]
        df = pd.DataFrame(rows, columns=columns)
        df.to_csv(output_path, sep="\t", index=False)

    def process_issue(self, issue_path):
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

        issue_states = {}
        issue_dates = []
        rows = []

        creation_date = parse(issue["fields"]["created"]).date()
        if issue["fields"]["resolutiondate"] is None:
            resolution_date = datetime.now(timezone.utc).date()
        else:
            resolution_date = parse(issue["fields"]["resolutiondate"]).date()

        if creation_date == resolution_date:
            logging.info("Filtered out {} because resolution date is equal to "
                         "creation date".format(issue["key"]))
            return rows

        self.append_state_at_current_time(issue, issue_states, issue_dates)
        self.append_states_from_changelog(issue, issue_states, issue_dates)
        self.append_state_at_creation_time(issue, issue_states, issue_dates)
        self.append_state_at_resolution_time(issue, issue_states, issue_dates)

        self.add_comment_features(issue, issue_states, issue_dates)
        self.add_count_features(issue, issue_states, issue_dates)

        # two pointer approach to building a counting process dataset
        curr_idx, nxt_idx = 0, 1
        while nxt_idx < len(issue_dates):
            curr_date, nxt_date = issue_dates[curr_idx], issue_dates[nxt_idx]
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
            comment_count = issue_states[curr_date]["comment_count"]
            link_count = issue_states[curr_date]["link_count"]
            row = {"issuekey": issuekey,
                   "start": start,
                   "end": end,
                   "is_dead": is_dead,
                   "priority": priority,
                   "is_assigned": is_assigned,
                   "issuetype": issuetype,
                   "has_priority_change": has_priority_change,
                   "has_desc_change": has_desc_change,
                   "comment_count": comment_count,
                   "link_count": link_count
                   }
            rows.append(row)
            if is_dead:
                break
            else:
                curr_idx += 1
                nxt_idx += 1

        return rows

    def append_state_at_current_time(self, issue, issue_states, issue_dates):
        """ Appends the state of an issue at the current time.

        Args:
            issue: Dict that contains the issue's data.
            issue_states: Dict containg the states of the issue at the dates
                          of interest.
            issue_dates: Dates of interest, on which an issue changes its
                         state.
        """
        date = datetime.now(timezone.utc).date()
        is_dead = 0

        issuekey = issue["key"]
        priority = self.get_feature("priority", issue)
        is_assigned = self.get_feature("is_assigned", issue)
        issuetype = self.get_feature("issuetype", issue)
        desc = self.get_feature("desc", issue)
        link_count = self.get_feature("link_count", issue)

        state = {"issuekey": issuekey,
                 "is_dead": is_dead,
                 "priority": priority,
                 "is_assigned": is_assigned,
                 "issuetype": issuetype,
                 "desc": desc,
                 "link_count": link_count
                 }

        bisect.insort(issue_dates, date)
        issue_states[date] = state

    def append_states_from_changelog(self, issue, issue_states, issue_dates):
        """ Extract states from an issue's changelog in reverse chronogical order.

        Args:
            issue: Dict that contains the issue's data
            issue_states: Dict containg the states of the issue at the dates
                          of interest.
            issue_dates: Dates of interest, on which an issue changes its
                         state.
        """
        for change in reversed(issue["changelog"]["histories"]):
            date = parse(change["created"]).date()
            for item in change["items"]:
                if item["field"] == "priority":
                    self.append_state_at_feature_change(
                        "priority", issue, item, date, issue_states,
                        issue_dates)
                if item["field"] == "assignee":
                    self.append_state_at_feature_change(
                        "assignee", issue, item, date, issue_states,
                        issue_dates)
                if item["field"] == "issuetype":
                    self.append_state_at_feature_change(
                        "issuetype", issue, item, date, issue_states,
                        issue_dates)
                if item["field"] == "description":
                    self.append_state_at_feature_change(
                        "desc", issue, item, date, issue_states,
                        issue_dates)
                if item["field"] == "Link":
                    self.append_state_at_feature_change(
                        "link_count", issue, item, date, issue_states,
                        issue_dates)

    def append_state_at_creation_time(self, issue, issue_states,
                                      issue_dates):
        """ Appends the state of an issue at its creation time.

        Args:
            issue: Dict that contains the issue's data
            issue_states: Dict containg the states of the issue at the dates
                          of interest.
            issue_dates: Dates of interest, on which an issue changes its
                         state.
        """
        date = parse(issue["fields"]["created"]).date()

        if date in issue_dates:
            return
        else:
            state = self.infer_state(date, issue_states, issue_dates)
            bisect.insort(issue_dates, date)
            issue_states[date] = state

    def append_state_at_resolution_time(self, issue, issue_states, issue_dates):
        """ Appends the state of an issue at its resolution time.

        Args:
            issue: Dict that contains the issue's data
            issue_states: Dict containg the states of the issue at the dates
                          of interest.
            issue_dates: Dates of interest, on which an issue changes its
                         state.
        """
        if issue["fields"]["resolutiondate"] is None:
            return
        else:
            resolution_date = parse(issue["fields"]["resolutiondate"]).date()
            is_dead = 1
            if resolution_date in issue_dates:
                issue_states[resolution_date]["is_dead"] = is_dead
            else:
                state = self.infer_state(
                    resolution_date, issue_states, issue_dates)
                state["is_dead"] = is_dead
                bisect.insort(issue_dates, resolution_date)
                issue_states[resolution_date] = state

    def add_count_features(self, issue, issue_states, issue_dates):
        """ Goes through the issue states and add count features.

        Args:
            issue: Dict that contains the issue's data.
            issue_states: Dict containg the states of the issue at the dates
                          of interest.
        """
        has_priority_change = 0
        has_desc_change = 0
        for date in issue_dates:
            if issue_states[date].get("previous_priority"):
                has_priority_change = 1
            if issue_states[date].get("previous_desc"):
                has_desc_change = 1
            issue_states[date]["has_priority_change"] = has_priority_change
            issue_states[date]["has_desc_change"] = has_desc_change

    def add_comment_features(self, issue, issue_states, issue_dates):
        """ Adds the comment_count feature to the issue_states

        Args:
            issue: Dict that contains the issue's data
            issue_states: Dict containg the states of the issue at the dates
                          of interest
            issue_dates: Dates of interest, on which an issue changes its
                         state.
        """
        comment_count = 0

        # We first do a pass on the comment log and update states on dates
        # where comments have been written
        for comment in issue["comments"]:
            date = parse(comment["created"]).date()
            comment_count += 1
            if date in issue_dates:
                issue_states[date]["comment_count"] = comment_count
            else:
                state = self.infer_state(date, issue_states, issue_dates)
                state["comment_count"] = comment_count
                bisect.insort(issue_dates, date)
                issue_states[date] = state

        # We then do a pass on all states to give each of them the proper
        # comment_count feature
        comment_count = 0
        for date in issue_dates:
            if issue_states[date].get("comment_count") is None:
                issue_states[date]["comment_count"] = comment_count
            else:
                comment_count = issue_states[date]["comment_count"]

    def append_state_at_feature_change(self, feature, issue, item, date,
                                       issue_states, issue_dates):
        """ Appends the state of an issue when a feature changes.

        Args:
            feature: Feature that changed.
            issue: Dict that contains the issue's data.
            item: Dict that contains the item that was changed.
            date: Datetime on which the change occured.
            issue_states: Dict containg the states of the issue at the dates
                          of interest.
            issue_dates: Dates of interest, on which an issue changes its
                         state.
        """
        if feature == "priority":
            if date in issue_dates:
                issue_states[date]["previous_priority"] = int(item["from"])
            else:
                state = self.infer_state(date, issue_states, issue_dates)
                state["previous_priority"] = int(item["from"])
                bisect.insort(issue_dates, date)
                issue_states[date] = state

        elif feature == "assignee":
            if item["from"] is None:
                previous_is_assigned = 0
            else:
                previous_is_assigned = 1
            if date in issue_dates:
                issue_states[date]["previous_is_assigned"] = (
                    previous_is_assigned)
            else:
                state = self.infer_state(date, issue_states, issue_dates)
                state["previous_is_assigned"] = previous_is_assigned
                bisect.insort(issue_dates, date)
                issue_states[date] = state

        elif feature == "issuetype":
            if date in issue_dates:
                issue_states[date]["previous_issuetype"] = int(item["from"])
            else:
                state = self.infer_state(date, issue_states, issue_dates)
                state["previous_issuetype"] = int(item["from"])
                bisect.insort(issue_dates, date)
                issue_states[date] = state

        elif feature == "desc":
            if date in issue_dates:
                issue_states[date]["previous_desc"] = item["fromString"]
            else:
                state = self.infer_state(date, issue_states, issue_dates)
                state["previous_desc"] = item["fromString"]
                bisect.insort(issue_dates, date)
                issue_states[date] = state

        elif feature == "link_count":
            if date in issue_dates:
                if item["from"]:
                    if issue_states[date].get("previous_link_count"):
                        issue_states[date]["previous_link_count"] += 1
                    else:
                        issue_states[date]["previous_link_count"] = (
                            issue_states[date]["link_count"] + 1)
                elif item["to"]:
                    if issue_states[date].get("previous_link_count"):
                        issue_states[date]["previous_link_count"] -= 1
                    else:
                        issue_states[date]["previous_link_count"] = (
                            issue_states[date]["link_count"] - 1)
                else:
                    logging.INFO(
                        "Issue has both 'to' and 'from' in link feature")
            else:
                state = self.infer_state(date, issue_states, issue_dates)
                if item["from"]:
                    state["previous_link_count"] = (
                        state["link_count"] + 1)
                elif item["to"]:
                    state["previous_link_count"] = (
                        state["link_count"] - 1)
                else:
                    logging.INFO(
                        "Issue has both 'to' and 'from' in link feature")
                bisect.insort(issue_dates, date)
                issue_states[date] = state

        else:
            raise ValueError()

    def infer_state(self, date, issue_states, issue_dates):
        """  Infers the state of an issue at a given point in time.

        Args:
            date: Date on which we want to infer a state.
            issue_states: Dict containg the states of the issue at the dates
                          of interest.
        Returns:
            state: Issuekey as a string.
        """
        idx = bisect.bisect(issue_dates, date)

        next_date = issue_dates[idx]
        reference_state = issue_states[next_date]

        is_dead = 0
        issuekey = reference_state["issuekey"]

        if reference_state.get("previous_priority") is None:
            priority = reference_state["priority"]
        else:
            priority = reference_state["previous_priority"]

        if reference_state.get("previous_is_assigned") is None:
            is_assigned = reference_state["is_assigned"]
        else:
            is_assigned = reference_state["previous_is_assigned"]

        if reference_state.get("previous_issuetype") is None:
            issuetype = reference_state["issuetype"]
        else:
            issuetype = reference_state["previous_issuetype"]

        if reference_state.get("previous_desc") is None:
            desc = reference_state["desc"]
        else:
            desc = reference_state["previous_desc"]

        if reference_state.get("previous_link_count") is None:
            link_count = reference_state["link_count"]
        else:
            link_count = reference_state["previous_link_count"]

        state = {"issuekey": issuekey,
                 "is_dead": is_dead,
                 "priority": priority,
                 "is_assigned": is_assigned,
                 "issuetype": issuetype,
                 "desc": desc,
                 "link_count": link_count,
                 }

        return state

    def get_feature(self, feature, issue):
        """ Gets a feature from an issue's

        Args:
            feature: String of the feature to get
            issue: A dict containing an issue's data
        Returns:
            priority: Int containing the priority of the issue
        """
        if feature == "priority":
            if issue["fields"]["priority"].get("id"):
                priority = int(issue["fields"]["priority"]["id"])
            else:
                priority = -1
                print("Malformed issue: " + issue["key"])
            return priority

        elif feature == "is_assigned":
            if issue["fields"]["assignee"]:
                is_assigned = 1
            else:
                is_assigned = 0
            return is_assigned

        elif feature == "issuetype":
            if issue["fields"]["issuetype"].get("id"):
                issuetype = int(issue["fields"]["issuetype"]["id"])
            else:
                issuetype = -1
                print("Malformed issue: " + issue["key"])
            return issuetype

        elif feature == "desc":
            if issue["fields"].get("description"):
                desc = issue["fields"]["description"]
            else:
                desc = ""
            return desc

        elif feature == "link_count":
            if issue["fields"].get("issuelinks"):
                link_count = len(issue["fields"]["issuelinks"])
            else:
                link_count = 0
            return link_count

        else:
            raise ValueError()


if __name__ == "__main__":
    main()
