CREATE TABLE controller (
    id   macaddr PRIMARY KEY,
    ip   inet    UNIQUE NOT NULL,
    key  bytea   NOT NULL,
    name text
);

CREATE TYPE mtype_enum  AS ENUM ('OPEN');
CREATE TYPE status_enum AS ENUM ('OK', 'ERR', 'TRY_AGAIN');
CREATE TABLE log_messages (
    time          timestamp   NOT NULL DEFAULT current_timestamp,
    controller_id macaddr     REFERENCES controller,
    mtype         mtype_enum  NOT NULL,
    data          bytea       ,
    status        status_enum NOT NULL
);
CREATE TABLE log_badpackets (
    time          timestamp NOT NULL DEFAULT current_timestamp,
    error         text      NOT NULL,
    data          bytea     NOT NULL -- TODO is zero length NULL? That can happen...
);
