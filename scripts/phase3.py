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

sys.path.append('./myplot')
import myplot

DATE_FORMATS = ('%a_%b_%d_%Y',
                '%Y-%m-%d',                
)

##
## CONFIGURATION
##
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
    # TODO: skip tarballs we've already processed
    skip = SKIP_TARBALLS
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

def load_pickle(tag):
    path = os.path.join(OUTPUT_DIR, '%s.pickle' % tag)
    data = None
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                data = cPickle.load(f)
        except:
            logging.exception('Error loading pickle: %s' % path)

    if data == None:
        data = defaultdict(defaultdict_dict)

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
    # TODO: other values

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

            # PLT
            try:
                h1_plt = float(values[column_key['on_load-mean-h1']])
                h2_plt = float(values[column_key['on_load-mean-h2']])
                plt_data[tag][url][date] = h1_plt-h2_plt 
            except ValueError:
                logging.debug('PLT value error: %s, %s' % (result_file, url))

            # TODO: other values

    save_pickle('plt', plt_data)


def process_tarball(tarball):
    logging.info('Processing: %s' % tarball)

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

        # extract results
        for result_file in glob.glob(tmpdir + '/res-full*'):
            process_result_file(result_file, tag, date)

        # delete tmp dir
        try:
            shutil.rmtree(tmpdir)
        except:
            logging.exception('Error deleting tmp dir: %s' % tmpdir)

    else:
        logging.warn('Error parsing tarball name: %s', tarball)

    # TODO: add to processed tarballs list
    



    
        

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
