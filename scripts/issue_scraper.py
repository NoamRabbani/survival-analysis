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


def main():
    output_dir = './issues_hbase/'
    sc = IssueScraper()

    years = [2017, 2018, 2019]
    projects = ["HBASE"]
    # sc.scrape_issues(projects, years, output_dir)
    sc.scrape_issue_comments(output_dir)


class IssueScraper:

    def scrape_issues(self, projects, years, output_dir):
        """ Scrapes issues given a project and year range

        Scrapes issues project and saves them as individual JSON files.

        Args:
            projects: Apache projects to scrape
            years: List of years in which the issues were opened in
            output_dir: Directory where issues get saved as JSON files
        """
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        for p in projects:
            for y in years:
                print("Collecting year {}".format(y))
                start_at = 0
                while True:
                    print("Scraping issues {}-{}"
                          .format(start_at, start_at+1000))
                    url = (
                        'https://issues.apache.org/jira/rest/api/2/search?jql=' +  # noqa
                        'project={}&created%20%3E%3D%20{}-01-01%20AND%20created%20%3C%3D%20{}-12-31&maxResults=-1&startAt={}&expand=changelog'  # noqa
                        .format(p, y, y, start_at)
                    )
                    json_data = self.http_get_request(url)

                    if len(json_data['issues']) == 0:
                        break

                    for issue in json_data['issues']:
                        file_path = output_dir + issue['key']
                        if not os.path.exists(file_path):
                            with open(file_path, 'w') as f:
                                json.dump(issue, f)
                        else:
                            print(file_path + ' already exists')
                    start_at += 1000

    def scrape_issue_comments(self, issues_dir):
        """ Scrapes and appends comments for each issue in issues_dir

        JIRA does not support scraping the comments of an issue along all its
        other fields. Rather, each comment log has to  be scraped individually
        with a GET request. The comments are then appended to each issue's JSON
        file.

        Args:
            issues_dir: Directory that contains JSON issues
        """
        missing_issues = []
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
            comment_json_data = self.http_get_request(url)

            try:
                issue_json_data['comments'] = comment_json_data['comments']
            except:
                missing_issues.append(filename)
                print("Could not scrape comments for {}".format(filename))

            with open(path, 'w') as f:
                json.dump(issue_json_data, f)

        with open('missing_issues', 'w') as f:
            json.dump(missing_issues, f)

    def http_get_request(self, url):
        """ Makes and htttp GET request
        Args:
            url: url to send the get request to
        Returns:
            json_data: data returned from the GET request in JSON format
        """
        json_data = requests.get(
            url, headers={'Content-Type': 'application/json'}
        ).json()
        return json_data


if __name__ == '__main__':
    main()
