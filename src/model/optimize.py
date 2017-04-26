# coding=utf-8
import json
import shutil
import os
import sys
sys.path.append("..")
from mongodb_connector import TrainResult

reload(sys)
sys.setdefaultencoding('utf-8')

def rename():
    dir_name = ""#""../../data/model/"
    db = TrainResult()
    results = db.get_results()
    for result in results:
        print json.dumps(result,encoding='utf-8',ensure_ascii=False)
        name = result[u"名称"]
        no = result[u"条号"]
        accuracy = result[u"精度"]
        rate = (result[u"负训练集"]+0.0)/result[u"正训练集"]
        new_path = unicode(dir_name+name+u"-#"+str(no)+"-A"+str(accuracy)+"-R"+str(rate)+".m")
        old_path = unicode(dir_name+name+"-"+str(no)+".m")
        os.chdir("../../data/new_model")
        try:
            os.rename(old_path, new_path)
        except WindowsError:
            continue
        # print new_name


rename()
# os.chdir("../../test")
# os.rename(unicode("啊新"), unicode("啊啊新"))