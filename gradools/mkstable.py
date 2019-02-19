""" Convert grade csv file to simpler lookup
"""

from argparse import ArgumentParser

import pandas as pd


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "full_gradebook", help="Path to the csv file downloaded from Canvas")
    parser.add_argument(
        "--aname", help="Name of our assignment")
    parser.add_argument(
        "-o", "--output", default='student.csv', help="Path for output file")
    args = parser.parse_args()
    if args.aname is None:
        from .mconfig import CONFIG
        args.aname = CONFIG['assignment']
    required = ['Student', 'SIS User ID', 'SIS Login ID', 'Section',
                args.aname]
    df = pd.read_csv(args.full_gradebook)
    # Some strange unicode characters in 'Student' with a default read
    df.rename(columns={df.columns[0]: 'Student'}, inplace=True)
    df = df[required]
    df = df.dropna(subset = ['SIS User ID'])
    df['SIS User ID'] = df['SIS User ID'].astype(int)
    df.to_csv(args.output, index=False)
