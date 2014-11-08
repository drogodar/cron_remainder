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
    (\d|\*|,)*      # any number of digits, asterisks, comma TODO: ranges, divisions, pluses, ?, 'L', 'M'
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
                log_lines = [k for k in sys_log_file.readlines()]

                # Find and parse the last execution time
                for log_line in log_lines:
                    if log_line.find(job) > 0:
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

    # If last execution time was found then first thread,
    # else second TODO: write first thread, modify second(*/5, ranges, etc.)

    #if last_date:
    #    return next_date
    #else:
    #    return next_date

    # Calculate date values one by one. In decreasing order. If '*' - stay the same and skip the block.
    # 1. Get all hours from row, to_init them and then sort;
    # 2. Filter the previous action result and get the first item
    if cron_date[3] != '*':  # Month
        next_month = []
        month_list = sorted(map(lambda x: int(x), cron_date[3].split(',')))
        approp_list = filter(lambda x: (x >= today.month), month_list)

        for month in approp_list:
            next_month = month
            break

        # 3. If next month is within this year, then just add it.
        if next_month:
            next_date += MonthDelta((next_month - today.month))
            if next_month != today.month:
                not_now = True
        # 4. If not, then get the lowest number from month_list and go with it to next year
        else:
            next_date += MonthDelta((12 - today.month + month_list[0]))
            not_now = True

    if cron_date[2] != '*':  # Day
        next_day = []
        day_list = sorted(map(lambda x: int(x), cron_date[2].split(',')))
        approp_list = filter(lambda x: (x >= today.day), day_list)

        for day in approp_list:
            next_day = day
            break

        # If not if this month, then just get the lowest number from day_list with other the same values.
        if not_now:
            if day_list[0] < today.day:
                next_date += timedelta(calendar.monthrange(today.year, today.month)[1] - today.day + day_list[0])
                not_now = True
            else:
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
        hour_list = sorted(map(lambda x: int(x), cron_date[1].split(',')))
        approp_list = filter(lambda x: (x >= today.hour), hour_list)

        for hour in approp_list:
            next_hour = hour
            break

        if not_now:
            if hour_list[0] < today.hour:
                next_date += timedelta(hours=24 - today.hour + hour_list[0])
                not_now = True
            else:
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
        min_list = sorted(map(lambda x: int(x), cron_date[0].split(',')))
        approp_list = filter(lambda x: (x >= today.minute), min_list)

        for min in approp_list:
            next_min = min
            break

        if not_now:
            if min_list[0] < today.minute:
                next_date += timedelta(minutes=24 - today.minute + min_list[0])
            else:
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


if __name__ == '__main__':
    crontab_processing()