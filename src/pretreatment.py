# coding=utf-8
# 预处理输入文本
import os
import re
import sys
from statistic.withdraw_doc import get_withdraw_doc_no
import xml_reader as xml

sys.path.append("..")
from mongodb_connector import DocFeature

def corresponding_to_patterns(text, patterns):
    # patterns = get_withdraw_accusation_patterns()
    for pattern in patterns:
        # print pattern
        c = re.compile(pattern)
        m = c.search(text)
        if m:
            print "->", m.group(0), "<-"
            return True
    return False


def get_withdraw_accusation_patterns():
    file_obj = open("../data/pattern_withdraw_accusation.txt")
    patterns = []
    for line in file_obj:
        patterns.append(line.strip())
    file_obj.close()
    return patterns


# t = '''相伴，无人购物，缺少灯。 被告纺织城辩履行到2017年只是合同履行期限的部分，属于合同变更，不是继续履行合同。合同变更是双方协商一致以其其他法定原因。原告在合同履行期间违反了双方约定的承租人义务，擅自将租赁商铺转租他人、拒绝交纳物业费，违反合同约定。导致我公司要求解除合同合理合法也符合双方的约定，其要求继续履行的诉请不应得到支持。 反诉原告纺织城诉称，请求判令解除双方签订的《沈阳国际纺织服装城商铺租赁合同》（NO．51000095），判令反诉被告支付拖欠的物业管理费56580元、电费295．5元，并按银行同期贷款利率计算违约金，自2013年12月11日起计算至判决确定支付之日止；诉讼费由反诉被告承担。2012年7月5日反诉原告将商铺交付反诉被告使用，约定2014年3月10日前免收租金及物业管理费仅交纳电费，反诉原告及反诉被告于2013年12月1日签订了《沈阳国际纺织服装城商铺租赁合同》，约定了经营范围、租赁期限、租金和物业管理费交费标准、交费方法、违约责任等条款。合同签订后，反诉原告履行了交付商铺使用的义务，反诉被告未履行及交纳物业费及电费的义务，经反诉原告多次催告后仍未交纳，还将其所租赁的商铺擅自转租第三人，反诉被告的行为已经构成根本违约。 反诉被告李永亮辩称，我方不是要求变更合同，而是按照合同约定逐段进行主张。双方签订的合同是双方真实意思表示，且已经实际履行，原告为履行合同已经抛弃了原经营场所，投入必要财力物力，被告单方提出解除合同是违约行为。关于拖欠物业管理费的问题，反诉原告不是物业公司也不具备物业公司管理职能，现反诉原告拒收物业管理费，反诉原告的本意是想将纺织城五楼整体对外招商，与五层业主解除合同。 经审理查明，2013年12月1日，原告（反诉被告）与被告（反诉原告）签订《沈阳国际纺织服装城商铺租赁合同》（NO．51000095），合同第一条约定原告（反诉被告）租赁沈阳国际纺织服装城B5s-503、B5s-503a商铺，使用面积按实际使用面积计算，经营范围为户外野营服装，租赁期限为18年，自2014年3月11日至2032年3月10日，租金和物业管理费交纳标准为：2014年3月11日至2015年3月10日，租金为零，物业管理费为1．5元／㎡／天……。合同第二条约定，第一年度的物业费须于2013年12月10日前一次性交纳，以后每年度的租金和物业管理费须在上一个年度结束之日计算3个月前一次性交纳，原告（反诉被告）不按时向被告（反诉原告）交纳租金及物业管理费的，被告（反诉原告）有权无条件收回商铺，合同终止。原告（反诉被告）所租商铺独立安装电表，自合同签订之日起按季度实际发生金额交付。原告（反诉被告）应于每季度首月5日前向被告（反诉原告）交纳上季度电费。电费标准为每度电1．1元计算。第六条约定如果原告（反诉被告）违反下列任何一项规定，被告（反诉原告）有权单方解除本合同，没收原告（反诉被告）经营保证金，并将原告（反诉被告）清退出场，已交纳的租金、物业管理费等费用概不退还原告（反诉被告）：……2、原告（反诉被告）拖欠任何一项部分或全部应交费用达一个月以上，在经被告（反诉原告）准许的期限内仍未付清的；3、擅自合同约定的经营商品种类或经营范围的；4、原告（反诉被告）擅自将商铺使用权用于抵押、担保、转租、转让或转包的；……。第九条约定被告（反诉原告）给原告（反诉被告）所发的函、通知或公告等文书，以下任何一种情况下均视为送达：……4、被告（反诉原告）采用市场内公告方式的，以被告在沈阳国际纺织服装城内张贴公告日视为送达；……。合同签约日期下方载有“本合同开业时间作废，五层按实际开业时间起算”字样。在合同履行的过程中，原告（反诉被告）实际使用的商铺为B5s-503、B5s-503a。被告（反诉原告）于2014年6月14日在纺织城宣传栏处张贴公告，向五楼全体商户发出公告，通知尚未缴纳2014年3月11日至2015年3月10日（即第一年度）物业管理费的商户，于本公告发布之日起30日内到被告（反诉原告）财务处交纳相关费用，逾期不交纳的将根据合同第二条、第六条第二款之规定，被告（反诉原告）将单方解除合同，无条件收回商铺，并清退出场。合同中并未约定纺织城五层开业时间。 2015年1月19日，被告（反诉原告）向原告（反诉被告）发出《函告》，告知原告（反诉被告）于收到本函告7日内到被告（反诉原告）财务处交纳拖欠的物业管理费及电费，正式通知原告（反诉被告）解除合同收回商铺。原告（反诉被告）于2015年1月19日收到该《函告》。 另查明，沈阳国际纺织服装城五层于2012年8月对外营业。 在本案审理过程中，被告（反诉原告）撤回要求原告（反诉被告）交纳物业费及违约金的诉讼请求。 上述事实，有原告（反诉被告）、被告（反诉原告）的陈述、《沈阳国际纺织服装城商铺租赁合同》、公告及函告照片、电费通知单等证据，经庭审质证，本院予以确认。 '''
t = "撤销终止，其权利义务由被告承继。为此，原告备文起诉"

def test():
    withdraw_doc_no_list = get_withdraw_doc_no()
    patterns = get_withdraw_accusation_patterns()
    dir_name = "../data/test_sets/MinShi1/test/"
    file_list = os.listdir(dir_name)
    i = 0
    j = 0
    x = 0
    miss = 0
    start = False
    file_list = DocFeature(False).get_doc_no_randomly(5000)
    for file_name in file_list:
        pattern = re.compile('(\d+)(\.xml)*')
        m = re.search(pattern, file_name)
        if m:
            doc_no = m.group(1)
            ##########
            # if doc_no == "1123096":
            #     start = True
            # if not start:
            #     continue
            ###########
            # isValid = analyse(doc_no, "../data/test_sets/MinShi1/train/" + str(doc_no) + ".xml")
            text = xml.get_AJJBQK_SSJL(dir_name + str(doc_no) + ".xml")
            if text:
                x += 1
                # print text
                print "~~~~~~~~~~~~~~~~~~~~~~~~~"
                if corresponding_to_patterns(text.encode('utf-8'), patterns):
                    in_list = False
                    for withdraw_doc_no in withdraw_doc_no_list:
                        if withdraw_doc_no == doc_no:
                            in_list = True
                    if in_list:
                        i += 1
                    else:
                        j += 1
                        print "不在撤诉列表中：", doc_no
                        # print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
                    # print i, "/", x, doc_no
                    # print "----------------"
                    # print doc_no, "fail"
                    # print text
                else:
                    for withdraw_doc_no in withdraw_doc_no_list:
                        if withdraw_doc_no == doc_no:
                            print "需要补充样式：", doc_no, "<" + str((0.0 + i) / x) + ">", i, x
                            print "=============================="
                            miss += 1
                            break

                print "hit:", i, "wrong:", j, "miss:", miss, "total:", x
        else:
            print "文件名错误: ", file_name
    print "撤诉数量:", i, "总数量:", x

# p = []
# t = "撤销。起诉"
# p.append("(撤回|撤销)[^。一-龥、（）]*(诉讼|起诉|本诉|反诉|告诉)")
# print corresponding_to_patterns(t, p)
test()
#18:32