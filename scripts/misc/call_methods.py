"""
Calls methods from other classes to test functionality. For example,
we can generate the issue_states of a single issue here.

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

import pickle
import sys
import os
sys.path.insert(0, "./scripts/generation/")
import generate_dataset  # noqa


def main():
    cp = generate_dataset.CountingProcess()
    project = "hadoop"
    input_paths, output_paths = cp.generate_file_paths(project)
    c = Caller()
    c.call_generate_issue_states(input_paths, "HADOOP-1")


class Caller:

    def call_generate_issue_states(self, input_paths, issuekey):
        cp = generate_dataset.CountingProcess()
        with open(input_paths["reputations"], 'rb') as fp:
            reputations = pickle.load(fp)
        with open(input_paths["workloads"], 'rb') as fp:
            workloads = pickle.load(fp)
        first_resolution = False
        increment_resolution_date = True
        issue_path = os.path.join(input_paths["issues"], issuekey)
        issue_states, issue_dates = cp.generate_issue_states(
            issue_path, first_resolution, increment_resolution_date,
            reputations, workloads)
        pass


if __name__ == "__main__":
    main()
