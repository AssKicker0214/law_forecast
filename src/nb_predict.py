# coding=utf-8
import json
import os
import re
import test_matcher as cos_pre
from sklearn.externals import joblib
from tool.mysort import sort
import xml_reader as xml
import jieba.analyse as ana
from mongodb_connector import DocFeature
from mongodb_connector import TrainResult
from mongodb_connector import get_relevant_law


def predict(doc_no, model_dir="../data/model/", vec=None):
    doc_path = get_doc_path(doc_no)
    if vec is None:
        AJJBQK = xml.getAJJBQK(doc_path)
        doc_feature = DocFeature(False)
        vec_label = doc_feature.get_word_vec_label()
        vec = doc_feature.text_to_vec(get_tf_idfs(AJJBQK), vec_label)
    model_list = os.listdir(model_dir)
    # print json.dumps(vec_label, encoding='utf-8', ensure_ascii=False)
    # print vec
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
        # reliability = get_reliability(splited["accuracy"], splited["rate"])
        # if reliability == 0:
        #     continue
        cnt += 1
        model_path = model_dir + model_file#.decode(encoding='gbk').encode(encoding='utf-8')
        # print model_path
        gnb = joblib.load(model_path)
        result = gnb.predict([vec])
        # print result
        # #################使用中间结果###################
        # result = gnb._joint_log_likelihood([vec])
        # print result
        # ########################################
        if result[0] == 1:
            i += 1
            predicted_law.append(law)
            predicted_reliability.append(1)
    sorted_pre = sort(predicted_law, predicted_reliability)
    print "# 使用有效模型", cnt
    return sorted_pre


def split_model_name(model_name):
    # pattern_str = '(.+)-#(\d+)-A(.+)-R([\.\d]+).*.m'
    pattern_str = '(.+)-#*(\d+).*.m'
    pattern = re.compile(pattern_str)
    m = re.search(pattern, model_name)
    splited = {}
    if m:
        splited['name'] = m.group(1)
        splited['no'] = m.group(2)
        # try:
        #     splited['accuracy'] = float(m.group(3))
        # except ValueError:
        #     splited['accuracy'] = 0
        # splited['rate'] = float(m.group(4))
    return splited


def get_reliability(accuracy, rate):
    # if accuracy < 0.7:
    #     return 0
    # if rate < 1:
    #     return 0
    return accuracy * 100


def get_doc_path(doc_no):
    return "../data/test_sets/MinShi1/test/" + str(doc_no) + ".xml"


def get_tf_idfs(text):
    tags = ana.extract_tags(text, topK=100, withWeight=True, allowPOS=('n', 'v'))
    # print tags
    return tags


def test(doc_no, vec=None):
    print "测试：", doc_no
    # predicted = predict(doc_no, model_dir="../data/new_model/", vec=vec)
    predicted = cos_pre.cos_predict(doc_no)
    laws = get_relevant_law(doc_no)
    predicted_laws = predicted['labels']
    predicted_reliability = predicted['values']
    hit = 0
    print "======", "预测", "======"
    index = 0
    sort(predicted["labels"], predicted["values"])
    pred_array = []
    for i in range(0, len(predicted_reliability)):
        label = predicted["labels"][i]
        value = predicted["values"][i]
        if value > 0:
            index += 1
            try:
                pred_array.append(label.decode('gbk'))
                print str(index) + ": " + label.decode(encoding='gbk').encode(), "【", value, "】"
            except UnicodeDecodeError:
                pred_array.append(label)
                # print str(index) + ": " + label.encode(), "【", value, "】"


    models = TrainResult().get_results()
    model_array = []
    law_array = []
    for model in models:
        model_array.append(unicode(model[u"名称"]+"-"+str(model[u"条号"])))
    for law in laws:
        law_array.append(unicode(law[u"名称"]+"-"+str(law[u"条号"])))
    model_set = set(model_array)
    # print json.dumps(model_array, encoding='utf-8', ensure_ascii=False)
    # print json.dumps(law_array, encoding='utf-8', ensure_ascii=False)
    # print json.dumps(pred_array, encoding='utf-8', ensure_ascii=False)
    law_set = set(law_array)
    pred_set = set(pred_array)
    hits = law_set.intersection(pred_set)
    ins = model_set.intersection(law_set)
    miss = ins.difference(hits)
    outs = law_set.difference(model_set)
    print "======", "命中:", len(hits), "======"
    print json.dumps(list(hits), encoding='utf-8', ensure_ascii=False, indent=1)
    print "======", "遗漏:", len(miss), "======"
    print json.dumps(list(miss), encoding='utf-8', ensure_ascii=False, indent=1)

    print "======", "实际", "======"
    for law in laws:
        print law[u"名称"], "#"+str(law[u"条号"])
    print "hit: ", len(hits), "miss:", len(laws)-len(hits), "of", str(len(predicted_laws))
    hit_rate = 0.0
    if len(pred_set)>0:
        hit_rate = (0.0+len(hits))/len(pred_set)
    return {"hits": hits, "hit_rate": hit_rate}


def positive_precision(law_name, law_no):
    testDB = DocFeature(False)
    vec_label = testDB.get_word_vec_label()
    rs = testDB.get_doc_feature_by_law(law_name, law_no, vec_label)
    doc_nos = rs["doc_nos"]
    doc_features = rs["features"]
    law = law_name+"-"+str(law_no)
    contains = 0
    total = len(doc_nos)
    for i in range(0, total):
        hits = test(doc_nos[i], vec=doc_features[i])["hits"]
        for hit in hits:
            if hit == law:
                contains += 1
                print "contain"
    print contains, total
    return contains/(total+0.0)


def append_precision():
    rsDB = TrainResult()
    results = rsDB.get_results_without_precision()
    for result in results:
        precision = positive_precision(result[u"名称"], result[u"条号"])
        rsDB.update_attr(result[u"名称"], result[u"条号"], {"精确度": precision})


def random_test(number=10):
    testDB = DocFeature(False)
    vec_label = testDB.get_word_vec_label()
    doc_nos = testDB.get_doc_no_randomly(number)
    cnt = 0
    hr = 0.0
    for doc_no in doc_nos:
        hit_rate = test(doc_no)["hit_rate"]
        cnt += 1
        hr += hit_rate
    print hr/cnt

# 1015082 1016766 1015698 1015992 1016116
random_test(300)
# positive_precision("《中华人民共和国担保法》", 19)
# test(1242300)
# models = [{"名称": "1", "条号":1}, {"名称":2, "条号":2}]
# laws = [{"名称": "3", "条号":3}, {"名称":2, "条号":2}]
# models = [1, 2]
# laws = [2, 3]
# set1 = set(models)
# set2 = set(laws)
# print set1.union(set2)