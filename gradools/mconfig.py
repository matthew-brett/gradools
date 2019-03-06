""" Tools for grading
"""

from os.path import exists, join as pjoin
from collections import OrderedDict

import pytoml as toml

import pandas as pd


class ConfigError(RuntimeError):
    pass


class Config:

    config_fname = 'gdconfig.toml'
    required_fields = ('year',)
    default_log = 'marking_log.md'

    def __init__(self):
        self._params = None

    def __getitem__(self, key):
        return self.params[key]

    def __contains__(self, key):
        return key in self.params

    def get(self, key, *args, **kwargs):
        return self.params.get(key, *args, **kwargs)

    @property
    def params(self):
        if self._params is None:
            self._params = self._read_config()
        return self._params

    def _read_config(self):
        fname = self.config_fname
        if not exists(fname):
            raise ConfigError(
                f'Should be {fname} in current directory')
        with open(fname, 'rb') as fobj:
            config = toml.load(fobj)
        for field in self.required_fields:
            if not field in config:
                raise ConfigError(f'{fname} should have "{field}" field')
        return config

    @property
    def marking_log(self):
        fn = self.get('log', self.default_log)
        if not exists(fn):
            raise ConfigError(f'Log {fn} does not exist')
        return fn

    @property
    def year(self):
        return self.params['year']

    @property
    def student_fname(self):
        return f'students_{self.year}.csv'

    @property
    def marks_fname(self):
        return f'marks_{self.year}.csv'

    @property
    def nb_template(self):
        template = self.get('notebooks', {}).get('template')
        if template is None:
            return None
        return pjoin(*template.split('/'))

    def get_students(self):
        if not exists(self.student_fname):
            raise ConfigError('Run gdo-mkstable here')
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


