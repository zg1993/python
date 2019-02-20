# encoding: utf8


import calendar
import datetime
import sys


# 计算最后一个周五的日期
# 当月
def last_weekday(month_diff):
    now = datetime.datetime.today()
    weekdays, days = calendar.monthrange(now.year, now.month + int(month_diff))
    front_diff = (calendar.FRIDAY - weekdays) % 7
    last_diff = (days - 1 - front_diff) % 7
    print weekdays, days, front_diff, last_diff
    return days - last_diff


if __name__ == '__main__':
    month_diff = 0
    if len(sys.argv) == 2:
        month_diff = sys.argv[1]
    print last_weekday(month_diff)


