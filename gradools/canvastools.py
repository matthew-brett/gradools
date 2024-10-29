""" Tools for working with Canvas outputs
"""

from os.path import split as psplit
import regex

import numpy as np
import pandas as pd

# Canvas filename.  p{Ll} is lower case letter in Unicode, specific to regex
# package. \u0308 is a combining diaeresis, as in Brontë.
# https://www.fileformat.info/info/unicode/char/0308/index.htm
_FNAME_RE = regex.compile(
    r'''
    (?P<name>[\p{Ll}\u0308\-_]+)
    (?:LATE_)?
    (?P<id_no>\d+)_
    ''',
    flags=regex.VERBOSE)

# Column name, dtypes required for upload to Canvas.
# None means - dtype not constrained.
REQUIRED_COLS = {'Student': None,
                 'SIS User ID': np.dtype(int),
                 'SIS Login ID': None,
                 'Section': None,
                }

# Primary key for student in tables.
CANVAS_ID_COL = 'SIS User ID'

# For back compatibility
REQUIRED_COL_NAMES = tuple(REQUIRED_COLS)
_REQUIRED = REQUIRED_COL_NAMES


class CanvasError(ValueError):
    """ Exception for violations of Canvas rules
    """


def to_minimal_df(full_gradebook, fields=None, dtypes=None):
    """ Return template dataframe from full gradebook

    Parameters
    ----------
    full_gradebook : str or DataFrame
        Filename of full gradebook as downloaded from Canvas, or DataFrame
        loaded from same.
    fields : None or sequence, optional
        List of fields to copy, or None (default).  If None, results in minimal
        set of fields to upload to Canvas (keys in ``REQUIRED_COLS``
        dictionary).
    dtypes : None or dict, optional
        Dictionary of field: dtype key: value or None (default).  None gives
        the default mappings from the ``REQUIRED_COLS`` dictionary.

    Returns
    -------
    mini_df : DataFrame
        DataFrame containing rows (students) from `full_gradebook`, and fields
        specified in `fields`.

    Raises
    ------
    ValueError
        If `dtypes` contains field names not in `fields`.
    """
    fields = tuple(REQUIRED_COLS) if fields is None else fields
    dts = {n: d for n, d in REQUIRED_COLS.items() if d and (n in fields)}
    if dtypes:
        bad_cols = set(dtypes).difference(fields)
        if bad_cols:
            raise ValueError('Odd names "{}" in dtypes {}'.format(
                ', '.join(bad_cols), dtypes))
        dts.update({n: np.dtype(d) for n, d in dtypes.items()})
    df = (full_gradebook if hasattr(full_gradebook, 'columns') else
          pd.read_csv(full_gradebook))
    # Some strange unicode characters in 'Student' with a default read, at some
    # point.  No longer seems to be true.  Pandas version?
    assert df.columns[0].endswith('Student')
    df = df.rename(columns={df.columns[0]: 'Student'})
    # Drop invalid rows, with NA for SIS User ID.  These include first one or
    # two rows, and Test Student at end.  Restrict to requested columns.
    df = df.loc[~pd.isna(df[CANVAS_ID_COL]), list(fields)]
    # Set dtypes
    for col, dt in dts.items():
        df[col] = df[col].astype(dt)
    # Reset to default integer index.
    return df.reset_index(drop=True)


def fname2key(fname):
    """ Return tuple key from Canvas output filename
    """
    path, name = psplit(fname)
    match = _FNAME_RE.match(name)
    if match is None:
        raise CanvasError(
            f'Filename "{name}" should be of form name, optional "LATE_", '
            'followed by the student ID number, e.g '
            '"brettmatthew_LATE_124_something_else.zip"')
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
