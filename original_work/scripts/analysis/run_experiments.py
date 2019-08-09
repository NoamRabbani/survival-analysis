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

    df = pd.read_csv("./dataset/hbase_features_survsplit.csv", delimiter='\t')

    exp.print_mode(df, ['priority', 'issuetype'])
    exp.print_median_resolution_time(df)

    describe = df.describe()
    describe.to_csv("./scripts/analysis/describe.csv", sep="\t")


class Experiments:
    """ Handles experiments for research on survival analysis
    """

    def print_mode(self, df, columns):
        print("Mode of {}".format(columns))
        print(df.loc[:, columns].mode())

    def print_median_resolution_time(self, df):
        resolution_rows = df.loc[df["is_dead"] == 1]
        median = resolution_rows.loc[:, "end"].median()
        print("Median resolution time: {}".format(median))


if __name__ == '__main__':
    main()
