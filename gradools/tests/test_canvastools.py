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
    ndt = np.dtype
    csv_path = pjoin(DATA_DIR, 'full_gb_example.csv')
    df = to_minimal_df(csv_path)
    data = OrderedDict((('Student', ['Matthew Brett', 'Martin Brett']),
                        ('SIS User ID', [9876543, 1357908]),
                        ('SIS Login ID', ['mb312', 'mb110']),
                        ('Section', ['A Module Title'] * 2)))
    exp_df = pd.DataFrame(data)
    assert np.all(df == exp_df)
    assert df['SIS User ID'].dtype == ndt(int)
    # Can also pass DataFrame
    full_df = pd.read_csv(csv_path)
    df2 = to_minimal_df(full_df)
    assert np.all(df2 == exp_df)
    # Can pass field names
    df_less = to_minimal_df(full_df, ('SIS User ID', 'Student'))
    data = OrderedDict((
        ('SIS User ID', [9876543, 1357908]),
        ('Student', ['Matthew Brett', 'Martin Brett']),
    ))
    assert np.all(df_less == pd.DataFrame(data))
    assert df_less['SIS User ID'].dtype == ndt(int)
    df_less2 = to_minimal_df(full_df, ('Section', 'SIS Login ID'))
    data = OrderedDict((
        ('Section', ['A Module Title'] * 2),
        ('SIS Login ID', ['mb312', 'mb110']),
    ))
    assert np.all(df_less2 == pd.DataFrame(data))
    # Can pass data types for fields.
    df_1 = to_minimal_df(full_df, ('SIS User ID', 'ID', 'Student'))
    data = OrderedDict((
        ('SIS User ID', [9876543, 1357908]),
        ('ID', [12345, 567876]),
        ('Student', ['Matthew Brett', 'Martin Brett']),
    ))
    assert np.all(df_1 == pd.DataFrame(data))
    assert df_1.dtypes.equals(pd.Series(
        {'SIS User ID': ndt(int), 'ID': ndt(float), 'Student': ndt(object)}))
    df_2 = to_minimal_df(full_df, ('SIS User ID', 'ID', 'Student'),
                         {'ID': int})
    assert np.all(df_2 == pd.DataFrame(data))
    assert df_2.dtypes.equals(pd.Series(
        {'SIS User ID': ndt(int), 'ID': ndt(int), 'Student': ndt(object)}))
    df_3 = to_minimal_df(full_df, ('SIS User ID', 'ID', 'Student'),
                         {'SIS User ID': object, 'ID': np.dtype(int)})
    assert np.all(df_3 == pd.DataFrame(data))
    assert df_3.dtypes.equals(pd.Series(
        {'SIS User ID': ndt(object), 'ID': ndt(int), 'Student': ndt(object)}))
    # field for dtype not in fields - error.
    with pytest.raises(ValueError):
        to_minimal_df(full_df, ('SIS User ID', 'ID', 'Student'),
                      {'Foo': object})


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
