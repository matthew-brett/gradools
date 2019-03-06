""" Convert grade csv file to simpler lookup
"""

from argparse import ArgumentParser

import pandas as pd

_REQUIRED = ('Student', 'SIS User ID', 'SIS Login ID', 'Section')


def to_minimal_df(full_gradebook):
    df = pd.read_csv(full_gradebook)
    # Some strange unicode characters in 'Student' with a default read
    df.rename(columns={df.columns[0]: 'Student'}, inplace=True)
    df = df[list(_REQUIRED)]
    df = df.dropna(subset = ['SIS User ID'])
    df['SIS User ID'] = df['SIS User ID'].astype(int)
    return df


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "full_gradebook", help="Path to the csv file downloaded from Canvas")
    parser.add_argument(
        "-o", "--output", help="Path for output file")
    args = parser.parse_args()
    if args.output is None:
        from .mconfig import CONFIG
        args.output = args.output if args.output else CONFIG.student_fname
    to_minimal_df(args.full_gradebook).to_csv(args.output, index=False)
