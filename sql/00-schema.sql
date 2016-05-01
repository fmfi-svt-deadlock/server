-- DeadServer's database table definitions

-- Note: Don't forget to update WHEN clauses in `02-triggers.sql` when changing scheme!

----- BASIC DATA -----------------------------------------------------------------------------------

CREATE TABLE controller (
    id  serial  PRIMARY KEY,
    mac macaddr UNIQUE NOT NULL,
    key bytea   NOT NULL,

    last_seen  timestamptz,
    db_version integer,
    fw_version integer
);

CREATE TABLE aptype (
    id   serial PRIMARY KEY,
    name text   UNIQUE NOT NULL CHECK (name <> '')
);

CREATE TABLE accesspoint (
    id         serial  PRIMARY KEY,
    ip         inet    UNIQUE,
    name       text    UNIQUE NOT NULL CHECK (name <> ''),
    type       integer REFERENCES aptype,
    controller integer UNIQUE REFERENCES controller
);

CREATE TABLE identity (
    id   serial PRIMARY KEY,
    card bytea  NOT NULL
);

----- RULES ----------------------------------------------------------------------------------------

--- Identity expressions ---

CREATE TYPE expr_op AS ENUM ('INCLUDE', 'EXCLUDE');
-- There is no "NOT" -- (INCLUDE a, EXCLUDE a, EXCLUDE b) is just ()

CREATE TABLE identity_expr (
    id   serial PRIMARY KEY,
    name text   UNIQUE NOT NULL CHECK (name <> '')
);

CREATE TABLE identity_expr_edge ( -- not really normalized, but convenient, plus simple constraints
    operation expr_op NOT NULL,
    parent    integer NOT NULL REFERENCES identity_expr,
    child     integer REFERENCES identity_expr,
    identity  integer REFERENCES identity,

    UNIQUE     (parent, child, identity),
    CONSTRAINT leaf_or_not_leaf CHECK (identity IS NOT NULL OR child IS NOT NULL),
    CONSTRAINT but_not_both     CHECK (identity IS NULL     OR child IS NULL)
);

--- Rules ----

-- this is cron (with intervals instead of points): NULL matches everything, stuff is ANDed together
CREATE TABLE time_spec (
    id           serial PRIMARY KEY,
    name         text UNIQUE NOT NULL CHECK (name <> ''),
    time_from    time with time zone,
    time_to      time with time zone,
    weekday_mask bit(7), -- 0 is MONDAY!!!!!
    date_from    date,
    date_to      date,

    CONSTRAINT   time_both CHECK ((time_from IS NOT NULL AND time_to IS NOT NULL) OR
                                  (time_from IS NULL     AND time_to IS NULL)),
    CONSTRAINT   date_both CHECK ((date_from IS NOT NULL AND date_to IS NOT NULL) OR
                                  (date_from IS NULL     AND date_to IS NULL))
);

CREATE TYPE rule_kind AS ENUM ('ALLOW', 'DENY');

CREATE TABLE ruleset (
    id    serial      PRIMARY KEY,
    name  text        UNIQUE NOT NULL CHECK (name <> ''),
    mtime timestamptz DEFAULT current_timestamp
);

CREATE TABLE rule (
    id        serial    PRIMARY KEY,
    ruleset   integer   NOT NULL REFERENCES ruleset,
    priority  integer   NOT NULL, -- higher wins
    aptype    integer   NOT NULL REFERENCES aptype,
    time_spec integer   REFERENCES time_spec, -- if NULL, means UnknownTime
    expr      integer   NOT NULL REFERENCES identity_expr,
    rkind     rule_kind NOT NULL,

    UNIQUE    (aptype, priority)
);

----- AUXILIARY (ACCESS LOGS) ----------------------------------------------------------------------

CREATE TABLE accesslog (
    id         serial      PRIMARY KEY,
    time       timestamptz NOT NULL,
    controller integer     NOT NULL REFERENCES controller,
    card       bytea       NOT NULL,
    allowed    boolean     NOT NULL
);
