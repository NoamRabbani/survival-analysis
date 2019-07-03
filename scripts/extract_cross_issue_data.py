"""
Extract data that span multiple issues such as reporter_reputation
and assignee_workload

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

import os
import json
import datetime
import pickle
from dateutil.parser import parse
import bisect
import generate_counting_process_dataset
from copy import deepcopy


def main():

    input_paths = {"issues": "./issues_hbase/"}
    output_paths = {"reputations": "./cross_issue_data/reputation_timelines.pickle",  # noqa
                   "workloads": "./cross_issue_data/workload_timelines.pickle"}  # noqa

    cidp = CrossIssueDataProcessor()
    reputations = cidp.generate_reporter_reputations(input_paths, output_paths)
    workloads = cidp.generate_assignee_workloads(
        input_paths, output_paths, reputations)


class CrossIssueDataProcessor():
    """ Parses JSON issues to extract cross-issue data.
    """

    def generate_reporter_reputations(self, input_paths, output_paths):

        open_issues_timelines = {}
        close_issues_timelines = {}
        reputation_timelines = {}

        worklogs = self.generate_reporter_worklogs(input_paths)
        for reporter, worklog in worklogs.items():
            open_dates, issues_opened_on, open_issues_timeline = (
                self.extract_opened_issues(reporter, worklog))
            timeline_entry = {"open_dates": open_dates,
                              "issues_opened_on": issues_opened_on,
                              "open_issues_timeline": open_issues_timeline}
            open_issues_timelines[reporter] = timeline_entry

            close_dates, issues_closed_on, close_issues_timeline = (
                self.extract_closed_issues(reporter, worklog))
            timeline_entry = {"close_dates": close_dates,
                              "issues_closed_on": issues_closed_on,
                              "close_issues_timeline": close_issues_timeline}
            close_issues_timelines[reporter] = timeline_entry

            reputation_timeline = {}
            reputation_dates = []
            for date in open_dates:
                if reputation_timeline.get(date) is None:
                    bisect.insort(reputation_dates, date)
                    reputation_timeline[date] = -1
            for date in close_dates:
                if reputation_timeline.get(date) is None:
                    bisect.insort(reputation_dates, date)
                    reputation_timeline[date] = -1

            opened = 0
            fixed = 0
            for date in reputation_dates:
                if open_issues_timeline.get(date):
                    opened = open_issues_timeline[date]
                if close_issues_timeline.get(date):
                    fixed = close_issues_timeline[date]
                reputation_timeline[date] = (fixed / (opened + 1))
            timeline_entry = {"reputation_dates": reputation_dates,
                              "reputation_timeline": reputation_timeline}
            reputation_timelines[reporter] = timeline_entry

        with open(output_paths["reputations"], 'wb') as fp:
            pickle.dump(reputation_timelines, fp)

        output_path = "./cross_issue_data/open_issues_timelines.json"
        self.save_dict_as_json(output_path, open_issues_timelines)

        output_path = "./cross_issue_data/close_issues_timelines.json"
        self.save_dict_as_json(output_path, close_issues_timelines)

        output_path = "./cross_issue_data/reputation_timelines.json"
        self.save_dict_as_json(output_path, reputation_timelines)

        return reputation_timelines

    def generate_assignee_workloads(self, input_paths, output_paths,
                                    reputations):
        assigned_issues_timelines = {}
        unassigned_issues_timelines = {}
        workload_timelines = {}

        worklogs = self.generate_assignee_worklogs(input_paths, reputations)
        for assignee, worklog in worklogs.items():
            assigned_dates, issues_assigned_on, assigned_issues_timeline = (
                self.extract_assigned_issues(assignee, worklog))
            timeline_entry = {"assigned_dates": assigned_dates,
                              "issues_assigned_on": issues_assigned_on,
                              "assigned_issues_timeline": assigned_issues_timeline}  # noqa
            assigned_issues_timelines[assignee] = timeline_entry

            unassigned_dates, issues_unassigned_on, unassigned_issues_timeline = (  # noqa
                self.extract_unassigned_issues(assignee, worklog))
            timeline_entry = {"unassigned_dates": unassigned_dates,
                              "issues_unassigned_on": issues_unassigned_on,
                              "unassigned_issues_timeline": unassigned_issues_timeline}  # noqa
            unassigned_issues_timelines[assignee] = timeline_entry

            workload_timeline = {}
            workload_dates = []
            for date in assigned_dates:
                if workload_timeline.get(date) is None:
                    bisect.insort(workload_dates, date)
                    workload_timeline[date] = -1
            for date in unassigned_dates:
                if workload_timeline.get(date) is None:
                    bisect.insort(workload_dates, date)
                    workload_timeline[date] = -1

            assigned = 0
            unassigned = 0
            for date in workload_dates:
                if assigned_issues_timeline.get(date):
                    assigned = assigned_issues_timeline[date]
                if unassigned_issues_timeline.get(date):
                    unassigned = unassigned_issues_timeline[date]
                workload_timeline[date] = assigned - unassigned
            timeline_entry = {"workload_dates": workload_dates,
                              "workload_timeline": workload_timeline}
            workload_timelines[assignee] = timeline_entry

        with open(output_paths["workloads"], 'wb') as fp:
            pickle.dump(workload_timelines, fp)

        output_path = "./cross_issue_data/assigned_issues_timelines.json"
        self.save_dict_as_json(output_path, assigned_issues_timelines)

        output_path = "./cross_issue_data/unassigned_issues_timelines.json"
        self.save_dict_as_json(output_path, unassigned_issues_timelines)

        output_path = "./cross_issue_data/workloads_timelines.json"
        self.save_dict_as_json(output_path, workload_timelines)

        return workload_timelines

    # TODO: merge the two functions below
    def extract_closed_issues(self, reporter, worklog):
        dates = []
        issues_closed_on = {}
        for issue in worklog:
            if issue["resolution_date"]:
                date = issue["resolution_date"]
            else:
                continue
            if issues_closed_on.get(date):
                issues_closed_on[date] += 1
            else:
                issues_closed_on[date] = 1
                bisect.insort(dates, date)

        close_issues_timeline = {}
        cumulative_close_issues = 0
        for date in dates:
            cumulative_close_issues += issues_closed_on[date]
            close_issues_timeline[date] = cumulative_close_issues
        return dates, issues_closed_on, close_issues_timeline

    def extract_unassigned_issues(self, assignee, worklog):
        dates = []
        issues_unassigned_on = {}
        for issue in worklog:
            if issue["unassigned_date"]:
                date = issue["unassigned_date"]
            else:
                continue
            if issues_unassigned_on.get(date):
                issues_unassigned_on[date] += 1
            else:
                issues_unassigned_on[date] = 1
                bisect.insort(dates, date)

        unassigned_issues_timeline = {}
        cumulative_unassigned_issues = 0
        for date in dates:
            cumulative_unassigned_issues += issues_unassigned_on[date]
            unassigned_issues_timeline[date] = cumulative_unassigned_issues
        return dates, issues_unassigned_on, unassigned_issues_timeline

    def extract_opened_issues(self, reporter, worklog):
        dates = []
        issues_opened_on = {}
        for issue in worklog:
            date = issue["creation_date"]
            if issues_opened_on.get(date):
                issues_opened_on[date] += 1
            else:
                issues_opened_on[date] = 1
                bisect.insort(dates, date)

        open_issues_timeline = {}
        cumulative_open_issues = 0
        for date in dates:
            cumulative_open_issues += issues_opened_on[date]
            open_issues_timeline[date] = cumulative_open_issues
        return dates, issues_opened_on, open_issues_timeline

    def extract_assigned_issues(self, reporter, worklog):
        dates = []
        issues_assigned_on = {}
        for issue in worklog:
            date = issue["assigned_date"]
            if issues_assigned_on.get(date):
                issues_assigned_on[date] += 1
            else:
                issues_assigned_on[date] = 1
                bisect.insort(dates, date)

        assigned_issues_timeline = {}
        cumulative_assigned_issues = 0
        for date in dates:
            cumulative_assigned_issues += issues_assigned_on[date]
            assigned_issues_timeline[date] = cumulative_assigned_issues
        return dates, issues_assigned_on, assigned_issues_timeline

    def generate_reporter_worklogs(self, input_paths, output_path=None):
        worklogs = {}
        for filename in os.listdir(input_paths["issues"]):
            issue_path = os.path.join(input_paths["issues"], filename)
            with open(issue_path, "r") as f:
                issue = json.load(f)

            reporter = issue["fields"]["creator"]["key"]
            issue_key = issue["key"]
            creation_date = parse(issue["fields"]["created"]).date()
            # TODO: Maybe this should be the first resolution occurence
            if issue["fields"]["resolutiondate"] is None:
                resolution_date = None
            else:
                resolution_date = parse(
                    issue["fields"]["resolutiondate"]).date()

            worklog_entry = {"issuekey": issue_key,
                             "creation_date": creation_date,
                             "resolution_date": resolution_date}
            worklogs[reporter] = worklogs.get(reporter, [])
            worklogs[reporter].append(worklog_entry)

        output_path = "./cross_issue_data/reporter_worklogs.json"
        self.save_dict_as_json(output_path, worklogs)

        return worklogs

    def generate_assignee_worklogs(self, input_paths, reputations):
        worklogs = {}
        cp = generate_counting_process_dataset.CountingProcess()
        for filename in os.listdir(input_paths["issues"]):
            issue_path = os.path.join(input_paths["issues"], filename)
            with open(issue_path, "r") as f:
                issue = json.load(f)
            issue_dates, issue_states = cp.generate_issue_states(
                issue_path, input_paths, reputations)

            if not issue_dates:
                continue

            issue_key = issue["key"]
            prev_date = issue_dates[0]
            prev_assignee = issue_states[prev_date]["assignee"]
            for i in range(len(issue_dates)):
                curr_date = issue_dates[i]
                curr_assignee = issue_states[curr_date]["assignee"]
                if curr_assignee != prev_assignee:
                    worklog_entry = {"issuekey": issue_key,
                                     "assigned_date": prev_date,
                                     "unassigned_date": curr_date}
                    worklogs[prev_assignee] = worklogs.get(prev_assignee, [])
                    worklogs[prev_assignee].append(worklog_entry)

                    prev_date = curr_date
                    prev_assignee = curr_assignee
                if issue_states[curr_date]["is_dead"]:
                    break
            worklog_entry = {"issuekey": issue_key,
                             "assigned_date": prev_date,
                             "unassigned_date": curr_date}
            worklogs[prev_assignee] = worklogs.get(prev_assignee, [])
            worklogs[prev_assignee].append(worklog_entry)

        output_path = "./cross_issue_data/assignee_worklogs.json"
        self.save_dict_as_json(output_path, worklogs)

        return worklogs

    def save_dict_as_json(self, path, d):
        dict_copy = deepcopy(d)
        self.dictRecursiveFormat(dict_copy)
        with open(path, 'w') as fp:
            json.dump(dict_copy, fp)

    def dictRecursiveFormat(self, d):
        if type(d) is list:
            for item in d:
                item = str(item)
        elif type(d) is dict:
            for key, val in list(d.items()):
                if isinstance(key, datetime.date):
                    val = d.pop(key)
                    d[str(key)] = val
                if (isinstance(val, datetime.date) and
                        isinstance(key, datetime.date)):
                    d[str(key)] = str(val)
                elif isinstance(val, datetime.date):
                    d[key] = str(val)
                if type(val) is list:
                    for item in val:
                        if isinstance(item, datetime.date):
                            d[key] = list(map(str, val))
                            break
                        else:
                            self.dictRecursiveFormat(item)
                if type(val) is dict:
                    self.dictRecursiveFormat(val)


if __name__ == '__main__':
    main()
