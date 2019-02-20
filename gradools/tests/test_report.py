""" Test report module
"""

from os.path import join as pjoin, dirname

from gradools.report import read_old_totals


DATA_DIR = pjoin(dirname(__file__), 'data')


def test_read_old_totals():
    totals = read_old_totals(pjoin(DATA_DIR, 'marks_2017.txt'))
    assert list(totals) == ['mbr312', 'vrr110', 'lxl101']
    assert list(totals.values()) == [43.5, 90.0, 80.5]
