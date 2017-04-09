# coding=utf-8
from pymongo import MongoClient
import law.law_analyser
client = MongoClient("localhost", 27017)
db = client.get_database("law_forecast_minshi1")
collection_doc = db['doc']


# 含有《民事诉讼法》145条的文书
def get_withdraw_doc_no():
    query = {"法条": {"$elemMatch": {"名称": "《中华人民共和国民事诉讼法》", "条号": 145}}}
    show = {"doc_no": 1, "_id":0}
    rs = collection_doc.find(query, show)
    rs_set = []
    for item in rs:
        rs_set.append(item['doc_no'].encode())

    return rs_set



# rs = get_withdraw_doc_no()
# for item in rs:
#     if item == '1199758':
#         print "true"