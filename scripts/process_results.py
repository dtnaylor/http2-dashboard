#!/usr/bin/env python
'''
Processes HTTP2 measurement results and outputs data files for the
dashboard site.
'''

import os
import sys
import argparse
import logging
import glob
import datetime
import json
import pprint

from collections import defaultdict
from country_codes import country_to_code


##
## HELPER FUNCTIONS
##
def setup_logging():
    if args.quiet:
        level = logging.WARNING
    elif args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO
    config = {
        'format' : "%(levelname) -10s %(asctime)s %(module)s:%(lineno) -7s %(message)s",
        'level' : level
    }
    logging.basicConfig(**config)

def load_conf(conf_file):
    conf = None
    try:
        with open(conf_file, 'r') as f:
            conf = eval(f.read())
        f.closed
    except:
        logging.exception('Error reading configuration: %s', conf_file)

    return conf

def read_time_series(filepath):
    try:
        with open(filepath, 'r') as f:
            counts = []
            start_date = None
            last_date = None
            for line in f:
                # parse the line
                if line.strip() == '': continue
                count, date = line.strip().split()
                count = int(count)
                date = datetime.datetime.strptime(date, '%a_%b_%d_%Y')

                # if this is the first entry, set start_date
                if not start_date:
                    start_date = date

                # check for duplicate or missing days
                if last_date:
                    days_since_last_point = (date-last_date).days

                    # ignore this point if 2nd point this day
                    if days_since_last_point == 0:
                        continue

                    # repeat last data point if days are missing
                    if days_since_last_point > 1:
                        counts += [counts[-1]]*(days_since_last_point-1)

                counts.append(count)
                last_date = date

        return counts, start_date, 24 * 3600 * 1000
    except Exception:
        logging.exception('Error reading time series: %s' % filepath)
        return None, None, None

##
## DATA PROCESSING FUNCTIONS
##
def support_by_date(conf, out_file):
    series = ['advertised_support_by_date',
              'actual_support_by_date',
              'h2_12_advertised_support_by_date',
              'h2_14_advertised_support_by_date',
              'h2_15_advertised_support_by_date',
              'h2_16_advertised_support_by_date',
              'h2_17_advertised_support_by_date',
              'spdy_2',
              'spdy_3',
              'spdy_3.1',
             ]
    
    # series name -> key (counts, start, interval) -> value
    data = defaultdict(dict)

    for series_name in series:
        counts, start_date, interval =\
            read_time_series(conf[series_name])

        data[series_name]['counts'] = counts
        data[series_name]['start_year'] = start_date.year
        data[series_name]['start_month'] = start_date.month-1
        data[series_name]['start_day'] = start_date.day
        data[series_name]['interval'] = interval

    with open(out_file, 'w') as f:
        json.dump(data, f)

def support_by_country(conf, out_file):

    # get most recent country support data
    dates = glob.glob(conf['country_support_prefix'] + '*')
    dates = map(lambda x: 
        datetime.datetime.strptime(x.replace(conf['country_support_prefix'], ''), '%a_%b_%d_%Y')
        , dates)
    dates = sorted(dates, reverse=True)
    most_recent = dates[0].strftime('%a_%b_%d_%Y')
    data_file = conf['country_support_prefix'] + most_recent
    print data_file

    # read the file & match countries with codes
    data = {}
    data['data_date'] = dates[0].strftime('%a, %b %d, %Y')
    data['values'] = []
    with open(data_file, 'r') as f:
        for line in f:
            country, count = line.strip().split()
            country = country.replace('-', ' ')
            data['values'].append({
                'name': country,
                'code': country_to_code[country],  # TODO: catch value error
                'value': int(count)
            })

    with open(out_file, 'w') as f:
        json.dump(data, f)



##
## MAIN
##
def main():

    # make output data dir if it doesn't exist
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)
    
    # SUPPORT BY DATE
    #out_file = os.path.join(args.outdir, 'support_by_date.json')
    #support_by_date(conf, out_file)

    # SUPPORT BY COUNTRY
    out_file = os.path.join(args.outdir, 'support_by_country.json')
    support_by_country(conf, out_file)
        






if __name__ == "__main__":
    # set up command line args
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,\
                                     description='Process H2 measurement results to make dashboard site data files.')
    parser.add_argument('-c', '--config', default='./test.conf', help='Configuration file.')
    parser.add_argument('-o', '--outdir', default='./data', help='Output directory for data files.')
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='only print errors')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='print debug info. --quiet wins if both are present')
    args = parser.parse_args()
    
    # load conf
    conf = load_conf(args.config)

    # set up logging
    setup_logging()
    
    main()
