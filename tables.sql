controller (id macaddr PRIMARY KEY, ip inet UNIQUE NOT NULL, key bytea NOT NULL, name text)
log        (time timestamp NOT NULL, ctrl_id macaddr REFERENCES controller, message text)
