""" Tools for grading
"""

from os.path import exists
from io import StringIO
from collections import OrderedDict

import pytoml as toml

import pandas as pd


class Config:

    config_fname = 'gdconfig.toml'
    required_fields = ('log', 'year')

    def __init__(self):
        self._params = None

    @property
    def params(self):
        if self._params is None:
            self._params = self._read_config()
        return self._params

    def _read_config(self):
        fname = self.config_fname
        if not exists(fname):
            raise RuntimeError(
                f'Should be {fname} in current directory')
        with open(fname, 'rb') as fobj:
            config = toml.load(fobj)
        for field in self.required_fields:
            assert field in config, f'{fname} should have "{field}" field'
        assert exists(config['log']), \
                f'{config["log"]} from {fname} does not exist'
        return config

    @property
    def marking_log(self):
        return self.params['log']

    @property
    def year(self):
        return self.params['year']

    def student_fname(self):
        return f'students_{self.year}.csv'

    def get_students(self):
        if not exists(self.student_fname):
            raise RuntimeError('Run gdo-mkstable here')
        return pd.read_csv(self.student_fname)

    @property
    def scores(self):
        return get_scores(self.marking_log)

    @property
    def score_lines(self):
        return get_score_lines(*self.scores)


CONFIG = Config()


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
