CREATE TABLE IF NOT EXISTS controller (
    id macaddr PRIMARY KEY,
    ip inet UNIQUE NOT NULL,
    key bytea NOT NULL,
    name text
);
CREATE TABLE IF NOT EXISTS log (
    time timestamp NOT NULL,
    ctrl_id macaddr REFERENCES controller,
    message text
);
