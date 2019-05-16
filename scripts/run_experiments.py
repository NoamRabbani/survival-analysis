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

import pandas as pd


def main():
    exp = Experiments()

    df = pd.read_csv("./dataset/apache_features_filtered.csv", delimiter='\t')
    print(df.head())

    exp.print_mode(df, ['priority', 'issuetype'])


class Experiments:
    """ Handles experiments for research on survival analysis
    """

    def print_mode(self, df, columns):
        print("Mode of {}".format(columns))
        print(df.loc[:, columns].mode())


if __name__ == '__main__':
    main()
