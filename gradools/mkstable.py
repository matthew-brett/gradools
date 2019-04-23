""" Convert grade csv file to simpler lookup
"""

from argparse import ArgumentParser

from .canvastools import to_minimal_df

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
