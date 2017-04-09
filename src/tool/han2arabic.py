# coding=utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


def han2arabic(han):
    try:
        return int(han)
    except ValueError:
        pass

    total = 0
    tmp = 0
    # print han
    for c in list(unicode(han)):

        if c == "十":
            if tmp == 0:
                tmp = 1
            tmp *= 10
            total += tmp
            tmp = 0
        elif c == "百":
            tmp *= 100
            total += tmp
            tmp = 0
        elif c == "千":
            tmp *= 1000
            total += tmp
            tmp = 0
        else:
            tmp = figure_map(c)
        # print c, tmp, total
    total += tmp
    return total


def figure_map(han):
    i = 0
    if han == "一":
        i = 1
    elif han == "二":
        i = 2
    elif han == "三":
        i = 3
    elif han == "四":
        i = 4
    elif han == "五":
        i = 5
    elif han == "六":
        i = 6
    elif han == "七":
        i = 7
    elif han == "八":
        i = 8
    elif han == "九":
        i = 9
    else:
        pass
    return i

# print han2arabic("一百四十六")
# print figure_map(u"二")