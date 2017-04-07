# coding=utf-8
import time

import alarm

from pymongo import MongoClient
import timer
import math

#####  PROCEDURE   ####################################
# 1. analyse docs to build DocCorpus
# 2. count reference
# 3. culculate inverse document frequency
# 4. culculate tf_idf of DocCorpus as doc feature
##########################################################
client = MongoClient("localhost", 27017)
#### 注意修改数据库名
# db_name = "law_forecast_minshi1"

db = client.get_database("law_forecast_minshi1")
collection_doc = db['doc']
collection_doc_word_reference = db['doc_word_reference']


def add_doc(doc_no, words_tfs):
    collection_doc.insert({'doc_no': doc_no, 'words_tfs': words_tfs})


def add_relevant_law(doc_no, laws):
    collection_doc.update({'doc_no': doc_no}, {'$set': {'法条': laws}}, True)


def recalculate_reference():
    collection_doc_word_reference.remove()
    print "corpus cleared"
    i = 0
    for item in collection_doc.find(no_cursor_timeout=True):
        i += 1
        if i%100 == 0:
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
        if count%100==0:
            print (count/total)*100, "%"
        reference = item['reference']
        _id = item['_id']
        idf = math.log10(total / (1.0 + reference))
        collection_doc_word_reference.update({"_id": _id}, {"$set": {"idf": idf}})


def calculate_tf_idf():
    count = 0
    for item in collection_doc.find():
        _id = item['_id']
        words_tfs = item['words_tfs']
        words_tf_idfs = {}
        count += 1
        if count%100==0:
            print count
        for key, value in words_tfs.items():
            idf = collection_doc_word_reference.find_one({'word': key})['idf']
            tf_idf = idf * value
            words_tf_idfs[key] = tf_idf
        collection_doc.update({"_id": _id}, {"$set": {"words_tf_idfs": words_tf_idfs}})


def append_law(doc_no, laws):
    pass


def append_ay(doc_no, ay):
    collection_doc.update({'doc_no': doc_no}, {'$set': {'案由': ay}}, False)

# def culculate_tf_idf_optimized():
#     collection_doc.aggregate([{"$project":{}}])
#     pass


def process_doc_tf_idf():
    # time.clock()
    # recalculate_reference()
    print "reference calculation done"
    calculate_idf()
    print "idf calculation done"
    calculate_tf_idf()
    # print "finished in", time.clock(), "s"
    # alarm.alarm()


def get_idf(db_name, collection_name, word):
    collection = MongoClient("localhost", 27017).get_database(db_name)[collection_name]
    item = collection.find_one({'word': word}, {"idf": 1})
    if item:
        return item['idf']
    else:
        print word, ", no match in corpus"
        return 1.0
