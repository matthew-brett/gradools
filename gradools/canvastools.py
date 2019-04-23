""" Tools for working with Canvas outputs
"""

from os.path import split as psplit
import re

import pandas as pd

_FNAME_RE = re.compile(r'([a-z\-_]+)(\d+)_')
_REQUIRED = ('Student', 'SIS User ID', 'SIS Login ID', 'Section')


def to_minimal_df(full_gradebook):
    """ Return template dataframe from full gradebook
    """
    df = pd.read_csv(full_gradebook)
    # Some strange unicode characters in 'Student' with a default read
    df.rename(columns={df.columns[0]: 'Student'}, inplace=True)
    df = df[list(_REQUIRED)]
    df = df.dropna(subset = ['SIS User ID'])
    df['SIS User ID'] = df['SIS User ID'].astype(int)
    return df


def fname2key(fname):
    """ Return tuple key from Canvas output filename
    """
    path, name = psplit(fname)
    match = _FNAME_RE.match(name)
    if match is None:
        raise ValueError('Bad filename', name)
    names, number = match.groups()
    names = [_capitalize(n) for n in names.split('_')]
    return (names[0], ' '.join(names[1:]), number)


def _capitalize(name):
    if '-' in name:
        return '-'.join([_capitalize(n) for n in name.split('-')])
    return name.capitalize()
