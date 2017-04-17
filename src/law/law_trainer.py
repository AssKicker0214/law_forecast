# coding=utf-8
import sys
import time
from sklearn.naive_bayes import GaussianNB
from sklearn.externals import joblib
from sklearn.metrics import accuracy_score

sys.path.append("..")
import tool.alarm as alm
from mongodb_connector import DocFeature
import mongodb_connector as db_connector

reload(sys)
sys.setdefaultencoding('utf-8')

def train_with_NB(datas, labels, file_name):
    gnb = GaussianNB()
    gnb.fit(datas, labels)
    path = u"../../data/model/"+str(file_name)+u".m"

    joblib.dump(gnb, path)


def test_of_NB(datas, labels, doc_nos, file_name):
    gnb = joblib.load(str("../../data/model/"+file_name+".m").decode().encode(encoding="gbk"))
    pred = gnb.predict(datas)
    # for i in range(0, len(pred)):
    #     print doc_nos[i], pred[i], labels[i]
    return accuracy_score(pred, labels)


# 从mongodb中读取得到的法条名已经时utf8了，所以无需使用这个函数
def format_path(file_name):
    return unicode("../../data/model/"+file_name+".m", "utf-8")

def test(law_name, law_no, is_train=True ):
    print "使用训练集?", is_train
    mc = DocFeature(is_train)
    vec_label = mc.get_word_vec_label()
    # positive = mc.get_doc_feature_by_law("《中华人民共和国侵权责任法》", 6, vec_label)
    positive = mc.get_doc_feature_by_law(law_name, law_no, vec_label)
    print "正集准备就绪"
    positive_features = positive['features']
    positive_doc_nos = positive['doc_nos']
    negative = mc.get_doc_feature_exclude_nos(positive_doc_nos, vec_label, len(positive_doc_nos))
    # negative = mc.get_doc_feature_exclude_nos(positive_doc_nos, vec_label, 1000)
    negative_features = negative['features']
    negative_doc_nos = negative['doc_nos']
    print "负集准备就绪"
    labels = [1 for x in range(0, len(positive_features))]
    labels.extend([0 for y in range(0, len(negative_features))])
    datas = positive_features
    datas.extend(negative_features)
    doc_nos = positive_doc_nos
    doc_nos.extend(negative_doc_nos)
    if is_train:
        print "开始训练...", len(datas)
        train_with_NB(datas, labels, law_name+"-"+str(law_no))
    else:
        print "开始测试...", len(datas)
        return test_of_NB(datas, labels, doc_nos, law_name+"-"+str(law_no))



def test_result():
    # test("《中华人民共和国交通安全法》", 76)
    test("《中华人民共和国交通安全法》", 76, False)


def auto_train():
    itr = db_connector.get_sorted_law_reference()
    cnt = 0
    file_obj = open("test_result.txt", "w")
    for item in itr:
        start = time.time()
        cnt += 1
        if cnt<4:
            continue
        law_name = item["_id"][u"名称"]
        law_no = item["_id"][u"条号"]
        print "________________", cnt
        print "训练", law_name, str(law_no)
        test(law_name, law_no)
        train_end = time.time()
        print "训练完成", "花费"+str(train_end-start)
        test_result = test(law_name, law_no, False)
        test_end = time.time()
        print "测试完成", "花费"+str(test_end-start)
        file_obj.write(law_name+"#"+str(law_no)+" 精度:"+str(test_result)+",数目:"+str(item[u'数目'])+",比例:"+str(round(100*item[u'比例'], ndigits=2))+"% train_cost:"+str(train_end-start)+" test_cost:"+str(test_end-start))
        file_obj.write("\n")
        file_obj.flush()
        print ""
        alm.alarm(1)
    file_obj.close()

s = time.time()
# test_result()
auto_train()
print time.time()-s
alm.alarm(5)

# test_train()
