""" Split grading log into student feedback fragments, build PDFS
"""

import os
from os.path import join as pjoin, isdir
import re
from subprocess import Popen, PIPE, check_call

from .mconfig import MARKING_LOG


STUDENT_SPLITTER = re.compile(r'^##\s+', re.M)
STID_FINDER = re.compile(r'^\w\w\w\d+')
TOTAL_FINDER = re.compile(r'^Total\s*:\s*[0-9.]+')
FEEDBACK_DIR = 'feedback'


def prune_part(part):
    lines = []
    have_total = False
    for line in part.splitlines():
        if have_total:
            lines.append(line)
        elif TOTAL_FINDER.match(line):
            have_total = True
    return '\n'.join(lines)


def get_parts():
    with open(MARKING_LOG, 'rt') as fobj:
        text = fobj.read()
    parts = STUDENT_SPLITTER.split(text)
    public_parts = {}
    for part in parts:
        match = STID_FINDER.match(part)
        if match is None:
            continue
        public_parts[match.group()] = prune_part(part)
    return public_parts


def write_parts(parts, out_dir=FEEDBACK_DIR):
    for stid, text in parts.items():
        out_root = pjoin(out_dir, stid)
        proc = Popen(['pandoc', '-f' 'gfm', '-t', 'latex', '-o',
                      out_root + '_notes.pdf'],
                     stdin=PIPE, stderr=PIPE)
        out, err = proc.communicate(text.encode('utf8'))
        if err:
            raise RuntimeError(err)
        check_call(['jupyter', 'nbconvert', stid + '.ipynb',
                    '--to', 'pdf', '--output', out_root + '_nb'])


def write_stids(stids, out_dir=FEEDBACK_DIR):
    with open(pjoin(out_dir, 'stids.txt'), 'wt') as fobj:
        fobj.write('\n'.join(stids))


def main():
    if not isdir(FEEDBACK_DIR):
        os.makedirs(FEEDBACK_DIR)
    parts = get_parts()
    write_parts(parts)
    write_stids(parts)


if __name__ == '__main__':
    main()