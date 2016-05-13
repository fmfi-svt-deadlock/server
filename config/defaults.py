"""The server configuration defaults.

The following have no defaults and therefore *must* be set somewhere else:

 - host
 - port
 - http_host
 - http_port
 - db_url
 - controller_files_path

"""

import yaml  # for lazy people who don't like typing

### Resources (such as ports, DB, filesystem) ######################################################

# host = ...
# port = ...
# http_host = ...
# http_port = ...
# db_url = ...
# controller_files_path = ...

### Application settings ###########################################################################

# Process only these message types.
allowed_msg_types = {'PING', 'XFER', 'ALOG', 'ASK', 'ECHOTEST'}

# Run only the following batch job types.
allowed_batch_jobs = {'offlinedb', 'echotest'}

test_id = 0  # ID reserved for testing purposes
             # a controller and an associated accesspoint with this ID needed for integration tests

### deadaux configuration ##########################################################################

deadaux = dict(
    echotest=dict(
        interval=30,  # send test packet every x seconds
        timeout=0.5,  # how long to wait for reply, in seconds
    ),
    offlinedb=dict(
        num_worker_threads=8
    ),
)

### Logging config #################################################################################

# logging_config = yaml.load(open('config/logging-prod.yml'))
logging_config = yaml.load(open('config/logging-devel.yml'))

# when logging the full message buffer, save at most...
log_message_bytes = 1024
