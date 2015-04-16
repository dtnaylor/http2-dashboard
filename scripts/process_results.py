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

def advertised_support_by_date(result_file, out_file):
    print result_file, out_file





def main():

    # make output data dir if it doesn't exist
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)
    
    # advertised support by date
    if os.path.isfile(conf['advertised_support_by_date']):
        out_file = os.path.join(args.outdir, 'advertised_support_by_date.json')
        advertised_support_by_date(conf['advertised_support_by_date'], out_file)
        






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
