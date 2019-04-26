""" Test canvastools module
"""

from os.path import join as pjoin, dirname, abspath
from collections import OrderedDict

import numpy as np
import pandas as pd

from gradools.canvastools import to_minimal_df, fname2key, CanvasError

import pytest


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


def test_fname2key():
    assert (fname2key('last_first139727_anything')
            == ('Last', 'First', '139727'))
    with pytest.raises(CanvasError):
        fname2key('last_first139727anything')
    with pytest.raises(CanvasError):
        fname2key('lastfirst139727_anything')
    assert (fname2key(
        'last_first139727_question_815185_4738509_First Last_bio240_r_2.Rmd'
    ) == ('Last', 'First', '139727'))
    fname = 'brett_matthew124954_question_815185_4781127_an_exercise.Rmd'
    assert (fname2key(fname) == ('Brett', 'Matthew', '124954'))
    assert (fname2key(abspath(fname)) == ('Brett', 'Matthew', '124954'))
    assert (fname2key(
        'hoffman_philip_seymour111617_question_815185_4772418_an_exercise '
        'Philip Hoffman.Rmd') == ('Hoffman', 'Philip Seymour', '111617'))
    assert (fname2key(
        'cholmondley-warner_james124011_question_815185_4782899_Some Text.Rmd'
    ) == ('Cholmondley-Warner', 'James', '124011'))
