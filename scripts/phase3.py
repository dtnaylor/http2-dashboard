#!/usr/bin/env python
'''
Pre-process phase3 results to produce intermediate data (so we don't need to
pull all phase3 results just to update the website).
'''

import os
import sys
import shutil
import argparse
import logging
import re
import glob
import datetime
import pprint
import tempfile
import shutil
import subprocess
import cPickle
from collections import defaultdict
from logging import handlers

sys.path.append('./myplot')
import myplot

DATE_FORMATS = ('%a_%b_%d_%Y',
                '%Y-%m-%d',                
)

##
## CONFIGURATION
##
SMTP_CREDENTIALS = './smtp.conf'
RESULT_DIR = './results'
OUTPUT_DIR = os.path.join(RESULT_DIR, 'phase3-processed-for-site')
PHASE3_DIRS = [
    'phase3/telefonica',
    'phase3/telefonica/3G',
    'phase3/telefonica/4G',
    'phase3/cmu',
    'phase3/case',
]

SKIP_TARBALLS = [
    'results/phase3/case/res-weirdsites.tgz',
    'results/phase3/telefonica/res-10-23-15-1445591500.tgz',
    'results/phase3/telefonica/res-10-26-15-1445887874.tgz',
]


##
## HELPER FUNCTIONS
##
def setup_logging():
    logfmt = "%(levelname) -10s %(asctime)s %(module)s:%(lineno) -7s %(message)s"
    if args.quiet:
        level = logging.WARNING
    elif args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logging.getLogger('').setLevel(level)

    # log to file (capped at 10 MB)
    file_handler = handlers.RotatingFileHandler('phase3.log',\
        maxBytes=10*1024*1024, backupCount=3)
    file_handler.setFormatter(logging.Formatter(fmt=logfmt))
    file_handler.setLevel(level)
    logging.getLogger('').addHandler(file_handler)

    # send errors by email
    try:
        smtp_conf = None
        with open(SMTP_CREDENTIALS, 'r') as f:
            smtp_conf = eval(f.read())

        email_handler = handlers.SMTPHandler(\
            smtp_conf['server'], 'varvello.research@gmail.com',\
            ['dtbn07@gmail.com'], 'HTTP/2 Dashboard Error',\
            credentials=smtp_conf['credentials'], secure=())
        email_handler.setFormatter(logging.Formatter(fmt=logfmt))
        email_handler.setLevel(logging.WARN)
        logging.getLogger('').addHandler(email_handler)
    except:
        logging.warn('Error loading SMTP conf')

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

#def dates_for_prefix(prefix, date_format='%Y-%m-%d'):
#    dates = glob.glob(prefix + '*')
#    dates = map(lambda x: 
#        datetime.datetime.strptime(x.replace(prefix, ''), date_format)
#        , dates)
#    dates = sorted(dates, reverse=True)
#    return dates

def get_new_tarballs():
    # skip bad tarballs or ones we've already processed
    processed_tarballs = load_pickle('processed', default=[])
    skip = SKIP_TARBALLS + processed_tarballs
    new_tarballs = []

    for p3_dir in PHASE3_DIRS:
        p3_dir = os.path.join(RESULT_DIR, p3_dir)

        for tarball in glob.glob(p3_dir + '/*.tgz'):
            if not any(skip_path in tarball for skip_path in skip):
                new_tarballs.append(tarball)

    return new_tarballs

# hack for pickling
def defaultdict_dict():
    return defaultdict(dict)

def load_pickle(tag, default=None):
    path = os.path.join(OUTPUT_DIR, '%s.pickle' % tag)
    data = None
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                data = cPickle.load(f)
        except:
            logging.exception('Error loading pickle: %s' % path)

    if data == None:
        if default == None:
            data = defaultdict(defaultdict_dict)
        else:
            data = default

    return data

def save_pickle(tag, data):
    path = os.path.join(OUTPUT_DIR, '%s.pickle' % tag)
    with open(path, 'w') as f:
        cPickle.dump(data, f)







##
## DATA PROCESSING FUNCTIONS
##
def process_result_file(result_file, tag, date):
    # open data files
    plt_data = load_pickle('plt')
    num_objs_data = load_pickle('num_objs')
    num_conns_data = load_pickle('num_conns')
    num_domains_data = load_pickle('num_domains')

    # add new values to existing data
    with open(result_file, 'r') as f:
        column_key = None
        for line in f:
            if not column_key:
                headings = line.strip().split('\t')
                column_key = {headings[i]: i for i in range(len(headings))}
                continue

            values = line.strip().split('\t')
            url = values[column_key['url']]

            # When loaded over H2, what fraction of the page's objects use H2?
            try:
                h2_frac = float(values[column_key['num_h2_objects-delayed-h2']])/\
                          float(values[column_key['num_objects-delayed-h2']])
            except:
                h2_frac = None

            # TODO: condense this if same for all measurements

            # PLT
            try:
                plt_data[tag][url][date] = {
                    'h2-obj-frac': h2_frac,
                    'h1-value': float(values[column_key['on_load-mean-h1']]),
                    'h2-value': float(values[column_key['on_load-mean-h2']]),
                }
            except ValueError as e:
                if e.message != 'could not convert string to float: N/A':
                    logging.debug('PLT value error: %s, %s\n%s' % (result_file, url, e))

            # NUM OBJECTS
            try:
                num_objs_data[tag][url][date] = {
                    'h2-obj-frac': h2_frac,
                    'h1-value': float(values[column_key['num_objects-delayed-h1']]),
                    'h2-value': float(values[column_key['num_objects-delayed-h2']]),
                }
            except ValueError as e:
                if e.message != 'could not convert string to float: N/A':
                    logging.debug('Num objects value error: %s, %s' % (result_file, url))
            
            # NUM CONNECTIONS
            try:
                num_conns_data[tag][url][date] = {
                    'h2-obj-frac': h2_frac,
                    'h1-value': float(values[column_key['num_tcp_handshakes-mean-h1']]),
                    'h2-value': float(values[column_key['num_tcp_handshakes-mean-h2']]),
                }
            except ValueError as e:
                if e.message != 'could not convert string to float: N/A':
                    logging.debug('Num conns value error: %s, %s' % (result_file, url))
            
            # NUM DOMAINS
            try:
                num_domains_data[tag][url][date] = {
                    'h2-obj-frac': h2_frac,
                    'h1-value': float(values[column_key['num_hosts-mean-h1']]),
                    'h2-value': float(values[column_key['num_hosts-mean-h2']]),
                }
            except ValueError as e:
                if e.message != 'could not convert string to float: N/A':
                    logging.debug('Num domains value error: %s, %s' % (result_file, url))


    save_pickle('plt', plt_data)
    save_pickle('num_objs', num_objs_data)
    save_pickle('num_conns', num_conns_data)
    save_pickle('num_domains', num_domains_data)


def process_tarball(tarball):
    logging.info('Processing: %s' % tarball)

    # if there are no problems, don't process this tarball in the future
    all_ok = True

    # get date and tag (location + access network type)
    matches = re.match(r'.*/(cmu|case|telefonica)/(3G|4G)*/*res-([0-9]{2}-[0-9]{2}-[0-9]{2})-[0-9]*.tgz',\
        tarball)

    if matches:
        location = matches.group(1)
        network = matches.group(2) if matches.group(2) else 'eth'
        date = matches.group(3)
        tag = '%s-%s' % (location, network)

        # make a temp dir to untar the tarball in
        tmpdir = tempfile.mkdtemp(prefix='phase3')
        
        # copy tarball to tmp dir and extract
        try:
            tar_cmd = 'tar -xzf %s -C %s' % (tarball, tmpdir)
            logging.debug('Untar: %s', tar_cmd)
            subprocess.check_call(tar_cmd.split())
        except:
            logging.exception('Error extracting tarball: %s', tarball)
            all_ok = False

        # extract results
        for result_file in glob.glob(tmpdir + '/res-full*'):
            try:
                process_result_file(result_file, tag, date)
            except:
                logging.exception('Error processing result file: %s' % result_file)
                all_ok = False

        # delete tmp dir
        try:
            shutil.rmtree(tmpdir)
        except:
            logging.exception('Error deleting tmp dir: %s' % tmpdir)

    else:
        logging.warn('Error parsing tarball name: %s', tarball)
        all_ok = False

    # add to processed tarballs list
    if all_ok:
        processed_tarballs = load_pickle('processed', default=[])
        processed_tarballs.append(tarball)
        save_pickle('processed', processed_tarballs)
    



    
        

##
## RUN
##
def run():
    # make output data dir if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for tarball in get_new_tarballs():
        process_tarball(tarball)



##
## MAIN
##
def main():
    run()
        





if __name__ == "__main__":
    # set up command line args
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,\
                                     description='Preprocess phase3 results for website.')
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='only print errors')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='print debug info. --quiet wins if both are present')
    args = parser.parse_args()
    
    # set up logging
    setup_logging()
    
    main()
