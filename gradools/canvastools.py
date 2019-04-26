""" Tools for working with Canvas outputs
"""

from os.path import split as psplit
import re

import pandas as pd

_FNAME_RE = re.compile(r'([a-z\-_]+)(\d+)_')
_REQUIRED = ('Student', 'SIS User ID', 'SIS Login ID', 'Section')


class CanvasError(ValueError):
    """ Exception for violations of Canvas rules
    """


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
        raise CanvasError('Bad filename', name)
    names, number = match.groups()
    names = [_capitalize(n) for n in names.split('_')]
    if len(names) == 1:
        raise CanvasError('Should be names separated by -', name)
    return (names[0], ' '.join(names[1:]), number)


def _capitalize(name):
    if '-' in name:
        return '-'.join([_capitalize(n) for n in name.split('-')])
    return name.capitalize()


def check_unique_stid(filenames):
    """ Raise CanvasError unless `filenames` have unique student IDs
    """
    found_ids = {}
    for fname in filenames:
        name, _, stid = fname2key(fname)
        if stid in found_ids:
            raise CanvasError(
                f'{fname} has same student ID {stid} as '
                f'{found_ids[stid]}')
        found_ids[stid] = fname
