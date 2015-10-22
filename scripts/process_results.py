#!/usr/bin/env python
'''
Processes HTTP2 measurement results and outputs data files for the
dashboard site.
'''

import os
import sys
import shutil
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

DATE_FORMATS = ('%a_%b_%d_%Y',
                '%Y-%m-%d',                
)


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

def parse_date(date_str):
    for fmt in DATE_FORMATS:
        try:
            date = datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            pass  # try another format
        else:
            return date  # if we parsed date successfully, stop tyring more formats
    else:  # no format succeeded
        raise ValueError('Error parsing date: %s' % date_str)

def read_time_series(filepath, date_first=False):
    try:
        with open(filepath, 'r') as f:
            counts = []
            start_date = None
            last_date = None
            for line in f:
                # parse the line
                if line.strip() == '': continue
                if date_first:
                    date, count = line.strip().split()
                else:
                    count, date = line.strip().split()

                try:
                    count = int(count)
                except:
                    if count not in ('NA', 'NaN'):
                        logging.warn('Invalid count: %s  (%s)' % (count, filepath))
                    continue

                try:
                    date = parse_date(date)
                except:
                    logging.warn('Invalid date: %s  (%s)' % (date, filepath))
                    continue

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

def dates_for_prefix(prefix, date_format='%Y-%m-%d'):
    dates = glob.glob(prefix + '*')
    dates = map(lambda x: 
        datetime.datetime.strptime(x.replace(prefix, ''), date_format)
        , dates)
    dates = sorted(dates, reverse=True)
    return dates

def dates_to_show(dates):
    '''
        Given a list of available crawl dates, return a subset that should
        be displayed to the user.
    '''

    dates_to_display = []
    
    # take the most recent week
    most_recent = dates[0]
    for date in dates:
        if (most_recent - date).days <= 7:
            dates_to_display.append(date)
        else:
            break

    # now take the first of every month as far back as we have
    for date in dates[len(dates_to_display):]:
        if date.day == 1:
            dates_to_display.append(date)

    return dates_to_display

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
def summary(conf, out_file):
    announced_count = read_time_series(conf['advertised_support_by_date'])[0][-1]
    partial_count = read_time_series(conf['partial_support_by_date'])[0][-1]
    true_count = read_time_series(conf['true_support_by_date'])[0][-1]

    data = {
        'announced_count': announced_count,
        'partial_count': partial_count,
        'true_count': true_count,
    }
    
    with open(out_file, 'w') as f:
        json.dump(data, f)

def support_by_date(conf, out_file):
    series = ['advertised_support_by_date',
              'partial_support_by_date',
              'true_support_by_date',
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

def support_by_server(conf, out_file):
    series = glob.glob('%s/*' % conf['server_support_prefix'])
    
    # series name -> key (counts, start, interval) -> value
    data = defaultdict(dict)

    for series_path in series:
        counts, start_date, interval =\
            read_time_series(series_path, date_first=True)
        series_name = os.path.split(series_path)[-1]

        if counts == None or start_date == None or interval == None: continue
        if counts[-1] < 100: continue  # TODO: smarter threshold

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

    data = []
    for date in dates_to_show(dates):
        date_file_suffix = date.strftime('%Y-%m-%d')  # dash for no leading 0 on day
        data_file = conf['country_support_prefix'] + date_file_suffix

        values = []
        with open(data_file, 'r') as f:
            for line in f:
                country, count = line.strip().split()
                country = country.replace('-', ' ')
                try:
                    values.append({
                        'name': country,
                        'code': country_to_code[country],
                        'value': int(count)
                    })
                except KeyError:
                    if country != 'NA':
                        logging.warn('Unknown country: %s  (%s)' % (country, data_file))
                except ValueError:
                    if count not in ('NA', 'NaN'):
                        logging.warn('Invalid count: %s  (%s)' % (count, data_file))
                except:
                    logging.exception('Error processing row in %s' % data_file)

        data.append({
            'pretty_date': date.strftime('%a, %b %d, %Y'),
            'values': values
        })

    with open(out_file, 'w') as f:
        json.dump(data, f)

def support_by_organization(conf, out_file):

    # get list of dates we have org data for
    dates = dates_for_prefix(conf['country_support_prefix'])

    data = []
    for date in dates_to_show(dates):
        date_file_suffix = date.strftime('%Y-%m-%d')  # dash for no leading 0 on day
        data_file = conf['organization_support_prefix'] + date_file_suffix

        values = []
        with open(data_file, 'r') as f:
            for line in f:
                org, count = line.strip().split()
                org = org.replace('-', ' ')
                try:
                    values.append({
                        'name': org,
                        'value': int(count)
                    })
                except ValueError:
                    if count not in ('NA', 'NaN'):
                        logging.warn('Invalid count: %s  (%s)' % (count, data_file))
                except:
                    logging.exception('Error processing row in %s' % data_file)

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
    for date in dates_to_show(dates):
        # read time/count pairs from file
        in_file = conf['active_workers_prefix'] + date.strftime('%Y-%m-%d')
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
    for date in dates_to_show(dates):
        # read completion times
        in_file = conf['task_completion_prefix'] + date.strftime('%Y-%m-%d')
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
        m = re.match(r'([^_]*)_([0-9]{4}-[0-9]{2}-[0-9]{2})', os.path.basename(fname))
        if m:
            protocol = m.group(1)
            date_str = m.group(2)
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')

            objects = []
            conns = []
            domains = []
            plts = []
            with open(fname, 'r') as f:
                for line in f:
                    fields = line.strip().split()
                    objects.append(float(fields[1]))
                    conns.append(float(fields[3]))
                    domains.append(float(fields[7]))
                    plts.append(float(fields[8]))

            temp_data[date][protocol] = {
                'num_objects': objects,
                'num_connections': conns,
                'num_domains': domains,
                'plt': plts,
            }

    # convert to output format (for hists and CDFs)
    data = []
    for date in sorted(temp_data.keys(), reverse=True):  # TODO: dates to show
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

def url_list(conf, out_subdir, prefix):
    # get most recent country support data
    dates = dates_for_prefix(prefix)

    # For now, just publish most recent
    # TODO: Check file doesn't already exist?
    # TODO: Check if we should copy old lists, in case script didn't run one day?
    try:
        date_file_suffix = dates[0].strftime('%Y-%m-%d')  # dash for no leading 0 on day
        data_file = prefix + date_file_suffix
        dest_file = os.path.join(out_subdir, '%s.txt' % os.path.split(data_file)[1])
        shutil.copyfile(data_file, dest_file)
        return dest_file
    except:
        logging.exception('Error copying URL list(s) for %s' % prefix)
        return '#'  # link to nowhere

def url_lists(conf, out_file, out_subdir):
    if not os.path.isdir(out_subdir):
        os.makedirs(out_subdir)

    # TODO: actually look up most recent we have
    announce_list = url_list(conf, out_subdir, conf['announce_list_dir'])
    partial_list = url_list(conf, out_subdir, conf['partial_list_dir'])
    true_list = url_list(conf, out_subdir, conf['true_list_dir'])

    data = {}
    data['h2-announce-list'] = announce_list
    data['h2-partial-list'] = partial_list
    data['h2-true-list'] = true_list
    
    with open(out_file, 'w') as f:
        json.dump(data, f)



    
        

##
## RUN
##
def run(conf_path, outdir):
    # load conf
    conf = load_conf(conf_path)

    # make output data dir if it doesn't exist
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    # SUMMARY
    out_file = os.path.join(outdir, 'summary.json')
    summary(conf, out_file)
    
    # SUPPORT BY DATE
    out_file = os.path.join(outdir, 'support_by_date.json')
    support_by_date(conf, out_file)
    
    # SUPPORT BY SERVER
    out_file = os.path.join(outdir, 'support_by_server.json')
    support_by_server(conf, out_file)

    # SUPPORT BY COUNTRY
    out_file = os.path.join(outdir, 'support_by_country.json')
    #support_by_country(conf, out_file)
    
    # SUPPORT BY ORGANIZATION
    out_file = os.path.join(outdir, 'support_by_organization.json')
    #support_by_organization(conf, out_file)

    # ACTIVE WORKERS
    out_file = os.path.join(outdir, 'active_workers.json')
    active_workers(conf, out_file)
    
    # TASK COMPLETION
    out_file = os.path.join(outdir, 'task_completion.json')
    task_completion(conf, out_file)
    
    # USAGE AND PERFORMANCE
    out_file = os.path.join(outdir, 'usage.json')
    usage_and_performance(conf, out_file)

    # URL LISTS
    out_file = os.path.join(outdir, 'lists.json')
    out_subdir = os.path.join(outdir, 'lists')
    url_lists(conf, out_file, out_subdir)



##
## MAIN
##
def main():
    run(args.config, args.outdir)
        





if __name__ == "__main__":
    # set up command line args
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,\
                                     description='Process H2 measurement results to make dashboard site data files.')
    parser.add_argument('-c', '--config', default='./test.conf', help='Configuration file.')
    parser.add_argument('-o', '--outdir', default='./data', help='Output directory for data files.')
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='only print errors')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='print debug info. --quiet wins if both are present')
    args = parser.parse_args()
    
    # set up logging
    setup_logging()
    
    main()
