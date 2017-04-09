# coding=utf-8
import sys
from sklearn.naive_bayes import GaussianNB
from sklearn.externals import joblib
sys.path.append("..")
import mongodb_connector as mc

def train_with_NB(datas, labels):
    gnb = GaussianNB()
    gnb.fit(datas, labels)
    joblib.dump(gnb, "../../data/nb.m")
