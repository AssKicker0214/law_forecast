# coding=utf-8
import json
import os
import re
import sys
from law.law_analyser import get_law_featured
from mongodb_connector import get_idf
import xml_reader as xml
import jieba.analyse as ana

reload(sys)
sys.setdefaultencoding('utf-8')


def match():
    law_array = []
    inner_product_array = []


def test():
    dir_name = "../data/test_sets/MinShi1"
    file_list = os.listdir(dir_name)
    j = 0
    for file_name in file_list:
        j += 1
        if j < 7218: # 7217 124095
            continue
        # 开始测试集
        pattern = re.compile('(\d+)\.xml')
        m = re.search(pattern, file_name)
        if m:
            doc_no = m.group(1)
            AJJBQK = xml.getAJJBQK(dir_name + "/" + doc_no + ".xml")
            if AJJBQK:
                print "test doc no = ", doc_no
                text_vector = make_word_vector(AJJBQK)
                law_featured_array = get_law_featured()
                articles = []
                products = []

                for law_featured in law_featured_array:
                    law_vector = make_law_vector(law_featured)
                    product = inner_product(text_vector, law_vector)
                    articles.append(law_featured[u"法名"]+str("条：【")+str(law_featured[u"条号"])+"】")
                    products.append(product)

                sort(articles, products)
                count = 0
                for i in range(0, len(articles)-1):
                    count += 1
                    if count > 300:
                        break
                    print count, articles[i], products[i]
            else:
                continue
        else:
            print "文件名错误: ", file_name
        break


def make_word_vector(AJJBQK):
    ana.set_stop_words("../data/stop_words.txt")
    tags = ana.extract_tags(AJJBQK, topK=100, withWeight=True, allowPOS=('n', 'v'))
    text_vector = {"word": [], "vector": []}
    for tag in tags:
        word = tag[0]
        tf = tag[1]
        idf = get_idf("law_forecast_minshi1", "doc_word_reference", word)
        # print idf, word
        tf_idf = tf * idf
        text_vector['word'].append(word)
        text_vector['vector'].append(tf_idf)
        # print word, tf_idf
    return text_vector


def make_law_vector(law_featured):
    law_vector = {"word": [], "vector": []}
    words = []
    # try:
    words = law_featured[u"词"]
    # except KeyError:
    #     print json.dumps(law_featured, ensure_ascii=False, indent=1)
    for word in words:
        law_vector["word"].append(word)
        law_vector["vector"].append(1.0)
    return law_vector


def inner_product(text_vector, law_vector):
    size_text_vector = len(text_vector["word"])
    size_law_vector = len(law_vector["word"])
    product = 0.0
    for i in range(0, size_law_vector-1):
        word_law = law_vector["word"][i]
        weight_law = law_vector["vector"][i]
        for j in range(0, size_text_vector-1):
            word_text = text_vector["word"][j]
            weight_text = text_vector["vector"][j]
            if word_text == word_law:
                product += weight_law * weight_text
                break
    return product


def sort(keys, values, desc=True):
    size = len(keys)
    for i in range(0, size-1):
        for j in range(0, size-2):
            needSwap = False
            if (values[j] < values[j+1]) and desc:
                needSwap = True
            if (values[j] > values[j+1]) and not desc:
                needSwap = True

            if needSwap:
                tmp_value = values[j]
                values[j] = values[j+1]
                values[j+1] = tmp_value
                tmp_key = keys[j]
                keys[j] = keys[j+1]
                keys[j+1] = tmp_key

test()
# str = "\xe8\xaf\x8d"
# print str.encode()