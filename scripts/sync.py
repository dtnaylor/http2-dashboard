#!/usr/bin/env python

##
## Pull crawl results from mplane, process new data, and push new data
## files to web server.
##

import os
import sys
import argparse
import logging
import subprocess
import process_results

from logging import handlers


# tools
RSYNC = '/usr/bin/env rsync'

# config
DATA_DIR = './data'
WEB_DIR = '/afs/cs.cmu.edu/project/http2dashboard/www'
REMOTE_RESULT_DIR = 'mplane:/home/varvello/HTTP-2/results'
LOCAL_RESULT_DIR = '.'
SMTP_CREDENTIALS = './smtp.conf'

# FIXME hacky. need this function to unpickle phase3 pickles.
def defaultdict_dict():
    return defaultdict(dict)

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
    file_handler = handlers.RotatingFileHandler('sync.log',\
        maxBytes=10*1024*1024, backupCount=3)
    file_handler.setFormatter(logging.Formatter(fmt=logfmt))
    file_handler.setLevel(level)
    logging.getLogger('').addHandler(file_handler)

    # send errors by email
    if not args.no_email:
        try:
            smtp_conf = None
            with open(SMTP_CREDENTIALS, 'r') as f:
                smtp_conf = eval(f.read())

            email_handler = handlers.SMTPHandler(\
                smtp_conf['server'], 'varvello.research@gmail.com',\
                ['david.t.naylor@gmail.com', 'varvello.research@gmail.com'],\
                'HTTP/2 Dashboard Error',\
                credentials=smtp_conf['credentials'], secure=())
            email_handler.setFormatter(logging.Formatter(fmt=logfmt))
            email_handler.setLevel(logging.WARN)
            logging.getLogger('').addHandler(email_handler)
        except:
            logging.exception('Error loading SMTP conf')






def main():
    logging.info('=============== SYNC LAUNCHED ===============')

    ##
    ## Copy new results from mplane
    ##
    logging.info('Syncing results from mplane.')
    try:
        rsync_cmd = '%s -avz --no-g --delete --exclude phase3 %s %s' %\
            (RSYNC, REMOTE_RESULT_DIR, LOCAL_RESULT_DIR)
        logging.debug('Running rsync: %s', rsync_cmd)
        subprocess.check_call(rsync_cmd.split())
    except:
        logging.exception('Error syncing results from mplane')
        sys.exit(-1)  # TODO: keep going under certain errors?


    ##
    ## Process the data
    ##
    logging.info('Processing results.')
    try:
        process_results.run('./production.conf', DATA_DIR)
    except:
        logging.exception('Error processing results from mplane')
        sys.exit(-1)  # TODO: keep going under certain errors?


    ##
    ## Copy new data to web server
    ##
    if not args.local:
        logging.info('Syncing data to web server.')
        try:
            aws_cmd = 'aws s3 sync %s s3://isthewebhttp2yet.com/data' % DATA_DIR
            logging.debug('Running aws sync: %s', aws_cmd)
            subprocess.check_call(aws_cmd.split())
        except:
            logging.exception('Error copying profiles to AWS')
    
    logging.info('Done.')



if __name__ == "__main__":
    # set up command line args
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,\
                                     description='Process new H2 crawl data and update site.')
    parser.add_argument('--no-email', action='store_true', default=False, help='Do not send error emails')
    parser.add_argument('-l', '--local', action='store_true', default=False, help='Local test; do not copy data to web server.')
    parser.add_argument('-q', '--quiet', action='store_true', default=False, help='only print errors')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='print debug info. --quiet wins if both are present')
    args = parser.parse_args()
    

    # set up logging
    setup_logging()
    
    main()
