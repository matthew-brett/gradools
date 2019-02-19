#!/usr/bin/env python
""" Generate initial marking scheme and notebook for student
"""

from os.path import exists, join as pjoin
from argparse import ArgumentParser

NB_TEMPLATE = pjoin('templates', 'grading.Rmd')

from .mconfig import SCORE_LINES, get_students


def get_init(student_id):
    students = get_students()
    student = students.loc[students['SIS Login ID'] == student_id]
    if len(student) == 0:
        raise RuntimeError(f"Cannot find student {student_id}")
    name = student['Student'].iloc[0]
    return f'## {student_id}\n\n{SCORE_LINES}\n\nTotal: \n\n{name}\n\n'


def write_notebook(login, nb_fname):
    if not exists(NB_TEMPLATE):
        return
    with open(NB_TEMPLATE, 'rt') as fobj:
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
    if not exists(nb_fname) or args.clobber:
        write_notebook(args.login, nb_fname)
    print(get_init(args.login))
