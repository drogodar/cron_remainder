#!/usr/bin/python

import re
import subprocess
from datetime import datetime, timedelta
from monthdelta import MonthDelta
import calendar

today = datetime.today()
today = datetime(today.year, today.month, today.day, today.hour, today.minute)


def crontab_processing():
    """Processes the 'crontab -l' output and finally prints next time execution of jobs."""

    # Get 'crontab -l' output and error(if it was).
    # Command will be executed by some user and give only his crontab file.
    sp = subprocess.Popen(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = sp.communicate()
    if err:
        return err  # possible error: 'no crontab for drozdek'
    if out:
        crontab_rows = out.split("\n")

    # Compile RegEx for speed and beauty
    p = re.compile('''
    ^               # beginning of the line
    (\d|\*|,|-|/)*      # any number of digits, asterisks, comma TODO: ?, 'L', 'M'
    $               # end of the line
    ''', re.VERBOSE)

    month_names = {"Jan": '1', "Feb": '2', "Mar": '3', "Apr": '4', "May": '5', "Jun": '6', "Jul": '7', "Aug": '8',
                   "Sep": '9', "Oct": '10', "Nov": '11', "Dec": '12'}

    # Split rows for five time elements and job.
    for cron_row in crontab_rows:
        row_elements = [k for k in cron_row.split(' ', 5)]
        time_list = [row_elements[i] for i in range(len(row_elements) - 1)]

        # Filter rows through the RegEx and check for len.
        # After that we have only "right" rows with jobs
        if [element for element in time_list if re.search(p, element) and len(row_elements) == 6]:
            job = row_elements[5][:-1]

            # Try to find previous job's executions.
            try:
                sys_log_file = open('/var/log/cron', 'r')  # Specify here cron log destination for your distr.
                                                           # Not required for current version.
                log_lines = [k for k in sys_log_file.readlines()]

                # Find and parse the last execution time
                for log_line in log_lines:
                    if log_line.find(job) > -1:
                        last_exec_date = log_line[:12]

                last_minute = last_exec_date.split('  ', )[1].split(' ')[1].split(':')[1]
                last_hour = last_exec_date.split('  ', )[1].split(' ')[1].split(':')[0]
                last_day = last_exec_date.split('  ', )[1].split(' ')[0]
                last_month = month_names[last_exec_date.split('  ')[0]]

                # Execute func to calculate the next execution time
                next_date = next_date_calc(time_list, [last_minute, last_hour, last_day, last_month])
            except Exception:
                sys_log_file = []
                next_date = next_date_calc(time_list)
            finally:
                if sys_log_file:
                    sys_log_file.close()

            # Echo the result
            print "\"" + job + "\"" + " job will be executed " + str(next_date)


def next_date_calc(cron_date, last_date=[]):
    """Calculate the date when job will be executed."""

    next_date = today  # Initial date
    not_now = False

    # Calculate date values one by one. In decreasing order. If '*' - stay the same and skip the block.
    if cron_date[3] != '*':  # Month
        next_month = []
        month_list = parse_list(cron_date[3], 'month')
        approp_list = filter(lambda x: (x >= today.month), sorted(month_list))

        for month in approp_list:
            next_month = month
            break

        # If next month is within this year, then just add it.
        if next_month:
            next_date += MonthDelta((next_month - today.month))
            if next_month != today.month:
                not_now = True
        # If not, then get the lowest number from month_list and go with it to next year
        else:
            next_date += MonthDelta((12 - today.month + month_list[0]))
            not_now = True

    if cron_date[2] != '*':  # Day
        next_day = []
        day_list = parse_list(cron_date[2], 'day')
        approp_list = filter(lambda x: (x >= today.day), sorted(day_list))

        for day in approp_list:
            next_day = day
            break

        # If not this month, then just get the lowest number from day_list with other the same values.
        if not_now:
            if day_list[0] < today.day:
                next_date = datetime(next_date.year, next_date.month, day_list[0],
                                     next_date.hour, next_date.minute, 0)
        elif next_day:
            next_date += timedelta(next_day - today.day)
            if next_day != today.day:
                not_now = True
        else:
            next_date += timedelta(calendar.monthrange(today.year, today.month)[1] - today.day + day_list[0])
            not_now = True

    if cron_date[1] != '*':  # Hour
        next_hour = []
        hour_list = parse_list(cron_date[1], 'hour')
        approp_list = filter(lambda x: (x >= today.hour), sorted(hour_list))

        for hour in approp_list:
            next_hour = hour
            break

        if not_now:
            if hour_list[0] < today.hour:
                next_date = datetime(next_date.year, next_date.month, next_date.day,
                                     hour_list[0], next_date.minute, 0)
        elif next_hour:
            next_date += timedelta(hours=next_hour - today.hour)
            if next_hour != today.hour:
                not_now = True
        else:
            next_date += timedelta(hours=24 - today.hour + hour_list[0])
            not_now = True

    if cron_date[0] != '*':  # Minute
        next_min = []
        min_list = parse_list(cron_date[0], 'minute')
        approp_list = filter(lambda x: (x >= today.minute), min_list)

        for min in approp_list:
            next_min = min
            break

        if not_now:
            next_date = datetime(next_date.year, next_date.month, next_date.day,
                                 next_date.hour, min_list[0], 0)

        elif next_min:
            next_date += timedelta(minutes=next_min - today.minute)
        else:
            next_date += timedelta(minutes=60 - today.minute + min_list[0])
    else:
        if not_now:
            next_date = datetime(next_date.year, next_date.month, next_date.day,
                                 next_date.hour, 0, 0)
        else:
            next_date += timedelta(minutes=1)

    return next_date


def parse_list(values, vtype):
    """Parse the input params to the list of values using cron rules."""

    value_list = []
    if vtype == 'month':
        first_relement = 1
        second_relement = 12
    elif vtype == 'day':
        first_relement = 1
        second_relement = 30
    elif vtype == 'hour':
        first_relement = 0
        second_relement = 23
    elif vtype == 'minute':
        first_relement = 0
        second_relement = 59
    else:
        return 'Wrong type designation.'

    # If '*/5'(for example), then return a list with 'every fifth'.
    if values.find('/') > -1 and values.find('*') > -1:
        value_list = range(first_relement, second_relement + 1, int(values.split('/')[1]))
    # If '3-9/3'(for example), then return a list with [3,6,9].
    elif values.find('/') > -1:
        value = values.split('/')[0]
        value_list = range(int(value.split('-')[0]), int(value.split('-')[1])+1, int(values.split('/')[1]))
    # If '1,2-4,6,9,10-12', then return a list with [1, 2, 3, 4, 6, 9, 10, 11, 12].
    else:
        for value in values.split(','):
            if value.find('-') > -1:
                for sgl_value in range(int(value.split('-')[0]), int(value.split('-')[1])+1):
                    value_list.append(sgl_value)
            else:
                value_list.append(int(value))

    return value_list


if __name__ == '__main__':
    crontab_processing()