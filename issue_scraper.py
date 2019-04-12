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
    sc = IssueScraper()
    sc.scrape_issues_created_in_2018()


class IssueScraper:

    def scrape_issues_created_in_2018(self):
        """ Scrapes the issues that were opened in 2018

            Scrapes all issues opened in 2018 in the Apache project and
            saves them as individual JSON files
        """
        output_dir = './issues/'
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        start_at = 0
        while True:
            print(start_at)
            url = (
                'https://issues.apache.org/jira/rest/api/2/search?jql=' +
                'created%20%3E%3D%202018-01-01%20AND%20created%20%3C%3D%202018-12-31&maxResults=-1&startAt={}'  # noqa
                .format(start_at)
            )
            json_data = self.http_get_request(url)

            if len(json_data['issues']) == 0:
                break

            for issue in json_data['issues']:
                file_path = output_dir + issue['key']
                if not os.path.exists(file_path):
                    with open(file_path, 'w') as f:
                        json.dump(issue, f)
                    print(file_path + ' added')
                else:
                    print(file_path + ' already exists')
            start_at += 1000

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
