""" Check marking totals
"""

import sys
import re

from collections import OrderedDict

from .mconfig import CONFIG, proc_line


def check_totals(fname):
    out = []
    totals, msg = checked_totals(fname)
    if msg:
        out.append(msg)
    for name, total in totals.items():
        out.append('{:<10} : {}'.format(name, total))
    return '\n'.join(out)


def checked_totals(fname, config=CONFIG):
    with open(fname, 'rt') as fobj:
        contents = fobj.read()
    required, optional = CONFIG.scores
    lists, msg = get_lists(contents, list(required), list(optional))
    totals = OrderedDict()
    for name, marks in lists.items():
        totals[name] = sum(marks.values())
    return totals, msg


def _check_total(line, name, marks, required_fields, msg_lines):
    missing = set(required_fields).difference(marks)
    if len(missing):
        msg_lines.append("Required field{} {} not present".format(
            's' if len(missing) > 1 else '',
            ', '.join(sorted(missing))))
    actual_total = sum(marks.values())
    if not line.lower().startswith('total'):
        msg_lines.append("Expecting total {} for {}".format(
            actual_total, name))
        return
    total_text = line.split(':')[1].strip()
    total = float(total_text) if total_text else 0.
    if not total == sum(marks.values()):
        msg_lines.append("Expected {} for {}, got {}".format(
            actual_total, name, total))


def get_lists(contents, required_fields, optional_fields):
    lists = {}
    state = 'before'
    msg_lines = []
    all_fields = required_fields + optional_fields
    for line in contents.splitlines():
        if line.strip() == '':
            continue
        if state == 'before':
            if re.match('##[^#]', line):
                state = 'in-list'
                name = line.split()[1]
                mark_list = {}
            continue
        if state == 'in-list':
            if line.startswith('* '):
                key, value = proc_line(line)
                if not key in all_fields:
                    msg_lines.append(
                        "Did not expect key: '{}' here".format(key))
                mark_list[key] = float(value)
                continue
            lists[name] = mark_list
            state = 'total'
        if state == 'total':
            _check_total(line, name, lists[name], required_fields, msg_lines)
            state = 'before'
    # Clean up incomplete list, missing total
    if state in ('in-list', 'total'):
        lists[name] = mark_list
        # Maybe still need to check the total, for list at end of file.
        _check_total('', name, lists[name], required_fields, msg_lines)
    return lists, '\n'.join(msg_lines)


def main():
    log = sys.argv[1] if len(sys.argv) > 1 else CONFIG.marking_log
    print(check_totals(log))
