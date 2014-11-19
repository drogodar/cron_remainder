#!/usr/bin/python2.7

# cron_remainder processes user's crontab file and prints the next execution time of jobs
# Copyright (C) 2014  Semen Pichugin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# My email: samret13@gmail.com

import re
import subprocess
from datetime import datetime, timedelta
from monthdelta import monthdelta
import calendar

today = datetime.today()
today = datetime(today.year, today.month, today.day, today.hour, today.minute)
weekday_names = {"MON": '1', "TUE": '2', "WED": '3', "THU": '4', "FRI": '5', "SAT": '6', "SUN": '7'}
month_names = {"JAN": '1', "FEB": '2', "MAR": '3', "APR": '4', "MAY": '5', "JUN": '6', "JUL": '7', "AUG": '8',
                   "SEP": '9', "OCT": '10', "NOV": '11', "DEC": '12'}
regex_pattern = "^(\d|\*|,|-|/|" + "|".join(weekday_names.keys()) + "|" + "|".join(month_names.keys()) + ")*$"


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
    else:
        return 'Crontab file has no lines.'

    # Compile RegEx for beauty
    p = re.compile(regex_pattern, re.IGNORECASE)
    job_found = False

    print 'Starting to search for appropriate lines...'

    # Split rows for five time elements and job.
    for cron_row in crontab_rows:
        row_elements = [k for k in cron_row.split(' ', 5)]

        # Filter rows through the RegEx
        time_list = [element for element in [row_elements[i] for i in range(len(row_elements) - 1)]
                     if re.search(p, element) and len(row_elements) == 6]

        # Check for a len and then we have only right rows with jobs
        if len(time_list) == 5:
            job = row_elements[5][:-1]
            next_date = today
            true_weekday = False
            job_found = True

            # Calc next date
            next_date = next_date_calc(time_list, next_date)

            # Check for day of week.
            while true_weekday is False:
                if next_date.isoweekday() in parse_list(time_list[4], 'weekday'):
                    true_weekday = True
                else:
                    next_date = datetime(next_date.year, next_date.month, next_date.day, 0, 0, 0) + timedelta(days=1)
                    next_date = next_date_calc(time_list, next_date)

            # Print the result
            print "\"" + job + "\"" + " job will be executed " + str(next_date)

    if job_found is False:
        return 'No appropriate lines have been found.'
    else:
        return 'Success!'


def next_date_calc(pattern, start_date):
    """Calculate the date when job will be executed."""

    next_date = start_date  # Initial date
    not_now = False

    # Calculate date values one by one. In decreasing order.

    # Month
    next_month = []
    month_list = parse_list(pattern[3], 'month')
    approp_list = filter(lambda x: (x >= start_date.month), sorted(month_list))

    if approp_list != []:
        next_month = approp_list[0]

    # If next month is within this year, then just add it.
    if next_month != []:
        next_date += monthdelta((next_month - start_date.month))
        if next_month != start_date.month:
            not_now = True
    # If not, then get the lowest number from month_list and go with it to next year
    else:
        next_date += monthdelta((12 - start_date.month + month_list[0]))
        not_now = True

    # Day
    next_day = []
    day_list = parse_list(pattern[2], 'day', [next_date.year, next_date.month])
    approp_list = filter(lambda x: (x >= start_date.day), sorted(day_list))

    if approp_list != []:
        next_day = approp_list[0]

    # If not this month, then just get the lowest number from day_list with other the same values.
    if not_now:
        if day_list[0] < start_date.day:
            next_date = datetime(next_date.year, next_date.month, day_list[0],
                                 next_date.hour, next_date.minute, 0)
    elif next_day != []:
        next_date += timedelta(next_day - start_date.day)
        if next_day != start_date.day:
            not_now = True
    else:
        next_date += timedelta(calendar.monthrange(start_date.year, start_date.month)[1] - start_date.day + day_list[0])
        not_now = True

    # Hour
    next_hour = []
    hour_list = parse_list(pattern[1], 'hour')
    approp_list = filter(lambda x: (x >= start_date.hour), sorted(hour_list))

    if approp_list != []:
        next_hour = approp_list[0]

    if not_now:
        if hour_list[0] < start_date.hour:
            next_date = datetime(next_date.year, next_date.month, next_date.day,
                                 hour_list[0], next_date.minute, 0)
    elif next_hour != []:
        next_date += timedelta(hours=next_hour - start_date.hour)
        if next_hour != start_date.hour:
            not_now = True
    else:
        next_date += timedelta(hours=24 - start_date.hour + hour_list[0])
        not_now = True

    # Minute
    next_min = []
    min_list = parse_list(pattern[0], 'minute')
    approp_list = filter(lambda x: (x >= start_date.minute), min_list)

    if approp_list != []:
        next_min = approp_list[0]

    if not_now:
        next_date = datetime(next_date.year, next_date.month, next_date.day,
                             next_date.hour, min_list[0], 0)

    elif next_min != []:
        next_date += timedelta(minutes=next_min - start_date.minute)
    else:
        next_date += timedelta(minutes=60 - start_date.minute + min_list[0])

    return next_date


def parse_list(entry_values, vtype, props=[]):
    """Parse the input params to the list of values using cron rules."""

    values = entry_values.upper()
    value_list = []

    if vtype == 'month':
        for month, num in month_names.items():
            values = values.replace(month, str(num))
        first_relement = 1
        second_relement = 12
    elif vtype == 'day':
        try:
            first_relement = 1
            second_relement = calendar.monthrange(props[0], props[1])[1]
        except IndexError:
            print 'Wrong props in the parse_list() for ' + vtype
            exit()
    elif vtype == 'hour':
        first_relement = 0
        second_relement = 23
    elif vtype == 'minute':
        first_relement = 0
        second_relement = 59
    elif vtype == 'weekday':
        for weekday, num in weekday_names.items():
            values = values.replace(weekday, str(num))
        first_relement = 1
        second_relement = 7
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
    if vtype == 'weekday' and value_list.count(0) > 0:
        value_list.remove(0)
        value_list.append(7)

    return list(set(value_list))


if __name__ == '__main__':
    print crontab_processing()