""" Report marks
"""

import numpy as np
import matplotlib.pyplot as plt

from .mconfig import CONFIG, read_totals, get_students
from .check import checked_totals


YEAR = CONFIG['year']
FUDGES = CONFIG.get('fudges', {})


def get_current():
    totals, msg = checked_totals(CONFIG['log'])
    if msg:
        raise RuntimeError(f'Check returns message "{msg}"')
    fudge = FUDGES.get(YEAR, 0)
    processed = totals.copy()
    for key, value in totals.items():
        processed[key] = min([value + fudge, 100])
    return processed


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


def main():
    iyear = int(YEAR)
    this_year = get_current()
    last_year = read_totals(f'marks_{iyear-1}.txt')
    report_year(this_year, iyear)
    report_year(last_year, iyear - 1)

    students = get_students()
    assignment = CONFIG['assignment']

    for login, mark in this_year.items():
        students.at[students['SIS Login ID'] == login, assignment] = mark
    students = students.dropna()

    # Check
    for login, mark in this_year.items():
        row = students[students['SIS Login ID'] == login]
        assert row[assignment].values == mark

    students.to_csv(f'marks_{YEAR}.csv', index=False)
