# coding=utf-8


def sort(labels, values, desc=True):
    max = len(values)
    for i in range(0, max - 1):
        for j in range(i, max - 1):
            left = values[j]
            right = values[j + 1]
            if left > right:
                tmp_label = labels[j]
                labels[j] = labels[j + 1]
                labels[j + 1] = tmp_label

                tmp_value = left
                values[j] = values[j + 1]
                values[j + 1] = tmp_value
    if desc:
        labels.reverse()
        values.reverse()
    return {"labels": labels, "values": values}

