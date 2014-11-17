#!/usr/bin/python

import re
import subprocess
from datetime import datetime, timedelta
from monthdelta import monthdelta
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

    # Compile RegEx for beauty TODO: Non-Standard Characters - '?', 'L', 'M', '#'
    p = re.compile('''
    ^                # beginning of the line
    (\d|\*|,|-|/)*   # any number of digits, asterisk, commas, '-' and '/'
    $                # end of the line
    ''', re.VERBOSE)

    month_names = {"Jan": '1', "Feb": '2', "Mar": '3', "Apr": '4', "May": '5', "Jun": '6', "Jul": '7', "Aug": '8',
                   "Sep": '9', "Oct": '10', "Nov": '11', "Dec": '12'}

    # Split rows for five time elements and job.
    for cron_row in crontab_rows:
        row_elements = [k for k in cron_row.split(' ', 5)]
        time_list = [element for element in [row_elements[i] for i in range(len(row_elements) - 1)]
                     if re.search(p, element) and len(row_elements) == 6]

        # Filter rows through the RegEx and check for len.
        # After that we have only "right" rows with jobs
        if len(time_list) == 5:
            job = row_elements[5][:-1]
            next_date = today
            true_weekday = False
            cnt = 0

            while true_weekday is False:
                # Try to find previous job's executions.
                try:
                    sys_log_file = open('/var/log/cron', 'r')  # Specify here cron log destination for your distr.
                                                               # Not required for current version.
                    log_lines = [k for k in sys_log_file.readlines()]

                    # Find and parse the last execution time.
                    for log_line in log_lines:
                        if log_line.find(job) > -1:
                            last_exec_date = log_line[:12]

                    last_minute = last_exec_date.split('  ', )[1].split(' ')[1].split(':')[1]
                    last_hour = last_exec_date.split('  ', )[1].split(' ')[1].split(':')[0]
                    last_day = last_exec_date.split('  ', )[1].split(' ')[0]
                    last_month = month_names[last_exec_date.split('  ')[0]]

                    # Execute func to calculate the next execution time.
                    next_date = next_date_calc(time_list, next_date, [last_minute, last_hour, last_day, last_month])
                except Exception:
                    sys_log_file = []
                    next_date = next_date_calc(time_list, next_date)
                finally:
                    if sys_log_file:
                        sys_log_file.close()

                # Check for day of week.
                if next_date.weekday() in parse_list(time_list[4], 'weekday'):
                    true_weekday = True
                else:
                    next_date = next_date_calc(time_list, next_date + timedelta(days=1))

                cnt += 1
                if cnt == 5:
                    true_weekday = True

            # Print the result
            print "\"" + job + "\"" + " job will be executed " + str(next_date)


def next_date_calc(pattern, start_date, last_date=[]):
    """Calculate the date when job will be executed."""

    next_date = start_date  # Initial date
    not_now = False

    # Calculate date values one by one. In decreasing order.

    next_month = []
    month_list = parse_list(pattern[3], 'month')
    approp_list = filter(lambda x: (x >= start_date.month), sorted(month_list))

    for month in approp_list:
        next_month = month
        break

    # If next month is within this year, then just add it.
    if next_month:
        next_date += monthdelta((next_month - start_date.month))
        if next_month != start_date.month:
            not_now = True
    # If not, then get the lowest number from month_list and go with it to next year
    else:
        next_date += monthdelta((12 - start_date.month + month_list[0]))
        not_now = True

    next_day = []
    day_list = parse_list(pattern[2], 'day')
    approp_list = filter(lambda x: (x >= start_date.day), sorted(day_list))

    for day in approp_list:
        next_day = day
        break

    # If not this month, then just get the lowest number from day_list with other the same values.
    if not_now:
        if day_list[0] < start_date.day:
            next_date = datetime(next_date.year, next_date.month, day_list[0],
                                 next_date.hour, next_date.minute, 0)
    elif next_day:
        next_date += timedelta(next_day - start_date.day)
        if next_day != start_date.day:
            not_now = True
    else:
        next_date += timedelta(calendar.monthrange(start_date.year, start_date.month)[1] - start_date.day + day_list[0])
        not_now = True

    next_hour = []
    hour_list = parse_list(pattern[1], 'hour')
    approp_list = filter(lambda x: (x >= start_date.hour), sorted(hour_list))

    for hour in approp_list:
        next_hour = hour
        break

    if not_now:
        if hour_list[0] < start_date.hour:
            next_date = datetime(next_date.year, next_date.month, next_date.day,
                                 hour_list[0], next_date.minute, 0)
    elif next_hour:
        next_date += timedelta(hours=next_hour - start_date.hour)
        if next_hour != start_date.hour:
            not_now = True
    else:
        next_date += timedelta(hours=24 - start_date.hour + hour_list[0])
        not_now = True

    next_min = []
    min_list = parse_list(pattern[0], 'minute')
    approp_list = filter(lambda x: (x >= start_date.minute), min_list)

    for min in approp_list:
        next_min = min
        break

    if not_now:
        next_date = datetime(next_date.year, next_date.month, next_date.day,
                             next_date.hour, min_list[0], 0)

    elif next_min:
        next_date += timedelta(minutes=next_min - start_date.minute)
    else:
        next_date += timedelta(minutes=60 - start_date.minute + min_list[0])

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
    elif vtype == 'weekday':
        first_relement = 0
        second_relement = 6
    else:
        return 'Wrong type designation.'

    if values == '*':
        return range(first_relement, second_relement+1)

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

    # In cron '0' and '7' is for Sunday, but in Python there is no '7' for Sunday, so replace it to '0'.
    if vtype == 'weekday' and value_list.count(7) > 0:
        value_list.remove(7)
        value_list.insert(0, 0)

    return list(set(value_list))


if __name__ == '__main__':
    crontab_processing()
