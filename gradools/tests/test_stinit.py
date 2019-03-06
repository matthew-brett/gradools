""" Test student initialization
"""

from os.path import join as pjoin, dirname
from collections import OrderedDict

import numpy as np
import pandas as pd

from gradools.mkstable import to_minimal_df
from gradools.stinit import get_init


DATA_DIR = pjoin(dirname(__file__), 'data')

class C:
    def get_students(self):
        return to_minimal_df(pjoin(DATA_DIR, 'full_gb_example.csv'))

    score_lines = '* one: 1\n* two: 2'


_config = C()


def test_get_init():
    res = get_init('mb312', _config)
    exp = """\
## mb312

* one: 1
* two: 2

Total: 

Matthew Brett

"""
    assert res == exp
