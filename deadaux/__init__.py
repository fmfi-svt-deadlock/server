"""The Deadlock auxiliary jobs: support for offline database creation and firmware updates.

A job module must export a `start(config)` function.

If you want your job to be run by `runaux.py`, import it below:
"""

from . import offlinedb
from . import echotest
