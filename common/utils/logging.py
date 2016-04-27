import binascii
import logging

class Formatter(logging.Formatter):
    """Deadlock-friendly formatter for logging. It likes to shorten things.

    Changes from logging.Formatter:

    - strips first name component from logger name, as it is redundant in both prod and devel config
    """
    def format(self, record):
        firstc = record.name.find('.')
        if record.name[:firstc] in ('deadaux', 'deadapi', 'deadserver'):
            record.name = record.name[firstc+1:]
        return super().format(record)
