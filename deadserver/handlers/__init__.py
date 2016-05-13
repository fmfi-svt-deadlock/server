"""Collects request handlers for the various message types.

How to write a request handler:

Your module must define `function(controller_id, request_data) -> status, response_data`. This must
be registered as a handler for a request type using the `@handles(deadserver.protocol.MsgType)`
decorator. See below for note on importing.

Hello world example:

```python
from deadserver.protocol import MsgType, ResponseStatus

@handles(deadserver.protocol.MsgType.HELLO)  # actually, this doesn't exist, but if it did...
def handle_hello(controller_id, data):
    return ResponseStatus.OK, b'Hello ' + controller_id + b'! You sent: ' + data
```

See `./open.py` for a real-world example.

----------------------------------------------------------------------------------------------------

In order to be executed (and therefore registered), your handler module must be imported somewhere.
This file is a good place for that, as it is imported by `deadserver.api`. Unless you have a reason
to do this differently, add your handlers below.
"""

### LIST OF ALL STANDARD HANDLER IMPORTS ###########################################################

from . import alog
from . import ask
from . import echotest
from . import ping
from . import xfer

####################################################################################################

from .defs import get_handler_for  # for more convenient access
