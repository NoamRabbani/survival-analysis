"""
This script scrapes issues from Apache's JIRA

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

import requests
import json
import os
import pandas
import time
import sys


def main():

    if len(sys.argv) < 2:
        print("Must specify project as argument")
        exit()

    project = sys.argv[1]

    sc = IssueScraper()

    years = list(range(2003, 2020))
    # sc.scrape_issues(project, years)
    sc.scrape_issue_comments(project)


class IssueScraper:

    def scrape_issues(self, project, years):
        """ Scrapes issues given a project and year range

        Scrapes issues project and saves them as individual JSON files.

        Args:
            project: Name of project to scrape
            years: List of years in which the issues were opened in
        """
        module_path = os.path.dirname(os.path.realpath(__file__))
        output_dir = os.path.join(module_path, "..", "..", "issues", project)

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for y in years:
            print("Collecting year {}".format(y))
            start_at = 0
            while True:
                print("Scraping issues {}-{}"
                      .format(start_at, start_at+1000))
                #
                url = (
                    'https://issues.apache.org/jira/rest/api/2/search?jql=' +  # noqa
                    'project={} and created >= "{}/01/01" and created <= "{}/12/31"&maxResults=-1&startAt={}&expand=changelog'  # noqa
                    .format(project, y, y, start_at)
                )
                json_data = self.http_get_request(url, delay=30)

                if len(json_data['issues']) == 0:
                    break

                for issue in json_data['issues']:
                    file_path = os.path.join(output_dir, issue['key'])
                    if not os.path.exists(file_path):
                        with open(file_path, 'w') as f:
                            json.dump(issue, f)
                    else:
                        print(file_path + ' already exists')
                start_at += 1000

    def scrape_issue_comments(self, project):
        """ Scrapes and appends comments for each issue in issues_dir

        JIRA does not support scraping the comments of an issue along all its
        other fields. Rather, each comment log has to  be scraped individually
        with a GET request. The comments are then appended to each issue's JSON
        file.

        Args:
            project: Name of project to scrape
        """
        module_path = os.path.dirname(os.path.realpath(__file__))
        issues_dir = os.path.join(module_path, "..", "..", "issues", project)

        issues_with_broken_comments = []
        for filename in os.listdir(issues_dir):
            path = os.path.join(issues_dir, filename)

            with open(path, "r") as f:
                issue_json_data = json.load(f)

            if issue_json_data.get('comments'):
                print("Already scraped {}".format(filename))
                continue

            url = (
                'https://issues.apache.org/jira/rest/api/2/issue/' +
                filename +
                '/comment'
            )
            print("Scraping {}".format(filename))
            comment_json_data = self.http_get_request(url, delay=0)

            try:
                issue_json_data['comments'] = comment_json_data['comments']
            except:
                issues_with_broken_comments.append(filename)
                print("Could not scrape comments for {}".format(filename))

            with open(path, 'w') as f:
                json.dump(issue_json_data, f)

        comment_log_path = os.path.join(
            module_path, "..", "..", "logs", project,
            "issues_with_broken_comments.csv")
        with open(path, 'w') as f:
            json.dump(issues_with_broken_comments, f)

    def http_get_request(self, url, delay):
        """ Makes and htttp GET request
        Args:
            url: url to send the get request to
            delay: time to sleep after performing an http request
        Returns:
            json_data: data returned from the GET request in JSON format
        """
        json_data = requests.get(
            url, headers={'Content-Type': 'application/json'}
        ).json()
        time.sleep(delay)
        return json_data


if __name__ == '__main__':
    main()
