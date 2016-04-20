#!/usr/bin/env python3
"""Deadlock batch jobs runner."""

import argparse
import logging
import logging.config
import threading

import deadaux
import config

log = logging.getLogger(__name__)

def run_all():
    threads = []
    for jobname in config.allowed_batch_jobs:
        job = getattr(deadaux, jobname, None)
        if job:
            t = threading.Thread(target=job.start, kwargs=dict(config=config))
            t.start()
            threads.append(t)
            log.info('started job: {}'.format(jobname))
    for t in threads: t.join()

if __name__ == '__main__':
    logging.config.dictConfig(config.logging_config)
    run_all()
