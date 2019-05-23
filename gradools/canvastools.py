""" Tools for working with Canvas outputs
"""

from os.path import split as psplit
import re

import pandas as pd

_FNAME_RE = re.compile(r'([a-z\-_]+)(\d+)_')

# Columns required for upload to Canvas
_REQUIRED = ('Student', 'SIS User ID', 'SIS Login ID', 'Section')

# Columns from list above that must be integers
_TO_INT_COLS = ('SIS User ID',)


class CanvasError(ValueError):
    """ Exception for violations of Canvas rules
    """


def to_minimal_df(full_gradebook, fields=None):
    """ Return template dataframe from full gradebook

    Parameters
    ----------
    full_gradebook : str or DataFrame
        Filename of full gradebook as downloaded from Canvas, or DataFrame
        loaded from same.
    fields : None or sequence, optional
        List of fields to copy, or None (default).  If None, results in minimal
        set of fields to upload to Canvas.

    Returns
    -------
    mini_df : DataFrame
        DataFrame containing rows (students) from `full_gradebook`, and fields
        specified in `fields`.
    """
    fields = _REQUIRED if fields is None else fields
    df = (full_gradebook if hasattr(full_gradebook, 'columns') else
          pd.read_csv(full_gradebook))
    # Some strange unicode characters in 'Student' with a default read
    df.rename(columns={df.columns[0]: 'Student'}, inplace=True)
    # First row is Points Possible, with NaN for user id
    df = df.dropna(subset = ['SIS User ID'])
    df = df[list(fields)]
    for col in _TO_INT_COLS:
        if col not in df:
            continue
        df[col] = df[col].astype(int)
    # Reset to default integer index
    return df.reset_index(drop=True)


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
