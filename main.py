import argparse
from getpass import getuser
import logging
from process_accidents import AccidentData


parser = argparse.ArgumentParser(description='Apply accident calculations for a single network.')
parser.add_argument('rates_workbook', help='Accident rates workbook')
parser.add_argument('network_file', help='Network file to process')
parser.add_argument('year', type=int, help='Year of the network')
parser.add_argument('log_file', help='Output log file for the process')
parser.add_argument('output_csv', help='Output CSV file for the results')

args = parser.parse_args()

logging.basicConfig(
    handlers=[logging.FileHandler(args.log_file), logging.StreamHandler()],
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s]: %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.info(f'Process started by {getuser()}')
logging.info(f'Network: {args.network_file}')
logging.info(f'Rates Book: {args.rates_workbook}')
logging.info(f'Year: {args.year}')

ad = AccidentData(args.network_file, year=args.year)
ad.get_accident_numbers(rates_workbook=args.rates_workbook)
ad.export_totals(args.output_csv)
