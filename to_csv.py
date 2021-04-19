import csv
from mgs import MGSPiracy
from argparse import ArgumentParser

if __name__ == '__main__':
    # parse arguments
    argp = ArgumentParser()
    argp.add_argument('--output', type=str, default='output.csv', help='CSV output file name')
    argp.add_argument('--from', type=int, default=0, help='First page', dest='_from')
    argp.add_argument('--to', type=int, default=10, help='Last page')
    args = argp.parse_args()

    # get cases
    mgs = MGSPiracy(from_page=args._from, to_page=args.to)
    cases = mgs.get_cases()

    # write to csv
    f = open(args.output, 'w', newline='')
    csv_writer = csv.writer(f)

    for case in cases:
        csv_writer.writerow((
            case['date'],
            case['statement_number'],
            case['applicant'],
            case['object'],
            case['doc_link'],
            case['violation_links']))

    f.close()