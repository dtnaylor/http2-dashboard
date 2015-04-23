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
import operator

from collections import defaultdict
from country_codes import country_to_code

#sys.path.append('./myplot')
#import myplot


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

def dates_for_prefix(prefix, date_format='%a_%b_%d_%Y'):
    dates = glob.glob(prefix + '*')
    dates = map(lambda x: 
        datetime.datetime.strptime(x.replace(prefix, ''), date_format)
        , dates)
    dates = sorted(dates, reverse=True)
    return dates




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
    dates = dates_for_prefix(conf['country_support_prefix'])
    most_recent = dates[0].strftime('%a_%b_%-d_%Y')  # dash for no leading 0 on day
    data_file = conf['country_support_prefix'] + most_recent

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

def active_workers(conf, out_file):
    # get list of crawl dates we have monitoring information for
    dates = dates_for_prefix(conf['active_workers_prefix'])

    # list of dicts:
    #   'year' -> year
    #   'month' -> month (for JS, so 0-11)
    #   'day' -> day
    #   'pretty_date' -> date as string
    #   'counts' -> list of [time, count] pairs
    data = []
    for date in dates:
        # read time/count pairs from file
        in_file = conf['active_workers_prefix'] + date.strftime('%a_%b_%-d_%Y')
        time_count_pairs = []
        with open(in_file, 'r') as f:
            for line in f:
                fields = line.strip().split()
                time_count_pairs.append([int(fields[0])*1000,  # convert to milliseconds
                    int(fields[1])])

        # add data to dict
        data.append({
            'year': date.year,
            'month': date.month-1,
            'day': date.day,
            'pretty_date': date.strftime('%a, %b %d, %Y'),
            'counts': time_count_pairs,
        })
    
    with open(out_file, 'w') as f:
        json.dump(data, f)


def task_completion(conf, out_file):
    # get list of crawl dates we have monitoring information for
    dates = dates_for_prefix(conf['task_completion_prefix'])

    # list of dicts:
    #   'year' -> year
    #   'month' -> month (for JS, so 0-11)
    #   'day' -> day
    #   'pretty_date' -> date as string
    #   'time_hist' -> list of (time, count) pairs
    data = []
    for date in dates:
        # read completion times
        in_file = conf['task_completion_prefix'] + date.strftime('%a_%b_%-d_%Y')
        completion_times = []
        with open(in_file, 'r') as f:
            for line in f:
                fields = line.strip().split()
                completion_times.append(int(fields[0]))
                
        # make histogram
        time_hist = defaultdict(int)
        for time in completion_times:
            time_hist[time] += 1
        
        # sort & format as a list for highcharts
        sorted_time_hist = sorted(time_hist.items(), key=operator.itemgetter(0))

        # TODO: CDF also?

        # add data to dict
        data.append({
            'year': date.year,
            'month': date.month-1,
            'day': date.day,
            'pretty_date': date.strftime('%a, %b %d, %Y'),
            'times': sorted_time_hist,
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
    #out_file = os.path.join(args.outdir, 'support_by_country.json')
    #support_by_country(conf, out_file)

    # ACTIVE WORKERS
    #out_file = os.path.join(args.outdir, 'active_workers.json')
    #active_workers(conf, out_file)
    
    # TASK COMPLETION
    out_file = os.path.join(args.outdir, 'task_completion.json')
    task_completion(conf, out_file)
        






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
