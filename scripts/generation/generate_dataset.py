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
import bisect
import logging
import pickle
import pandas as pd
from dateutil.parser import parse
from copy import deepcopy
from datetime import datetime, timezone, timedelta


def main():
    input_paths = {"issues": "issues_hbase/",
                   "reputations": "./cross_issue_data/reputation_timelines.pickle",  # noqa
                   "workloads": "./cross_issue_data/workload_timelines.pickle"}  # noqa
    output_paths = {"hbase_raw": "./dataset/hbase_features_raw.csv"}
    logging.basicConfig(level=logging.INFO, filename="log", filemode='w')
    logging.info("issuekey, reason")

    reputations = None
    workloads = None
    # Comment next four lines to ignore cross-issue features
    with open(input_paths["reputations"], 'rb') as fp:
        reputations = pickle.load(fp)
    with open(input_paths["workloads"], 'rb') as fp:
        workloads = pickle.load(fp)

    cp = CountingProcess()
    cp.generate_dataset(input_paths, output_paths,
                        reputations, workloads)


class CountingProcess:
    """ Generates a counting process dataset from JSON issue data.
    """

    def generate_dataset(self, input_paths, output_paths, reputations=None,
                         workloads=None):
        """ Generates the dataset in the counting process format

        Args:
            input_paths: Dictionary containing paths of input files.
            output_path: Dictionary containing paths of output files
            reputations: Dictionary containing the reputation of each user and
                         how it changes over time.
            workloads: Dictionary containing the workloads of each user and
                         how it changes over time.
        """
        # issue_path = input_paths["issues"] + "HBASE-10051"
        # issue_states, issue_dates = self.generate_issue_states(
        #     issue_path, reputations, workloads)

        rows = []
        for filename in sorted(os.listdir(input_paths["issues"])):
            issue_path = os.path.join(input_paths["issues"], filename)
            issue_states, issue_dates = self.generate_issue_states(
                issue_path, reputations, workloads)
            issue_rows = self.generate_counting_process_rows(
                issue_states, issue_dates, reputations, workloads)
            rows.extend(issue_rows)

        columns = ["issuekey",
                   "start",
                   "end",
                   "is_dead",
                   "priority",
                   "issuetype",
                   "assignee",
                   "is_assigned",
                   "comment_count",
                   "link_count",
                   "affect_count",
                   "fix_count",
                   "has_priority_change",
                   "has_desc_change",
                   "has_fix_change",
                   ]
        if reputations:
            columns.append("reporter_rep")
        if workloads:
            columns.append("assignee_workload")
        df = pd.DataFrame(rows, columns=columns)
        df.to_csv(output_paths["hbase_raw"], sep="\t", index=False)

    def generate_issue_states(self, issue_path, reputations,
                              workloads):
        """ Generates a history of the states of an issue.

        Args:
            issue_path: Path to the JSON file containing the issue data.
            reputations: Dictionary containing the reputation of each user and
                         how it changes over time.
            workloads: Dictionary containing the workloads of each user and
                         how it changes over time.
        Returns:
            issue_states: Dict containg the states of the issue at the dates
                          of interest.
            issue_dates: Dates of interest, on which an issue changes its
                         state.
        """
        with open(issue_path, "r") as f:
            issue = json.load(f)

        creation_date = parse(issue["fields"]["created"]).date()
        resolution_date = self.get_resolution_date(issue)

        if creation_date == resolution_date:
            logging.info(
                "{}, creation_date == resolution_date".format(issue["key"]))
            return [], {}

        issue_dates = []
        issue_states = {}
        self.append_state_at_current_time(issue, issue_states, issue_dates)
        self.append_states_from_changelog(issue, issue_states, issue_dates)
        self.append_state_at_creation(issue, issue_states, issue_dates)
        self.append_state_at_resolution(
            issue, issue_states, issue_dates, resolution_date)

        # Order of these functions matters.
        self.add_comment_features(issue, issue_states, issue_dates)
        if reputations:
            self.add_reporter_rep_feature(
                issue, issue_states, issue_dates, reputations)
        if workloads:
            self.add_assignee_workload_feature(
                issue, issue_states, issue_dates, workloads)
        self.level_issue_states(issue, issue_states,
                                issue_dates, reputations, workloads)
        self.add_count_features(issue, issue_states, issue_dates, count=True)

        return issue_states, issue_dates

    def generate_counting_process_rows(self, issue_states, issue_dates,
                                       reputations, workloads):
        """ Generates the counting process rows for the final dataset.

        Args:
            issue_states: Dict containg the states of the issue at the dates
                          of interest.
            issue_dates: Dates of interest, on which an issue changes its
                         state.
            reputations: Dictionary containing the reputation of each user and
                         how it changes over time.
            workloads: Dictionary containing the workloads of each user and
                         how it changes over time.
        Returns:
            rows: list of rows containing an issues features in couting process
        """
        rows = []

        if not issue_dates or not issue_states:
            return rows

        creation_date = issue_dates[0]
        # Two pointer approach to building a counting process dataset.
        curr_idx, nxt_idx = 0, 1
        while nxt_idx < len(issue_dates):
            curr_date, nxt_date = issue_dates[curr_idx], issue_dates[nxt_idx]
            issuekey = issue_states[curr_date]["issuekey"]
            start = (curr_date - creation_date).days
            end = (nxt_date - creation_date).days
            is_dead = issue_states[nxt_date]["is_dead"]
            priority = issue_states[curr_date]["priority"]
            assignee = issue_states[curr_date]["assignee"]
            is_assigned = issue_states[curr_date]["is_assigned"]
            issuetype = issue_states[curr_date]["issuetype"]
            has_priority_change = (
                issue_states[curr_date]["has_priority_change"])
            has_desc_change = issue_states[curr_date]["has_desc_change"]
            comment_count = issue_states[curr_date]["comment_count"]
            link_count = issue_states[curr_date]["link_count"]
            affect_count = (
                issue_states[curr_date]["affect_count"])
            fix_count = issue_states[curr_date]["fix_count"]
            has_fix_change = issue_states[curr_date]["has_fix_change"]
            if reputations:
                reporter_rep = issue_states[curr_date]["reporter_rep"]
            if workloads:
                assignee_workload = (
                    issue_states[curr_date]["assignee_workload"])
            row = {"issuekey": issuekey,
                   "start": start,
                   "end": end,
                   "is_dead": is_dead,
                   "priority": priority,
                   "issuetype": issuetype,
                   "assignee": assignee,
                   "is_assigned": is_assigned,
                   "has_priority_change": has_priority_change,
                   "has_desc_change": has_desc_change,
                   "comment_count": comment_count,
                   "link_count": link_count,
                   "affect_count": affect_count,
                   "fix_count": fix_count,
                   "has_fix_change": has_fix_change,
                   }
            if reputations:
                row["reporter_rep"] = reporter_rep
            if workloads:
                row["assignee_workload"] = assignee_workload
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
        assignee = self.get_feature("assignee", issue)
        is_assigned = self.get_feature("is_assigned", issue)
        issuetype = self.get_feature("issuetype", issue)
        desc = self.get_feature("desc", issue)
        link_count = self.get_feature("link_count", issue)
        affect_count = self.get_feature("affect_count", issue)
        fix_count = self.get_feature("fix_count", issue)

        state = {"issuekey": issuekey,
                 "is_dead": is_dead,
                 "priority": priority,
                 "assignee": assignee,
                 "is_assigned": is_assigned,
                 "issuetype": issuetype,
                 "desc": desc,
                 "link_count": link_count,
                 "affect_count": affect_count,
                 "fix_count": fix_count
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
                    self.append_state_at_feature_change(
                        "is_assigned", issue, item, date, issue_states,
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
                if item["field"] == "Version":
                    self.append_state_at_feature_change(
                        "affect_count", issue, item, date,
                        issue_states, issue_dates)
                if item["field"] == "Fix Version":
                    self.append_state_at_feature_change(
                        "fix_count", issue, item, date,
                        issue_states, issue_dates)

    def append_state_at_creation(self, issue, issue_states,
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

    def append_state_at_resolution(self, issue, issue_states, issue_dates,
                                   resolution_date):
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
            is_dead = 1
            if resolution_date in issue_dates:
                issue_states[resolution_date]["is_dead"] = is_dead
            else:
                state = self.infer_state(
                    resolution_date, issue_states, issue_dates)
                state["is_dead"] = is_dead
                bisect.insort(issue_dates, resolution_date)
                issue_states[resolution_date] = state

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

        # We do a pass on the comment log and update states on dates
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

    def add_reporter_rep_feature(self, issue, issue_states, issue_dates,
                                 reputations):
        """ Adds the cross issue features to the issue_states

        Args:
            issue: Dict that contains the issue's data
            issue_states: Dict containg the states of the issue at the dates
                          of interest
            issue_dates: Dates of interest, on which an issue changes its
                         state.
            reputations: Dictionary containing the reputation of each user and
                         how it changes over time.
        """
        reporter = issue["fields"]["creator"]["key"]
        reputation_dates = reputations[reporter]["reputation_dates"]
        reputation_timeline = reputations[reporter]["reputation_timeline"]
        creation_date = parse(issue["fields"]["created"]).date()

        # Get the starting date for the issue
        idx = bisect.bisect(reputation_dates, creation_date) - 1
        date = reputation_dates[idx]
        # Do a pass to add reputation changes
        while date <= issue_dates[-1] and idx < len(reputation_dates):
            date = reputation_dates[idx]
            reporter_rep = reputation_timeline[date]
            if date < issue_dates[0]:
                date = issue_dates[0]
            if date in issue_dates:
                issue_states[date]["reporter_rep"] = reporter_rep
            else:
                state = self.infer_state(date, issue_states, issue_dates)
                state["reporter_rep"] = reporter_rep
                bisect.insort(issue_dates, date)
                issue_states[date] = state
            idx += 1

    def add_assignee_workload_feature(self, issue, issue_states, issue_dates,
                                      workloads):
        """ Adds the assignee_workload feature to the issue states

        Args:
            issue: Dict that contains the issue's data
            issue_states: Dict containg the states of the issue at the dates
                          of interest
            issue_dates: Dates of interest, on which an issue changes its
                         state.
            workloads: Dictionary containing the workloads of each user and
                         how it changes over time.
        """
        # duplicate code
        if not issue_dates:
            return

        # get the assignees in an issues
        assignee_timelines = []
        prev_date = issue_dates[0]
        prev_assignee = issue_states[prev_date]["assignee"]
        for i in range(len(issue_dates)):
            curr_date = issue_dates[i]
            curr_assignee = issue_states[curr_date]["assignee"]
            if curr_assignee != prev_assignee:
                assignees_entry = {"assignee": prev_assignee,
                                   "assigned_date": prev_date,
                                   "unassigned_date": curr_date}
                assignee_timelines.append(assignees_entry)

                prev_date = curr_date
                prev_assignee = curr_assignee
            if issue_states[curr_date]["is_dead"]:
                break
        assignees_entry = {"assignee": prev_assignee,
                           "assigned_date": prev_date,
                           "unassigned_date": curr_date}
        assignee_timelines.append(assignees_entry)

        # add the workloads for each assignee to the issue states
        for assignee_timeline in assignee_timelines:
            assignee = assignee_timeline["assignee"]
            if assignee == "unassigned":
                continue
            workload_dates = workloads[assignee]["workload_dates"]
            workload_timeline = workloads[assignee_timeline["assignee"]
                                          ]["workload_timeline"]

            # Get the starting date for the assignee workload
            assigned_date = assignee_timeline["assigned_date"]
            unassigned_date = assignee_timeline["unassigned_date"]
            idx = bisect.bisect(workload_dates, assigned_date) - 1
            workload_date = workload_dates[idx]
            # Do a pass to add the assignee's workload
            while (workload_date <= issue_dates[-1] and
                   workload_date < unassigned_date and
                   idx < len(workload_dates)):
                workload_date = workload_dates[idx]
                assignee_workload = workload_timeline[workload_date]
                if workload_date < issue_dates[0]:
                    workload_date = issue_dates[0]
                if workload_date in issue_dates:
                    issue_states[workload_date]["assignee_workload"] = (
                        assignee_workload)
                else:
                    state = self.infer_state(
                        workload_date, issue_states, issue_dates)
                    state["assignee_workload"] = assignee_workload
                    bisect.insort(issue_dates, workload_date)
                    issue_states[workload_date] = state
                idx += 1

        # do a pass to set the workload of unassigned issues to None
        for date in issue_dates:
            if issue_states[date]["assignee"] == "unassigned":
                issue_states[date]["assignee_workload"] = None

    def level_issue_states(self, issue, issue_states, issue_dates,
                           reputations, workloads):
        """ Goes through the issue states to set the missing feature values.

        Args:
            issue: Dict that contains the issue's data.
            issue_states: Dict containg the states of the issue at the dates
                          of interest.
            reputations: Dictionary containing the reputation of each user and
                         how it changes over time.
            workloads: Dictionary containing the workloads of each user and
                         how it changes over time.
        """
        comment_count = 0
        first_date = issue_dates[0]
        if reputations:
            reporter_rep = issue_states[first_date]["reporter_rep"]
        if workloads:
            assignee_workload = issue_states[first_date]["assignee_workload"]

        for date in issue_dates:
            if issue_states[date].get("comment_count") is None:
                issue_states[date]["comment_count"] = comment_count
            else:
                comment_count = issue_states[date]["comment_count"]

            if reputations:
                if issue_states[date].get("reporter_rep") is None:
                    issue_states[date]["reporter_rep"] = reporter_rep
                else:
                    reporter_rep = issue_states[date]["reporter_rep"]

            if workloads:
                if issue_states[date].get("assignee_workload") is None:
                    issue_states[date]["assignee_workload"] = assignee_workload
                else:
                    assignee_workload = issue_states[date]["assignee_workload"]

    def add_count_features(self, issue, issue_states, issue_dates,
                           count=False):
        """ Goes through the issue states and add count features.

        Args:
            issue: Dict that contains the issue's data.
            issue_states: Dict containg the states of the issue at the dates
                          of interest.
            issue_dates: Dates of interest, on which an issue changes its
                         state.
            count: Boolean that determines whether the process features should
                   be bools or counts.
        """
        has_priority_change = 0
        has_desc_change = 0
        has_fix_change = 0
        for date in issue_dates:
            if issue_states[date].get("previous_priority") is not None:
                if count:
                    has_priority_change += 1
                else:
                    has_priority_change = 1
            if issue_states[date].get("previous_desc") is not None:
                if count:
                    has_desc_change += 1
                else:
                    has_desc_change = 1
            if issue_states[date].get("previous_fix_count") is not None:
                if count:
                    has_fix_change += 1
                else:
                    has_fix_change = 1
            issue_states[date]["has_priority_change"] = has_priority_change
            issue_states[date]["has_desc_change"] = has_desc_change
            issue_states[date]["has_fix_change"] = has_fix_change

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
                previous_assignee = "unassigned"
            else:
                previous_assignee = item["from"]
            if date in issue_dates:
                issue_states[date]["previous_assignee"] = previous_assignee
            else:
                state = self.infer_state(date, issue_states, issue_dates)
                state["previous_assignee"] = previous_assignee
                bisect.insort(issue_dates, date)
                issue_states[date] = state

        elif feature == "is_assigned":
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

        elif feature == "affect_count":
            if date in issue_dates:
                if item["from"]:
                    if issue_states[date].get("previous_affect_count"):
                        issue_states[date]["previous_affect_count"] += 1
                    else:
                        issue_states[date]["previous_affect_count"] = (
                            issue_states[date]["affect_count"] + 1)
                elif item["to"]:
                    if issue_states[date].get("previous_affect_count"):
                        issue_states[date]["previous_affect_count"] -= 1
                    else:
                        issue_states[date]["previous_affect_count"] = (
                            issue_states[date]["affect_count"] - 1)
                else:
                    logging.INFO(
                        "Issue has both 'to' and 'from' in affect feature")
            else:
                state = self.infer_state(date, issue_states, issue_dates)
                if item["from"]:
                    state["previous_affect_count"] = (
                        state["affect_count"] + 1)
                elif item["to"]:
                    state["previous_affect_count"] = (
                        state["affect_count"] - 1)
                else:
                    logging.INFO(
                        "Issue has both 'to' and 'from' in affect feature")
                bisect.insort(issue_dates, date)
                issue_states[date] = state

        elif feature == "fix_count":
            if date in issue_dates:
                if item["from"]:
                    if issue_states[date].get("previous_fix_count"):
                        issue_states[date]["previous_fix_count"] += 1
                    else:
                        issue_states[date]["previous_fix_count"] = (
                            issue_states[date]["fix_count"] + 1)
                elif item["to"]:
                    if issue_states[date].get("previous_fix_count"):
                        issue_states[date]["previous_fix_count"] -= 1
                    else:
                        issue_states[date]["previous_fix_count"] = (
                            issue_states[date]["fix_count"] - 1)
                else:
                    logging.INFO(
                        "Issue has both 'to' and 'from' in fix feature")
            else:
                state = self.infer_state(date, issue_states, issue_dates)
                if item["from"]:
                    state["previous_fix_count"] = (
                        state["fix_count"] + 1)
                elif item["to"]:
                    state["previous_fix_count"] = (
                        state["fix_count"] - 1)
                else:
                    logging.INFO(
                        "Issue has both 'to' and 'from' in fix feature")
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

        if reference_state.get("previous_assignee") is None:
            assignee = reference_state["assignee"]
        else:
            assignee = reference_state["previous_assignee"]

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

        if reference_state.get("previous_affect_count") is None:
            affect_count = reference_state["affect_count"]
        else:
            affect_count = reference_state["previous_affect_count"]

        if reference_state.get("previous_fix_count") is None:
            fix_count = reference_state["fix_count"]
        else:
            fix_count = reference_state["previous_fix_count"]

        state = {"issuekey": issuekey,
                 "is_dead": is_dead,
                 "priority": priority,
                 "assignee": assignee,
                 "is_assigned": is_assigned,
                 "issuetype": issuetype,
                 "desc": desc,
                 "link_count": link_count,
                 "affect_count": affect_count,
                 "fix_count": fix_count,
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

        elif feature == "assignee":
            if issue["fields"]["assignee"]:
                assignee = issue["fields"]["assignee"]["key"]
            else:
                assignee = "unassigned"
            return assignee

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

        elif feature == "affect_count":
            if issue["fields"].get("versions"):
                affect_count = len(issue["fields"]["versions"])
            else:
                affect_count = 0
            return affect_count

        elif feature == "fix_count":
            if issue["fields"].get("fixVersions"):
                fix_count = len(issue["fields"]["fixVersions"])
            else:
                fix_count = 0
            return fix_count

        else:
            raise ValueError()

    def get_resolution_date(self, issue):
        """ Gets the date of the first resolution of an issue

        Args:
            issue: A dict containing an issue's data
        Returns:
            resolution_date: Date containing the resolution_date
        """
        if issue["fields"]["resolutiondate"] is None:
            resolution_date = datetime.now(timezone.utc).date()
            return resolution_date
        else:
            for change in issue["changelog"]["histories"]:
                date = parse(change["created"]).date()
                for item in change["items"]:
                    if item["field"] == "resolution":
                        resolution_date = date + timedelta(days=1)
                        return resolution_date


if __name__ == "__main__":
    main()
