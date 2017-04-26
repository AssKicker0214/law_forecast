# coding=utf-8
import sys

sys.path.append("..")
from mongodb_connector import TrainResult


def make_up_train_result_collection():
    result_obj = TrainResult()
    result_obj.import_data_from_file("test_result_optimized.txt")


make_up_train_result_collection()
