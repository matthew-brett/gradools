""" Tools for working with Canvas outputs
"""

from os.path import split as psplit
import regex

import numpy as np
import pandas as pd

# Canvas filename.  p{Ll} is lower case letter in Unicode, specific to regex
# package. \u0308 is a combining diaeresis, as in Brontë.
# https://www.fileformat.info/info/unicode/char/0308/index.htm
_FNAME_RE = regex.compile(r'([\p{Ll}\u0308\-_]+)(?:LATE_)?(\d+)_')

# Columns required for upload to Canvas
REQUIRED_COL_NAMES = ('Student', 'SIS User ID', 'SIS Login ID', 'Section')

# For back compatibility
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
        set of fields to upload to Canvas.
    dtypes : None or sequence, optional
        Dictionary of field: dtype key: value or None (default).  Unless
        overridden by specific entry in `dtypes`, set 'SIS User ID' to int
        dtype.

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
    sis_id = 'SIS User ID'
    fields = REQUIRED_COL_NAMES if fields is None else fields
    dtypes = {} if dtypes is None else dtypes
    if sis_id in fields and sis_id not in dtypes:
        dtypes[sis_id] = np.dtype(int)
    missing_dtype_names = set(dtypes).difference(fields)
    if missing_dtype_names:
        raise ValueError('"dtypes" keys %s not in "fields"' %
                         (missing_dtype_names,))
    df = (full_gradebook if hasattr(full_gradebook, 'columns') else
          pd.read_csv(full_gradebook))
    # Some strange unicode characters in 'Student' with a default read, at some
    # point.  No longer seems to be true.  Pandas version?
    assert df.columns[0].endswith('Student')
    df.rename(columns={df.columns[0]: 'Student'}, inplace=True)
    # Drop invalid rows, with NA for SIS User ID.  These include first one or
    # two rows, and Test Student at end.
    df = df[~pd.isna(df[sis_id])]
    # Restrict to requested columns.
    df = df.loc[:, list(fields)]
    # Set dtypes
    for col, dt in dtypes.items():
        df[col] = df[col].astype(dt)
    # Reset to default integer index.
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
