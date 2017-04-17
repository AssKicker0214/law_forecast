# coding=utf-8
import math
import time

from pymongo import MongoClient
from src.tool import alarm

#####  PROCEDURE   ####################################
# 1. analyse docs to build DocCorpus
# 2. count reference
# 3. culculate inverse document frequency
# 4. culculate tf_idf of DocCorpus as doc feature
##########################################################
#### 注意修改数据库名
# db_name = "law_forecast_minshi1"
client = MongoClient("localhost", 27017)

db = client.get_database("law_forecast_minshi1")
collection_doc = db['doc']
collection_doc_word_reference = db['doc_word_reference']
collection_doc_for_test = db['doc_for_test']


######################## 训练集和测试集是否有交叉？ 答案：没有
# doc_no_for_test = []
# doc_no = []
# for doc in collection_doc_for_test.find({},{"doc_no":1, "_id":0}):
#     doc_no_for_test.append(doc['doc_no'])
# for doc in collection_doc.find({},{"doc_no":1, "_id":0}):
#     doc_no.append(doc['doc_no'])
#
# count = 0
# for n1 in doc_no:
#     for n2 in doc_no_for_test:
#         if n1 == n2:
#             count += 1
# print count



def add_doc(doc_no, words_tfs, is_train=True):
    if is_train:
        collection_doc.insert({'doc_no': doc_no, 'words_tfs': words_tfs})
    else:
        collection_doc_for_test.insert({'doc_no': doc_no, 'words_tfs': words_tfs})


def add_relevant_law(doc_no, laws, is_train=True):
    if is_train:
        collection_doc.update({'doc_no': doc_no}, {'$set': {'法条': laws}}, True)
    else:
        collection_doc_for_test.update({'doc_no': doc_no}, {'$set': {'法条': laws}}, True)


def recalculate_reference():
    collection_doc_word_reference.remove()
    print "corpus cleared"
    i = 0
    for item in collection_doc.find(no_cursor_timeout=True):
        i += 1
        if i % 100 == 0:
            print i
        words_tfs = item["words_tfs"]
        for word, tf in words_tfs.items():
            collection_doc_word_reference.update({'word': word}, {"$inc": {'reference': 1}}, True)


def calculate_idf():
    # collection_doc_word_reference.update({},{"$set":{'idf':}})
    count = 0.0
    total = collection_doc.find().count()
    for item in collection_doc_word_reference.find(no_cursor_timeout=True):
        count += 1
        if count % 100 == 0:
            print (count / total) * 100, "%"
        reference = item['reference']
        _id = item['_id']
        idf = math.log10(total / (1.0 + reference))
        collection_doc_word_reference.update({"_id": _id}, {"$set": {"idf": idf}})


def calculate_tf_idf(is_train=True):
    count = 0
    collection = None
    if is_train:
        collection = collection_doc
    else:
        collection = collection_doc_for_test
    for item in collection.find(no_cursor_timeout=True):
        _id = item['_id']
        words_tfs = item['words_tfs']
        words_tf_idfs = {}
        count += 1
        # if count % 100 == 0:
        #     print count
        # if count < 30801:
        #     continue
        for key, value in words_tfs.items():
            word_idf = collection_doc_word_reference.find_one({'word': key})
            if word_idf is None:
                print "语料库缺少词：", key
                continue
            else:
                idf = word_idf['idf']
                tf_idf = idf * value
                words_tf_idfs[key] = tf_idf
        collection.update({"_id": _id}, {"$set": {"words_tf_idfs": words_tf_idfs}})


def append_ay(doc_no, ay):
    collection_doc.update({'doc_no': doc_no}, {'$set': {'案由': ay}}, False)


# def culculate_tf_idf_optimized():
#     collection_doc.aggregate([{"$project":{}}])
#     pass


def process_doc_tf_idf():
    # recalculate_reference()
    # print "reference calculation done"
    # calculate_idf()
    # print "idf calculation done"
    calculate_tf_idf()


def get_idf(db_name, collection_name, word):
    collection = MongoClient("localhost", 27017).get_database(db_name)[collection_name]
    item = collection.find_one({'word': word}, {"idf": 1})
    if item:
        return item['idf']
    else:
        print word, ", no match in corpus"
        return 1.0


# calculate_tf_idf(False)
# alarm.alarm(5)
def get_sorted_law_reference():
    itr = collection_doc.aggregate([{'$project': {"法条": 1, "doc_no": 1, "_id": 0}}, {'$unwind': "$法条"},
                                    {'$group': {"_id": {"名称": "$法条.名称", "条号": "$法条.条号"}, "数目": {'$sum': 1}}},
                                    {'$sort': {"数目": -1}},
                                    {'$project': {"数目": 1, "比例": {'$divide': ["$数目", 118525]}}}])
    return itr


class DocFeature:
    MAX = 5000

    def __init__(self, is_train_set):
        c = MongoClient("localhost", 27017)

        db_minshi = c.get_database("law_forecast_minshi1")
        if is_train_set:
            self.collection = db_minshi['doc']
        else:
            self.collection = db_minshi['doc_for_test']

    def get_word_vec_label(self):
        itr = collection_doc_word_reference.find({"reference": {"$gt": 1}}, {"word": 1, "_id": 0},
                                                 no_cursor_timeout=True)
        vec = []
        for item in itr:
            vec.append(item['word'])
        return vec

    def get_doc_feature_by_law(self, law_name, article_no, vec_label):
        features = []
        doc_nos = []
        cnt = 0
        for item in self.collection.find({"法条": {"$elemMatch": {"名称": law_name, "条号": article_no}}},
                                         {"words_tf_idfs": 1, "_id": 0, "doc_no": 1}, no_cursor_timeout=True):
            # print item['doc_no']
            cnt += 1
            if cnt > self.MAX:
                break
            words_tf_idfs = item['words_tf_idfs']
            doc_nos.append(item['doc_no'])
            vec = [0 for x in range(0, len(vec_label))]
            for key, value in words_tf_idfs.items():
                for i in range(0, len(vec_label)):
                    if key == vec_label[i]:
                        vec[i] = value
                        # print "->", item['doc_no']
                        break
            features.append(vec)
        return {"doc_nos": doc_nos, "features": features}

    def get_doc_feature_exclude_nos(self, doc_nos, vec_label, size=10000):
        features = []
        doc_nos_excluded = []
        count = 0
        for item in self.collection.find({}, {"words_tf_idfs": 1, "_id": 0, "doc_no": 1}, no_cursor_timeout=True):
            if item['doc_no'] in doc_nos:
                continue
            else:
                count += 1
                if count > size or count>self.MAX:
                    break
                doc_nos_excluded.append(item['doc_no'])
                words_tf_idfs = item['words_tf_idfs']
                vec = [0 for x in range(0, len(vec_label))]
                for key, value in words_tf_idfs.items():
                    for i in range(0, len(vec_label) - 1):
                        if key == vec_label[i]:
                            vec[i] = value
                            break
                features.append(vec)
        return {"doc_nos": doc_nos_excluded, "features": features}


        # process_doc_tf_idf()
