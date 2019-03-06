""" Tests for mkstable module
"""

from os.path import join as pjoin, dirname
from collections import OrderedDict

import numpy as np
import pandas as pd

from gradools.mkstable import to_minimal_df


DATA_DIR = pjoin(dirname(__file__), 'data')


def test_to_minimal_df():
    df = to_minimal_df(pjoin(DATA_DIR, 'full_gb_example.csv'))
    data = OrderedDict((('Student', ['Matthew Brett', 'Martin Brett']),
                        ('SIS User ID', [9876543, 1357908]),
                        ('SIS Login ID', ['mb312', 'mb110']),
                        ('Section', ['A Module Title'] * 2)))
    exp_df = pd.DataFrame(data)
    exp_df.index = df.index
    assert np.all(df == exp_df)
