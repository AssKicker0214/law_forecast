# coding=utf-8
import json
import os
import re
import time
import mongodb_connector as mongo
from text_analyser import make_collection_doc
import text_analyser as ta
from alarm import alarm
from xml_reader import get_laws


def append_law_to_doc():
    dir_name = "../data/test_sets/MinShi1/train"
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
            laws = get_laws(dir_name + "/" + file_name)
            # print doc_no
            # print json.dumps(laws, encoding='utf-8', ensure_ascii=False)
            if laws:
                mongo.add_relevant_law(doc_no, laws)
                i += 1
        else:
            print "文件名错误: ", file_name

            # if i == 5:
            #     break


def make_corpus():
    # make_collection_doc()
    #
    mongo.process_doc_tf_idf()


time.clock()
# append_law_to_doc()
# make_corpus()
ta.analyse_ay()
print time.clock()
alarm(10)
