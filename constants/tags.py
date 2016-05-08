# TODO maybe split into more files?

# All should start with 0xDE (unassigned according to
# http://www.iana.org/assignments/cbor-tags/cbor-tags.xhtml)

### types ##########################################################################################

TYPE_RECORD  = 0xDE01
TYPE_IPADDR  = 0xDE02

### data fields ####################################################################################

MSG_PING     = 0xDE21
MSG_XFER     = 0xDE22
MSG_ALOG     = 0xDE23
MSG_ASK      = 0xDE28
MSG_ECHOTEST = 0xDE2E

RESPONSE_OK        = 0xDE42  # the answer...
RESPONSE_ERR       = 0xDE45
RESPONSE_TRY_AGAIN = 0xDE47

TIME     = 0xDE51
FILETYPE = 0xDE61
CARD_ID  = 0xDE91
ALLOWED  = 0xDE92

CONTROLLER = 0xDEAA
NONCE      = 0xDEAB
PAYLOAD    = 0xDEAC
VERSION    = 0xDEAD

### controller configuration #######################################################################

CONFIG_ID = 0xDEC0

# symmetric crypto
CONFIG_KEY = 0xDEC2

# asymmetric crypto
CONFIG_PRIVKEY     = 0xDEC4
CONFIG_SERVER_KEYS = 0xDEC5  # array; must be in the same order as server IPs in CONFIG_SERVERS

# network setup
CONFIG_MAC         = 0xDECA
CONFIG_IP          = 0xDECB
CONFIG_ROUTE       = 0xDECC
CONFIG_SERVERS     = 0xDECD  # array of IP addresses
CONFIG_SERVER_PORT = 0xDECE

### other ##########################################################################################

DUMMY = 0xDEFF
