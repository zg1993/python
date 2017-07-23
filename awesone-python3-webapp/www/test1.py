from datetime import datetime
import time
from functools import reduce

import os

print(os.path.basename('1'))

# a = datetime.now().strftime("%b %d %Y %H:%M:%S")
# t = (2009, 2, 17, 17, 3, 38, 1, 48, 0)
# t =time.gmtime(time.mktime(t))

# d = {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}

# c = '01'

# def strtoint(c):
# 	return reduce(lambda x, y: 10*x+y, map(lambda x: d[x], c))
# #print(strtoint(c))

# def add(x, y):
# 	print(x, y)
# 	return x+y
# a = reduce(add, [1, 2])
# print(a)
# it = iter([1,2])
# print(next(it))
# for x in it:
# 	print(111)
