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


def test_train():
    vec_label = mc.get_word_vec_label()
    print len(vec_label)
    positive = mc.get_doc_feature_by_law("《中华人民共和国侵权责任法》", 6, vec_label)
    print "正集准备就绪"
    positive_features = positive['features']
    positive_doc_nos = positive['doc_nos']
    negative_features = mc.get_doc_feature_exclude_nos(positive_doc_nos, vec_label, len(positive_doc_nos))
    print "负集准备就绪"
    labels = [1 for x in range(0, len(positive_features))]
    labels.extend([0 for y in range(0, len(negative_features))])
    datas = positive_features
    datas.extend(negative_features)
    print "开始训练..."
    train_with_NB(datas, labels)


def test_result():
    pass


test_train()
