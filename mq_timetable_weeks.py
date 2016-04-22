#!/usr/bin/env python

import arrow
import getpass
import json
import sys
from mq_timetable import MQeStudentSession, DAYS, TZ, get_selected_session

midsem_start = arrow.Arrow(2016, 4, 10, tzinfo=TZ)
midsem_end = midsem_start.replace(weeks=+2)


def tupleise_24h(t):
    hour, minute = map(int, t.split(':'))
    return hour, minute


def main():
    session = MQeStudentSession()
    sys.stderr.write('Student ID: ')
    session.login(input(), getpass.getpass())
    study_period_code, study_period_name = get_selected_session(session.get_timetable_page())
    start_end_arws = session.get_start_end_arrows()

    first_class = min(a for a, _ in start_end_arws.values())
    last_class = max(b for _, b in start_end_arws.values())

    week_start = first_class
    now = arrow.get()
    if week_start < now:
        week_start = now.floor('week')

    all_classes = process(session, study_period_code, week_start, last_class)
    json.dump({'session_name': study_period_name, 'classes': all_classes}, sys.stdout)


def process(session, study_period_code, week_start, last_class):
    all_classes = []

    while week_start < last_class:
        weektable = session.get_timetable_week(study_period_code, week_start)

        for isoweekdaym1, day in enumerate(DAYS):
            classes = weektable[day]

            for cls in reversed(classes):
                start_h, start_m = tupleise_24h(cls['start'])
                end_h, end_m = tupleise_24h(cls['end'])
                this_start = week_start.replace(days=+isoweekdaym1, hour=start_h, minute=start_m)
                this_end = week_start.replace(days=+isoweekdaym1, hour=start_h, minute=start_m)

                all_classes.append({
                    'subject': cls['subject'],
                    'what': cls['what'],
                    'where': cls['where'],
                    'start': this_start.format(),
                    'end': this_end.format(),
                })

        week_start = week_start.replace(weeks=+1)

    return all_classes