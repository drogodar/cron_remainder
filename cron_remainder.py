#!/usr/bin/python

import os
from datetime import datetime
import re


def dir_walker():
    p = re.compile(r'''
    ^                    # beginning of the line
    (\d|\*|\-|/|,)*      # any number of digits, asterisks, minuses, divisions, pluses and comma
    $                    # end of the line
    ''', re.VERBOSE)

    pd = re.compile(r'''
    ^                    # beginning of the line
    (\?|L|W)*            # day of month and day of week can have question mark, "L" and "W"
    $                    # end of the line
    ''', re.VERBOSE)

    month_names = {"Jan": '1', "Feb": '2', "Mar": '3', "Apr": '4', "May": '5', "Jun": '6', "Jul": '7', "Aug": '8',
                      "Sep": '9', "Oct": '10', "Nov": '11', "Dec": '12'}

    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute

    for fname in os.listdir('/home/drozdek/cron_dir_test'):
        f = open('/home/drozdek/cron_dir_test/' + fname, 'r')
        try:
            for frow in f.readlines():
                row_elements = [k for k in frow.split(' ', 5)]
                time_list = [row_elements[i] for i in range(len(row_elements) - 1)]

                if [element for element in time_list if re.search(p, element) and len(row_elements) == 6]:
                    minute = time_list[0]
                    hour = time_list[1]
                    day_of_month = time_list[2]
                    month = time_list[3]
                    day_of_week = time_list[4]

                    job = row_elements[5][:-1]

                    sys_log_file = open('/var/log/syslog', 'r')
                    log_lines = [k for k in sys_log_file.readlines()]

                    for log_line in log_lines:
                        if log_line.find(job) > 0:
                            last_exec_date = log_line[:12]

                    lastMinute = last_exec_date.split('  ', )[1].split(' ')[1].split(':')[1]
                    lastHour = last_exec_date.split('  ', )[1].split(' ')[1].split(':')[0]
                    lastDay = last_exec_date.split('  ', )[1].split(' ')[0]
                    lastMonth = month_names[last_exec_date.split('  ')[0]]
        finally:
            f.close()

    return 'Done'


def next_date_calc():
    pass


if __name__ == '__main__':
    print dir_walker()