""" Tools for grading
"""

from os.path import sep as psep, basename, exists, join as pjoin
from io import StringIO

import pytoml as toml

from collections import OrderedDict

import numpy as np


def read_config():
    config_fname = 'gdconfig.toml'
    if not exists(config_fname):
        raise RuntimeError(
            f'Should be {config_fname} in current directory')
    with open(config_fname, 'rb') as fobj:
        config = toml.load(fobj)
    assert 'log' in config, f'{config_fname} should have "log" field'
    assert 'year' in config, f'{config_fname} should have "year" field'
    assert exists(config['log']), \
            f'{config["log"]} from {config_fname} does not exist'
    return config


CONFIG = read_config()
MARKING_LOG = CONFIG['log']
STUDENT_FNAME = f'students_{CONFIG["year"]}.csv'


def get_students():
    if not exists(STUDENT_FNAME):
        raise RuntimeError('Run gdo-mkstable here')
    import pandas as pd
    return pd.read_csv(STUDENT_FNAME)


def make_runs(params, loc_params):
    n_runs, task_name = params['n_runs'], params['task_name']
    runs = OrderedDict()
    fmt_mid = ('{sep}{sub_part}{sep}func'
                '{sep}{sub_part}_task-' + task_name)
    fmt_mid += '' if n_runs == 1 else '_run-{run_no:02d}'
    new_data_loc = loc_params['new_data_location']
    old_data_loc = loc_params['old_data_location']
    for sub_no in params['sub_nos']:
        for run_no in range(1, n_runs + 1):
            sub_part = 'sub-{sub_no:02d}'.format(sub_no=sub_no)
            mid_part = fmt_mid.format(sub_part=sub_part,
                                      run_no=run_no,
                                      sep=psep)
            fname = old_data_loc + mid_part + '_bold'
            event_files = []
            for condition_name in params['conditions']:
                ev_suffix = ('{mid_part}_label-{cond_name}.txt'.
                             format(mid_part=mid_part,
                                    cond_name=condition_name))
                ev_fname = new_data_loc + ev_suffix
                if exists(ev_fname):
                    event_files.append(basename(ev_fname))
            structural = ('{data_root}{sep}{sub_part}{sep}'
                          'anat{sep}{sub_part}_T1w.nii.gz').format(
                              data_root=new_data_loc,
                              sub_part=sub_part,
                              sep=psep)
            runs[basename(fname)] = dict(
                event_files=event_files,
                structural=structural if exists(structural) else None)
    return runs


def _read_text_file(fname):
    vals = []
    with open(fname, 'rt') as fobj:
        for line in fobj:
            vals.append(float(line.split('\t')[1]))
    return np.array(vals)


def print_year():
    print(CONFIG['year'])


def read_totals(fname):
    with open(fname, 'rt') as fobj:
        mark_text = fobj.read()
    marks = OrderedDict()
    for line in mark_text.splitlines():
        login, value = line.split(':')
        login, value = login.strip(), float(value)
        value = 100 if value > 100 else value
        marks[login] = value
    return marks


def test_read_totals():
    totals = read_totals('marks_2018.txt')
    keys = list(totals)
    assert keys[0] == 'arn872'
    assert totals[keys[0]] == 97.5
    assert keys[-1] == 'zxi820'
    assert totals[keys[-1]] == 36.0
    totals = read_totals('marks_2017.txt')


def demeaned_col(df, name):
    vals = df[name].values
    return vals - np.mean(vals)


def get_scores(fileish):
    if hasattr(fileish, 'read'):
        contents = fileish.read()
    else:
        with open(fileish, 'rt') as fobj:
            contents = fobj.read()
    lines = contents.splitlines()
    state = 'searching'
    o_scores = OrderedDict()
    e_scores = OrderedDict()
    for i, line in enumerate(lines):
        line = line.strip()
        if line == '':
            continue
        if state == 'searching':
            if line == 'Ordinary maxima:':
                state = 'ordinary-scores'
        elif state == 'ordinary-scores':
            if line == 'Extra maxima:':
                state = 'extra-scores'
                continue
            elif line.startswith('Total'):
                break
            key, value = proc_line(line)
            o_scores[key] = float(value)
        elif state == 'extra-scores':
            if line.startswith('Total'):
                break
            key, value = proc_line(line)
            e_scores[key] = float(value)
    return o_scores, e_scores


def proc_line(line):
    if not line.startswith('*'):
        raise ValueError('Invalid list element')
    return [v.strip() for v in line[1:].split(':')]


def get_score_lines(o_scores, e_scores):
    lines = [f'* {k}: {v}' for k, v in o_scores.items()]
    if e_scores:
        lines.append('')
        lines += [f'* {k}: {v}' for k, v in e_scores.items()]
    return '\n'.join(lines) + '\n'


def test_get_scores():
    fobj = StringIO()
    o, e = get_scores(fobj)
    assert o == {}
    assert e == {}
    fobj = StringIO("""

* score_1 : 1
""")
    o, e = get_scores(fobj)
    assert o == {}
    assert e == {}
    fobj = StringIO("""

Ordinary maxima:
* score_1 : 1
""")
    o, e = get_scores(fobj)
    assert o == dict(score_1 = 1)
    assert e == {}
    fobj = StringIO("""

Ordinary maxima:
*score_1 : 1


Total: 1
""")
    o, e = get_scores(fobj)
    assert o == dict(score_1 = 1)
    assert e == {}
    fobj.seek(0)
    assert get_score_lines(o, e) == '* score_1: 1.0\n'
    fobj = StringIO("""

Ordinary maxima:
* score_1 : 1

Extra maxima:
* score_10: 2.5

Total: 3.5
""")
    o, e = get_scores(fobj)
    assert o == dict(score_1 = 1)
    assert e == dict(score_10=2.5)
    fobj.seek(0)
    assert (get_score_lines(o, e) ==
            '* score_1: 1.0\n\n* score_10: 2.5\n')
    fobj = StringIO("""
Ordinary maxima:
*  score_1 : 1
*another_score: 2

Extra maxima:

*score_10: 2.5
*    extra_score: 5

Total:
""")
    o, e = get_scores(fobj)
    assert o == OrderedDict((('score_1', 1), ('another_score', 2)))
    assert e == OrderedDict((('score_10', 2.5), ('extra_score', 5)))
    fobj.seek(0)
    assert (get_score_lines(o, e) ==
            '* score_1: 1.0\n* another_score: 2.0\n\n'
            '* score_10: 2.5\n* extra_score: 5.0\n')


O_SCORES, E_SCORES = get_scores(MARKING_LOG)
SCORE_LINES = get_score_lines(O_SCORES, E_SCORES)
