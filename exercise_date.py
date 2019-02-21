# encoding: utf8


import calendar
import datetime
import sys
from dateutil import rrule, relativedelta


# 1.计算最后一个周五的日期
# 当月
def last_weekday(month_diff):
    now = datetime.datetime.today()
    weekdays, days = calendar.monthrange(now.year, now.month + int(month_diff))
    front_diff = (calendar.FRIDAY - weekdays) % 7
    last_diff = (days - 1 - front_diff) % 7
    print weekdays, days, front_diff, last_diff
    return days - last_diff


# 2.指定月和周的从哪天开始，计算出当月和当周的开始和结束时间
# example: 03号开始（今天2019-02-01 start:2019-01-03 00:00 end:2019-02-03 00:00）
#                        2019-02-03 start:2019-02-03 00:00 end:2019-03-03 00:00
#                        2019-02-04 start:2019-02-03 00:00 end:2019-03-03 00:00
(monday, tuesday, wednesday, thursday, friday, saturday, sunday) = range(7)
select_week = tuesday
select_day = 4


def range_week_dateutil():
    today = datetime.date.today()
    today = datetime.datetime.combine(
        today, datetime.datetime.min.time())
    start_datetime = today - relativedelta.relativedelta(
        weekday=relativedelta.weekday(select_week)(-1))
    end_datetime = start_datetime + datetime.timedelta(days=7)
    return start_datetime, end_datetime


def range_week():
    pass


def range_month():
    pass


def range_month_dateutil():
    today = datetime.date.today()
    today = datetime.datetime.combine(
        today, datetime.datetime.min.time())
    the_month_day = today + relativedelta.relativedelta(
        day=select_day)
    if today.day > select_day:
        start_datetime = the_month_day
        end_datetime = start_datetime + relativedelta.relativedelta(
            months=1)
    else:
        end_datetime = the_month_day
        start_datetime = the_month_day - relativedelta.relativedelta(
            months=1)
    return start_datetime, end_datetime


if __name__ == '__main__':
    month_diff = 0
    if len(sys.argv) == 2:
        month_diff = sys.argv[1]
    print 'week: ', select_week, 'day: ', select_day
    print last_weekday(month_diff)
    print 'week: ', range_week_dateutil()
    print 'month: ', range_month_dateutil()


