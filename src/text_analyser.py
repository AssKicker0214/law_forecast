# encoding=utf-8
import os
import re
import jieba.analyse as ana
import time

import json

import sys

import mongodb_connector as mongo
import src.xml_reader as xml

reload(sys)
sys.setdefaultencoding('utf-8')
# doc_no = '43128'
ana.set_stop_words("../data/stop_words.txt")


def analyse(doc_no, path, is_train):
    AJJBQK = xml.getAJJBQK(path)
    if AJJBQK is not None:
        tags = ana.extract_tags(AJJBQK, topK=100, withWeight=True, allowPOS=('n', 'v'))
        words_tfs = {}
        for item in tags:
            # print item[0].encode('utf-8'),item[1]
            words_tfs[item[0]] = item[1]
        mongo.add_doc(doc_no, words_tfs, is_train)
        return True
    else:
        return False


def make_collection_doc(dir_name="../data/test_sets/MinShi1/train/", is_train=True):
    start = time.clock()
    # dir_name = "../data/test_sets/MinShi1"
    file_list = os.listdir(dir_name)
    i = 0
    j = 0
    for file_name in file_list:
        # print file_name
        j += 1
        pattern = re.compile('(\d+)\.xml')
        m = re.search(pattern, file_name)
        if m:
            doc_no = m.group(1)
            isValid = analyse(doc_no, dir_name + str(doc_no) + ".xml", is_train)
            # isValid = xml.get_laws(dir_name+"/"+file_name)
            # print json.dumps(isValid, encoding='utf-8', ensure_ascii=False)
            if isValid:
                i += 1
        else:
            print "文件名错误: ", file_name

        # if i == 5:
        #     break

    end = time.clock()
    print "collection doc finished in ", end, 's'
    print "j=", j   # j=7216


def analyse_ay(dir_name="../data/test_sets/MinShi1/train/"):
    i = 0
    file_list = os.listdir(dir_name)
    for file_name in file_list:
        i += 1
        if i % 100 == 0:
            print i
        pattern = re.compile('(\d+)\.xml')
        m = re.search(pattern, file_name)
        if m:
            doc_no = m.group(1)
            ay = xml.get_AY(dir_name + str(doc_no) + ".xml")
            if ay:
                mongo.append_ay(doc_no, ay)
        else:
            print "文件名错误: ", file_name
# make_collection_doc("../data/test_sets/MinShi1/test/", False)
'''
关键字选取，标准是足够让我从这些关键词中，猜出大致发生了什么事
'''
