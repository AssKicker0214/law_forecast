# coding=utf-8
import sys
import time

from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.naive_bayes import GaussianNB
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score
from sklearn import svm

sys.path.append("..")
import tool.alarm as alm
from mongodb_connector import DocFeature
import mongodb_connector as db_connector

reload(sys)
sys.setdefaultencoding('utf-8')


def train_with_NB(datas, labels, file_name, dir_name=u"../../data/model/"):
    gnb = GaussianNB()
    gnb.fit(datas, labels)
    path = dir_name + str(file_name) + u".m"
    joblib.dump(gnb, path)


def train_with_svm(datas, labels, file_name, dir_name=u"../../data/svm_model"):
    clf = svm.SVC()
    clf.fit(datas, labels)
    path = dir_name + str(file_name) + u".m"
    joblib.dump(clf, path);

def test_of_NB(datas, labels, file_name, dir_name=u"../../data/model/"):
    gnb = joblib.load(str(dir_name + file_name + ".m").decode().encode(encoding="gbk"))
    if datas:
        pred = gnb.predict(datas)
        for i in range(0, len(pred)):
            if pred[i] == 0 and labels[i] == 0:
                continue
            # print pred[i], labels[i]
        precision = precision_score(pred, labels)
        accuracy = accuracy_score(pred, labels)
        recall = recall_score(pred, labels)
        return {"precision": precision, "accuracy": accuracy, "recall": recall}
    else:
        return None

def test_of_svm(datas, labels, file_name, dir_name=u"../../data/svm_model"):
    clf = joblib.load(str(dir_name + file_name +".m").decode().encode(encoding="gbk"))
    if datas:
        pred = clf.predict(datas)
        precision = precision_score(labels, pred)
        accuracy = accuracy_score(labels, pred)
        recall = recall_score(labels, pred)
        return {"precision": precision, "accuracy": accuracy, "recall": recall}
    else:
        return None



# 从mongodb中读取得到的法条名已经时utf8了，所以无需使用这个函数
def format_path(file_name):
    return unicode("../../data/model/" + file_name + ".m", "utf-8")


# ################deprecated#####################
def test(law_name, law_no, is_train=True):
    print "使用训练集?", is_train
    mc = DocFeature(is_train)
    vec_label = mc.get_word_vec_label()
    # positive = mc.get_doc_feature_by_law("《中华人民共和国侵权责任法》", 6, vec_label)
    prepare_start = time.time()
    positive = mc.get_doc_feature_by_law(law_name, law_no, vec_label)
    print "正集准备就绪"
    # alm.alarm_up()
    positive_features = positive['features']
    positive_doc_nos = positive['doc_nos']
    negative = mc.get_doc_feature_exclude_nos(positive_doc_nos, vec_label, len(positive_doc_nos))
    # negative = mc.get_doc_feature_exclude_nos(positive_doc_nos, vec_label, 1000)
    negative_features = negative['features']
    negative_doc_nos = negative['doc_nos']
    print "负集准备就绪"
    prepare_time = time.time() - prepare_start
    # alm.alarm_up()
    labels = [1 for x in range(0, len(positive_features))]
    labels.extend([0 for y in range(0, len(negative_features))])
    datas = positive_features
    datas.extend(negative_features)
    doc_nos = positive_doc_nos
    doc_nos.extend(negative_doc_nos)
    train_start = time.time()
    if is_train:
        print "开始训练...", len(datas)
        train_with_NB(datas, labels, law_name + "-" + str(law_no))
        train_time = time.time() - train_start
        print prepare_time, train_time
        return [prepare_time, train_time]
    else:
        print "开始测试...", len(datas)
        return test_of_NB(datas, labels, doc_nos, law_name + "-" + str(law_no))


def process(law_name, law_no, train_size, is_train=True, use_nb=True):
    print "<优化>使用训练集?", is_train
    mc = DocFeature(is_train)
    prepare_start = time.time()
    result_set = mc.get_set(law_name, law_no, train_size)
    positive_amount = result_set["positive_amount"]
    negative_amount = result_set["negative_amount"]
    features = result_set["features"]
    labels = result_set["labels"]
    # alm.alarm_up()
    prepare_time = time.time() - prepare_start
    # alm.alarm_up()
    train_start = time.time()
    if is_train:
        print "开始训练...", "正集大小:", positive_amount, "负集大小:", negative_amount, "训练个数:", train_size
        if use_nb:
            train_with_NB(features, labels, law_name + "-" + str(law_no), dir_name=u"../../data/new_model/")
        else:
            train_with_svm(features, labels, law_name + "-" + str(law_no))
        train_time = time.time() - train_start
        print "准备时间:", prepare_time, "训练时间:", train_time
        return [prepare_time, train_time, positive_amount, negative_amount]
    else:
        print "开始测试...", "正集大小:", positive_amount, "负集大小:", negative_amount, "训练个数:", train_size
        if use_nb:
            test_result = test_of_NB(features, labels, law_name + "-" + str(law_no), dir_name=u"../../data/new_model/")
        else:
            test_result = test_of_svm(features, labels, law_name + "-" + str(law_no))
        accuracy = test_result["accuracy"]
        precision = test_result["precision"]
        recall = test_result["recall"]
        return [accuracy, precision, recall, positive_amount, negative_amount]



def auto_train():
    itr = db_connector.get_sorted_law_reference()
    cnt = 0
    file_obj = open("svm_test_result_optimized.txt", "a")
    ptime = 0
    ttime = 0
    for item in itr:
        start = time.time()
        cnt += 1
        # if cnt <= 50:
        #     continue
        # if cnt >= 1100:
        #     break
        law_name = item["_id"][u"名称"]
        law_no = item["_id"][u"条号"]
        print "________________", cnt
        print "训练", law_name, str(law_no)
        train_result = process(law_name, law_no, 8000, True, False)
        ptime += train_result[0]
        ttime += train_result[1]
        p_train_size = train_result[2]
        n_train_size = train_result[3]
        train_end = time.time()
        print "训练完成", "花费" + str(train_end - start)
        # alm.alarm_down()
        # ######################测试############################
        test_result = process(law_name, law_no, 1000, False, False)
        accuracy = test_result[0]
        precision = test_result[1]
        recall = test_result[2]
        p_test_size = test_result[3]
        n_test_size = test_result[4]
        test_end = time.time()
        print "测试完成", "花费"+str(test_end-train_end)
        alm.alarm_down()

        # #####################写入文件#########################
        # file_obj.write(law_name+"#"+str(law_no)+" 精度:"+str(test_result)+",数目:"+str(item[u'数目'])+",比例:"+str(round(100*item[u'比例'], ndigits=2))+"% train_cost:"+str(train_end-start)+" test_cost:"+str(test_end-start))
        file_obj.write(law_name+"#"+str(law_no)+"-A"+str(accuracy)+"-S"+str(p_train_size)+"_"+str(n_train_size)+"_"+str(p_test_size)+"_"+str(n_test_size)+"-C"+str(train_end-start)+"_"+str(test_end-train_end)+"-P"+str(precision)+"-R"+str(recall))
        file_obj.write("\n")
        file_obj.flush()
        # alm.alarm(1)
    # file_obj.close()
    print "准备总时间=", ptime, "训练总时间=", ttime


s = time.time()
# test_result()
auto_train()
print time.time() - s
alm.alarm(5)

# test_train()
