#!/usr/bin/env python
""" Generate initial marking scheme, maybe notebook for student
"""

from os.path import exists
from argparse import ArgumentParser

from .mconfig import CONFIG


def get_init(student_id, config=CONFIG):
    students = config.get_students()
    # Try login ID, then User ID, then name
    for field in ('SIS Login ID', 'SIS User ID', 'Student'):
        # Coerce to matching dtype
        try:
            st_id = students[field].dtype.type(student_id)
        except ValueError:
            continue
        these = students.loc[students[field] == st_id]
        if len(these) == 1:
            break
        elif len(these) > 1:
            raise RuntimeError(f"More than one match for {student_id}")
    else:
        raise RuntimeError(f"Cannot find student {student_id}")
    name, login = these[['Student', 'SIS Login ID']].iloc[0]
    lines = config.score_lines
    return f'## {login}\n\n{lines}\n\nTotal: \n\n{name}\n\n'


def write_notebook(login, nb_fname, nb_template):
    with open(nb_template, 'rt') as fobj:
        template = fobj.read()
    nb = template.replace('{{ login }}', login)
    with open(nb_fname, 'wt') as fobj:
        fobj.write(nb)


def main():
    parser = ArgumentParser()
    parser.add_argument('login', help='login name of submitting student')
    parser.add_argument('--clobber', action='store_true',
                        help='If specified, overwrite existing notebook')
    args = parser.parse_args()
    nb_fname = args.login + '.Rmd'
    nb_template = CONFIG.nb_template
    if nb_template and (not exists(nb_fname) or args.clobber):
        write_notebook(args.login, nb_fname, nb_template)
    print(get_init(args.login))
