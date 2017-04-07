# coding=utf-8
import json
import time

import sys

import src.alarm

from pymongo import MongoClient
from jieba import analyse as ana

reload(sys)
sys.setdefaultencoding('utf-8')
client = MongoClient("localhost", 27017)
db_name = "law"

db = client.get_database(db_name)
collection_law = db['law']
collection_law_featured = db['law_featured']
collection_part_featured = db['part_featured']
collection_chapter_featured = db['chapter_featured']
collection_section_featured = db['section_featured']
collection_article_featured = db['article_featured']


def feature_laws():
    # law_name = ""
    #
    # part_no = 0
    # part_feature = []
    #
    # chapter_no = 0
    # chapter_feature = []
    #
    # section_no = 0
    # section_feature = []
    #
    # article_no = 0
    # article_feature = []

    ana.set_stop_words("./stopwords_law_feature.txt")
    laws = collection_law.find({}, {"_id": 0})
    for law in laws:
        # print json.dumps(law, ensure_ascii=False)
        law_name = law[u"名称"]
        print law_name
        # feature = ana.extract_tags(law_name, allowPOS=('n', 'v'))
        # print json.dumps(feature, ensure_ascii=False)
        parts = law[u"编"]
        for part in parts:
            part_no = part[u"编号"]
            part_feature = get_feature(part_no, part)
            # if part_feature:
            #     print json.dumps(part_feature, ensure_ascii=False)
            chapters = part[u"章"]
            for chapter in chapters:
                chapter_no = chapter[u"章号"]
                chapter_feature = get_feature(chapter_no, chapter)
                # if chapter_feature:
                #     print json.dumps(chapter_feature, ensure_ascii=False)
                sections = None
                try:
                    sections = chapter[u"节"]
                except KeyError:
                    print chapter_no
                for section in sections:
                    section_no = section[u'节号']
                    section_feature = get_feature(section_no, section)
                    articles = section[u"条"]
                    for article in articles:
                        article_no = article[u"条号"]
                        article_feature = get_feature(article_no, article)
                        item = {"法名": law_name, "编号": part_no, "章号": chapter_no, \
                                "节号": section_no, "条号": article_no, "词": article_feature}
                        collection_article_featured.insert(item)


def get_feature(no, level):
    if no == 0:
        return []
    else:
        content = level[u"内容"]
        feature = ana.extract_tags(content, allowPOS=('n', 'v'))
        return feature


def clear_db():
    collection_article_featured.remove()
    collection_law_featured.remove()


def get_law_featured():
    laws = collection_article_featured.find({}, {'_id':0})
    return laws


# process()
