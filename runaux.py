#!/usr/bin/env python3
"""Deadlock batch jobs runner."""

import argparse
import logging
import threading

import deadaux
import config

argparser = argparse.ArgumentParser(description='Run auxiliary jobs for Deadlock server')
argparser.add_argument("-l", "--log", help='log level', nargs='?', default='WARNING')

def setup_logging(loglevel):  # "Python is one of the worst languages to write Java in."
    logger = logging.getLogger('')
    logger.setLevel(loglevel)
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)
    ch.setFormatter(logging.Formatter('%(name)s %(levelname)s %(message)s'))
    logger.addHandler(ch)

if __name__ == '__main__':
    args = argparser.parse_args()
    setup_logging(args.log)

    threads = set()
    for jobname in config.allowed_batch_jobs:
        job = getattr(deadaux, jobname, None)
        if job:
            t = threading.Thread(target=job.start, kwargs=dict(config=config))
            t.start()
            threads.add(t)
    for t in threads: t.join()
