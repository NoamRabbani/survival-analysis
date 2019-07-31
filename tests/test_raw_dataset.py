import pytest
import os
import pandas as pd

current_dir = os.path.dirname(__file__)
projects = ["hbase", "hadoop"]
input_paths = {"under_test": os.path.join(current_dir, "..", "dataset", "hbase_features_raw.csv"),  # noqa
               "within_issue": os.path.join(current_dir, "within_issue_dataset.csv"),  # noqa
               "cross_issue": os.path.join(current_dir, "cross_issue_dataset.csv")}  # noqa


@pytest.fixture()
def load_datasets():

    def load(project, cross_issue):
        dir_path = os.path.dirname(__file__)

        filename = "{}_features_raw.csv".format(project)
        path = os.path.join(dir_path, "..", "dataset", project,
                            filename)
        dataset_under_test = pd.read_csv(path, sep='\t')

        if cross_issue:
            path = os.path.join(dir_path, "reference_data", project,
                                "cross_issue_dataset.csv")
            reference_dataset = pd.read_csv(path, sep='\t')
        else:
            path = os.path.join(dir_path, "reference_data", project,
                                "within_issue_dataset.csv")
            reference_dataset = pd.read_csv(path, sep='\t')

        return dataset_under_test, reference_dataset

    return load


def test_hbase_within_issue_features(load_datasets):
    dataset_under_test, reference_dataset = load_datasets(
        "hbase", cross_issue=False)
    features = ["issuekey", "start_date", "is_dead", "priority", "issuetype",
                "assignee", "is_assigned", "comment_count", "link_count",
                "affect_count", "fix_count", "has_priority_change",
                "has_desc_change", "has_fix_change"]

    common_rows = pd.merge(dataset_under_test, reference_dataset,
                           on=features, how='inner')

    assert common_rows.shape[0] == reference_dataset.shape[0]


def test_hadoop_within_issue_features(load_datasets):
    dataset_under_test, reference_dataset = load_datasets(
        "hadoop", cross_issue=False)
    features = ["issuekey", "start_date", "is_dead", "priority", "issuetype",
                "assignee", "is_assigned", "comment_count", "link_count",
                "affect_count", "fix_count", "has_priority_change",
                "has_desc_change", "has_fix_change"]

    common_rows = pd.merge(dataset_under_test, reference_dataset,
                           on=features, how='inner')

    assert common_rows.shape[0] == reference_dataset.shape[0]


def test_hbase_cross_issue_features(load_datasets):
    dataset_under_test, reference_dataset = load_datasets(
        "hbase", cross_issue=True)
    features = ["issuekey", "start_date", "reporter_rep", "assignee_workload"]

    common_rows = pd.merge(dataset_under_test, reference_dataset,
                           on=features, how='inner')

    assert common_rows.shape[0] == reference_dataset.shape[0]
