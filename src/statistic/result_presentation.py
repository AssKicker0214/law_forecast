# coding=utf-8
from matplotlib import pyplot as plt
import sys
import numpy as np

sys.path.append("..")
from mongodb_connector import TrainResult


plt.figure(figsize=(9, 6))
n = 100
# rand 均匀分布和 randn高斯分布
# x = np.random.randn(1, n)
db = TrainResult()
results = db.get_results()
x = []
y = []
for result in results:
    accuracy = result[u"精度"]
    rate = result[u"被引用百分比"]
    amount = result[u"被引用数量"]
    y.append(rate)
    x.append(accuracy)
    # y.append(amount)
# x = [1, 2, 3, 4, 6]
# y = [1, 2, 3, 4, 5]
# print type(x)
# y = np.random.randn(1, n)
# T = np.arctan2(x, y)
plt.scatter(x, y, c=None, s=50, alpha=0.4, marker='o')
# T:散点的颜色
# s：散点的大小
# alpha:是透明程度
plt.show()
