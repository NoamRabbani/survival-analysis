import pytest
import os
import pandas as pd

current_dir = os.path.dirname(__file__)
input_paths = {"under_test": os.path.join(current_dir, "..", "dataset", "hbase_features_raw.csv"),  # noqa
               "within_issue": os.path.join(current_dir, "within_issue_dataset.csv"),  # noqa
               "cross_issue": os.path.join(current_dir, "cross_issue_dataset.csv")}  # noqa


def test_within_issue_features():
    dataset_under_test = pd.read_csv(input_paths["under_test"], sep='\t')
    reference_dataset = pd.read_csv(input_paths["within_issue"], sep='\t')
    features = ["issuekey", "start_date", "is_dead", "priority", "issuetype",
                "assignee", "is_assigned", "comment_count", "link_count",
                "affect_count", "fix_count", "has_priority_change",
                "has_desc_change", "has_fix_change"]

    common_rows = pd.merge(dataset_under_test, reference_dataset,
                           on=features, how='inner')

    assert common_rows.shape[0] == reference_dataset.shape[0]


def test_cross_issue_features():
    dataset_under_test = pd.read_csv(input_paths["under_test"], sep='\t')
    reference_dataset = pd.read_csv(input_paths["cross_issue"], sep='\t')
    features = ["issuekey", "start_date", "reporter_rep", "assignee_workload"]

    common_rows = pd.merge(dataset_under_test, reference_dataset,
                           on=features, how='inner')

    assert common_rows.shape[0] == reference_dataset.shape[0]
