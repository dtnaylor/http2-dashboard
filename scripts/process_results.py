#!/usr/bin/env python
'''
Processes HTTP2 measurement results and outputs data files for the
dashboard site.
'''

import os
import sys
import argparse
import logging
import re
import glob
import datetime
import json
import pprint
import operator

from collections import defaultdict
from country_codes import country_to_code

sys.path.append('./myplot')
import myplot


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

def histogram(values, round_values=False):
    if round_values:
        values=map(round, values)

    hist = defaultdict(int)
    for value in values:
        hist[value] += 1
    
    return sorted(hist.items(), key=operator.itemgetter(0))

def cdf(values, round_values=False):
    counts, x_vals = myplot.cdf_vals_from_data(values)
    if round_values:
        x_vals=map(round, x_vals)
    return zip(x_vals, counts)




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
    data['pretty_date'] = dates[0].strftime('%a, %b %d, %Y')
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

def support_by_organization(conf, out_file):

    # get list of dates we have org data for
    dates = dates_for_prefix(conf['country_support_prefix'])

    data = []
    for date in dates[:7]:  # TODO: first of each month all the way back?
        date_file_suffix = date.strftime('%a_%b_%-d_%Y')  # dash for no leading 0 on day
        data_file = conf['organization_support_prefix'] + date_file_suffix

        values = []
        with open(data_file, 'r') as f:
            for line in f:
                org, count = line.strip().split()
                org = org.replace('-', ' ')
                values.append({
                    'name': org,
                    'value': int(count)
                })

        data.append({
            'pretty_date': date.strftime('%a, %b %d, %Y'),
            'values': values
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

        # TODO: CDF also?

        # add data to dict
        data.append({
            'year': date.year,
            'month': date.month-1,
            'day': date.day,
            'pretty_date': date.strftime('%a, %b %d, %Y'),
            'times': histogram(completion_times),
        })
    
    with open(out_file, 'w') as f:
        json.dump(data, f)

def usage_and_performance(conf, out_file):

    # initially store data in temp_data dict:
    # date -> proto -> dict:
    #   'num_objects' -> list of values
    #   'num_connections' -> list of values
    #   'num_domains' -> list of values
    #   'plt' -> list of values
    #
    # then transform to list of dicts:
    #   'pretty_date' -> date as string
    #   'protocols' -> list of protocols
    #   'protocol_data' -> dict of dicts: 
    #      'num_objects_hist' -> list of (value, count) pairs
    #      'num_objects_cdf' -> list of (x, y) pairs
    #      'num_connections_hist' -> list of (value, count) pairs
    #      'num_connections_cdf' -> list of (x, y) pairs
    #      'num_domains_hist' -> list of (value, count) pairs
    #      'num_domains_cdf' -> list of (x, y) pairs
    #      'plt_hist' -> list of (value, count) pairs
    #      'plt_cdf' -> list of (x, y) pairs


    # read data and store in temp dict
    temp_data = defaultdict(dict)
    for fname in glob.glob(conf['usage_dir'] + '/*'):
        m = re.match(r'([^_]*)_((Sun|Mon|Tue|Wed|Thu|Fri|Sat)_(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)_[0-9][0-9]?_[0-9]{4})', os.path.basename(fname))
        if m:
            protocol = m.group(1)
            date_str = m.group(2)
            date = datetime.datetime.strptime(date_str, '%a_%b_%d_%Y')

            objects = []
            conns = []
            domains = []
            plts = []
            with open(fname, 'r') as f:
                for line in f:
                    fields = line.strip().split()
                    objects.append(float(fields[0]))
                    conns.append(float(fields[1]))
                    domains.append(float(fields[2]))
                    plts.append(float(fields[3]))

            temp_data[date][protocol] = {
                'num_objects': objects,
                'num_connections': conns,
                'num_domains': domains,
                'plt': plts,
            }

    # convert to output format (for hists and CDFs)
    data = []
    for date in sorted(temp_data.keys(), reverse=True):
        proto_data = {}
        for proto in temp_data[date]:
            proto_data[proto] = {
                'num_objects_hist': histogram(temp_data[date][proto]['num_objects'], round_values=True),
                'num_objects_cdf': cdf(temp_data[date][proto]['num_objects'], round_values=True),
                'num_connections_hist': histogram(temp_data[date][proto]['num_connections'], round_values=True),
                'num_connections_cdf': cdf(temp_data[date][proto]['num_connections'], round_values=True),
                'num_domains_hist': histogram(temp_data[date][proto]['num_domains'], round_values=True),
                'num_domains_cdf': cdf(temp_data[date][proto]['num_domains'], round_values=True),
                'plt_hist': histogram(temp_data[date][proto]['plt'], round_values=True),
                'plt_cdf': cdf(temp_data[date][proto]['plt'], round_values=True),
            }
            
        data.append({
            'pretty_date': date.strftime('%a, %b %d, %Y'),
            'protocols': temp_data[date].keys(),
            'protocol_data': proto_data
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
    
    # SUPPORT BY ORGANIZATION
    out_file = os.path.join(args.outdir, 'support_by_organization.json')
    support_by_organization(conf, out_file)

    # ACTIVE WORKERS
    #out_file = os.path.join(args.outdir, 'active_workers.json')
    #active_workers(conf, out_file)
    
    # TASK COMPLETION
    #out_file = os.path.join(args.outdir, 'task_completion.json')
    #task_completion(conf, out_file)
    
    # USAGE AND PERFORMANCE
    #out_file = os.path.join(args.outdir, 'usage.json')
    #usage_and_performance(conf, out_file)
        






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
