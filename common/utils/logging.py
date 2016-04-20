import binascii
import logging

class Formatter(logging.Formatter):
    """Deadlock-friendly formatter for logging. It likes to shorten things.

    Changes from logging.Formatter:

    - strips first name component from logger name, as it is redundant in both prod and devel config
    """
    def format(self, record):
        record.name = record.name[record.name.find('.')+1:]
        return super().format(record)
