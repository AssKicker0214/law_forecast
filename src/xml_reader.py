# coding=utf-8
import re
import xml.dom.minidom as utl

from src.tool import han2arabic as trans


def getAJJBQK(filePath):
    # dom = utl.parse('../msys/1016.xml')
    dom = utl.parse(filePath)
    writ = dom.documentElement
    QW = writ.getElementsByTagName("QW")[0]
    AJJBQK = None
    try:
        AJJBQK = QW.getElementsByTagName("AJJBQK")[0]
    except IndexError:
        # print filePath+" 案件基本情况缺失"
        return None
    return AJJBQK.getAttribute("value")


def get_AJJBQK_SSJL(file_path):
    dom = utl.parse(file_path)
    writ = dom.documentElement
    QW = writ.getElementsByTagName("QW")[0]
    AJJBQK = None
    SSJL = None
    try:
        AJJBQK = QW.getElementsByTagName("AJJBQK")[0]
    except IndexError:
        pass

    try:
        SSJL = QW.getElementsByTagName("SSJL")[0]
    except IndexError:
        pass

    if (AJJBQK is None) and (SSJL is None):
        return None

    text = ""
    if AJJBQK:
        text += AJJBQK.getAttribute("value")
    if SSJL:
        text += SSJL.getAttribute("value")

    return text

def get_laws(filePath):
    # print filePath
    dom = utl.parse(filePath)
    writ = dom.documentElement
    QW = writ.getElementsByTagName("QW")[0]

    FLFTFZs_array = []
    FLFTFZs1 = None
    try:
        PJJG = QW.getElementsByTagName("PJJG")[0]
        FLFTYYs = PJJG.getElementsByTagName("FLFTYY")
        for FLFTYY in FLFTYYs:
            FLFTFZs1 = FLFTYY.getElementsByTagName("FLFTFZ")
            FLFTFZs_array.append(FLFTFZs1)
    except IndexError:
        pass

    FLFTFZs2 = None
    try:
        CPFXGC = QW.getElementsByTagName("CPFXGC")[0]
        FLFTYYs = CPFXGC.getElementsByTagName("FLFTYY")
        for FLFTYY in FLFTYYs:
            FLFTFZs2 = FLFTYY.getElementsByTagName("FLFTFZ")
            FLFTFZs_array.append(FLFTFZs2)
    except IndexError:
        # print "裁判分析过程缺失", filePath
        pass

    laws = []
    for FLFTFZs in FLFTFZs_array:
        append_law(laws, FLFTFZs)
    return laws


def append_law(laws, FLFTFZs):
    if FLFTFZs is None:
        return
    for FLFTFZ in FLFTFZs:
        try:
            MC = FLFTFZ.getElementsByTagName("MC")[0]
            Ts = FLFTFZ.getElementsByTagName("T")
            name = MC.getAttribute("value")
            for T in Ts:
                law = {}
                law["名称"] = name
                law["条号"] = get_number(T.getAttribute("value"))
                laws.append(law)
        except IndexError:
            return


def get_AY(file_path):
    dom = utl.parse(file_path)
    writ = dom.documentElement
    ay = {}
    SSJL = None
    try:
        QW = writ.getElementsByTagName("QW")[0]
        SSJL = QW.getElementsByTagName("SSJL")[0]
        AY = SSJL.getElementsByTagName("AY")[0]
        ay["完整案由"] = AY.getElementsByTagName("WZAY")[0].getAttribute("value")
        ay["案由代码"] = AY.getElementsByTagName("AYDM")[0].getAttribute("value")
    except IndexError:
        print file_path, "index error"
        return False

    return ay


def get_number(han):
    pattern = re.compile(u"第(\S+)条")
    m = re.search(pattern, han)
    number = None
    if m:
        number = trans.han2arabic(m.group(1))

    return number
