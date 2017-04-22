# coding=utf-8
import os
import re

from sklearn.externals import joblib
from tool.mysort import sort
import xml_reader as xml
import jieba.analyse as ana
from mongodb_connector import DocFeature
from mongodb_connector import get_relevant_law


def predict(doc_no, model_dir="../data/model/"):
    doc_path = get_doc_path(doc_no)
    AJJBQK = xml.getAJJBQK(doc_path)
    doc_feature = DocFeature(False)
    vec_label = doc_feature.get_word_vec_label()
    vec = doc_feature.text_to_vec(get_tf_idfs(AJJBQK), vec_label)
    model_list = os.listdir(model_dir)
    cnt = 0
    i = 0
    predicted_law = []
    predicted_reliability = []
    for model_file in model_list:
        # law = model_file.decode(encoding='gbk').encode()
        splited = split_model_name(model_file)
        if not splited:
            print "名称不合法->", model_file.decode(encoding='gbk').encode()
            continue
        law = splited['name'] + "-" + str(splited["no"])
        reliability = get_reliability(splited["accuracy"], splited["rate"])
        if reliability == 0:
            continue
        cnt += 1

        gnb = joblib.load(model_dir + model_file)  # .decode().encode(encoding="gbk"))
        result = gnb.predict([vec])

        # #################使用中间结果###################
        # result = gnb._joint_log_likelihood([vec])
        # print result
        # ########################################
        if result[0] == 1:
            i += 1
            predicted_law.append(law)
            predicted_reliability.append(reliability)
            # print law, str(i) + "/" + str(cnt)
    sorted_pre = sort(predicted_law, predicted_reliability)
    print "# 使用有效模型", cnt
    return sorted_pre


def split_model_name(model_name):
    pattern_str = '(.+)-#(\d+)-A(.+)-R([\.\d]+).m'
    pattern = re.compile(pattern_str)
    m = re.search(pattern, model_name)
    splited = {}
    if m:
        splited['name'] = m.group(1)
        splited['no'] = m.group(2)
        try:
            splited['accuracy'] = float(m.group(3))
        except ValueError:
            splited['accuracy'] = 0
        splited['rate'] = float(m.group(4))
    return splited


def get_reliability(accuracy, rate):
    if accuracy < 0.7:
        return 0
    if rate < 1:
        return 0
    return accuracy * rate


def get_doc_path(doc_no):
    return "../data/test_sets/MinShi1/test/" + str(doc_no) + ".xml"


def get_tf_idfs(text):
    tags = ana.extract_tags(text, topK=100, withWeight=True, allowPOS=('n', 'v'))
    return tags


def test(doc_no):
    predicted = predict(doc_no)
    laws = get_relevant_law(doc_no)
    predicted_laws = predicted['labels']
    predicted_reliability = predicted['values']
    hit = 0
    for law in laws:
        for i in range(0, len(predicted_laws)):
            plaw = predicted_laws[i].decode(encoding='gbk')
            # print law
            if unicode(law[u"名称"]+"-"+str(law[u"条号"])) == plaw:
                hit += 1
                print plaw, "可信度:", predicted_reliability[i]
    print "======", "预测", "======"
    index = 0
    for i in range(0, len(predicted_reliability)):
        label = predicted["labels"][i]
        value = predicted["values"][i]
        if value > 0:
            index += 1
            print str(index) + ": " + label.decode(encoding='gbk').encode(), value
    print "======", "实际", "======"
    for law in laws:
        print law[u"名称"], "#"+str(law[u"条号"])

    print "hit: ", hit, "miss:", len(laws)-hit, "of", str(len(predicted_laws))

test(10153)
