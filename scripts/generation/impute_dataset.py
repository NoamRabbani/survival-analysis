"""
This script contains the functionality impute missing values in the
dataset

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
import numpy as np
from dateutil.parser import parse
from copy import deepcopy
from datetime import datetime, timezone


def main():
    dataset_input_path = "./dataset/hbase_features_filtered.csv"
    dataset_output_path = "./dataset/hbase_features_imputed.csv"

    imp = Imputer()
    df = pd.read_csv(dataset_input_path, sep='\t')
    df = imp.impute_df(df, column="assignee_workload", value=8)

    df.to_csv(dataset_output_path, sep='\t', index=False)


class Imputer:
    """ Handles imputation of missing values in the dataset.
    """

    def impute_df(self, df, column, value):
        """ Imputes missing values using the median

        Args:
            df: Dataframe issues as rows and features as columns
            column: Column to be imputed
            value: Value to use for imputation
        Returns:
            df: Imputed dataframe.
        """

        df[column] = df[column].fillna(value)

        return df


if __name__ == '__main__':
    main()
