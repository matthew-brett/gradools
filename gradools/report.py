""" Report marks
"""
from os.path import exists
from collections import OrderedDict

import numpy as np
import pandas as pd

from .mconfig import CONFIG
from .check import checked_totals

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def get_current(config=CONFIG):
    totals, msg = checked_totals(config.marking_log)
    if msg:
        raise RuntimeError(f'Check returns message "{msg}"')
    fudge = config.get('fudges', {}).get(config.year, 0)
    processed = totals.copy()
    for key, value in totals.items():
        processed[key] = min([value + fudge, 100])
    return processed


def read_old_totals(fname):
    # Old file format
    with open(fname, 'rt') as fobj:
        mark_text = fobj.read()
    marks = OrderedDict()
    for line in mark_text.splitlines():
        login, value = line.split(':')
        login, value = login.strip(), float(value)
        value = 100 if value > 100 else value
        marks[login] = value
    return marks


def report_year(marks, year):
    values = list(marks.values())
    print(f'Marks for {year}')
    print(f'---------------')
    print(f'n: {len(values)}')
    print(f'Mean: {np.mean(values):0.2f}')
    print(f'Stdev: {np.std(values, ddof=1):0.2f}')
    failed = [login for login, mark in marks.items() if mark < 50]
    if failed:
        print('Failed:')
        print('\n'.join(failed))
    plt.hist(values)
    plt.savefig(f'mark_histogram_{year}.png')
    plt.close()
    print()


def read_totals(year):
    root = f'marks_{year}'
    if exists(root + '.txt'):
        return read_old_totals(root + '.txt')
    if not exists(root + '.csv'):
        return None
    df = pd.read_csv(root + '.csv')
    return OrderedDict(zip(df['SIS Login ID'], df.iloc[:, -1]))


def main(config=CONFIG):
    year = config.year
    iyear = int(year)
    iym1 = iyear - 1
    this_year = get_current()
    report_year(this_year, iyear)
    last_year = read_totals(str(iym1))
    if last_year is None:
        print(f'No data for {iym1}')
    else:
        report_year(last_year, iym1)
    students = config.get_students()
    assignment = config['assignment']
    students[assignment] = np.nan

    for login, mark in this_year.items():
        students.at[students['SIS Login ID'] == login, assignment] = mark
    students = students.dropna()

    # Check
    for login, mark in this_year.items():
        row = students[students['SIS Login ID'] == login]
        assert row[assignment].values == mark

    students.to_csv(config.marks_fname, index=False)
