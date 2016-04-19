-- Automatically pre-evaluates and materializes access rules.
-- The current implementations of offlinedb and OPEN packet handler depend on this.

-- TODO currently I just recalculate everything on change, but incremental updating should be easy
-- to implement. Do it one day.

-- identity_id is allowed by expr_id. (This whole file is about making this table contain that.)
CREATE TABLE in_expr (
    identity_id integer NOT NULL REFERENCES identity,
    expr_id     integer NOT NULL REFERENCES identity_expr,
    UNIQUE      (identity_id, expr_id)
);

-- if expr_id in here, it is up-to-date, otherwise it needs to be recalculated
CREATE TABLE _mr_up_to_date (
    expr_id integer UNIQUE NOT NULL REFERENCES identity_expr
);

-- materialized "is there a path through operands from identity to this expr" almost like
-- WITH RECURSIVE, but stuff is added procedurally
CREATE VIEW _mr_expr_edge AS
    SELECT parent AS expr, identity_id AS identity, operation AS op
    FROM identity_expr_edge
    WHERE identity_id IS NOT NULL
UNION
    SELECT parent AS expr, m.identity_id AS identity, e.operation AS op
    FROM identity_expr_edge e JOIN in_expr m ON m.expr_id = e.child
    WHERE e.child IS NOT NULL;

-- Recalculates in_expr for the given expression id, recursing top to bottom.
CREATE FUNCTION RecalculateExpr(e integer) RETURNS void AS $$
BEGIN
    IF e IN (SELECT expr_id FROM _mr_up_to_date) THEN RETURN; END IF;
    INSERT INTO _mr_up_to_date VALUES(e);

    PERFORM RecalculateExpr(child)
        FROM identity_expr_edge
        WHERE parent = e AND child IS NOT NULL;

    INSERT INTO in_expr (identity_id, expr_id)
        (SELECT DISTINCT identity, expr FROM _mr_expr_edge WHERE expr = e AND op = 'INCLUDE'
          EXCEPT (SELECT identity, expr FROM _mr_expr_edge WHERE expr = e AND op = 'EXCLUDE'));
END
$$ LANGUAGE 'plpgsql';

CREATE FUNCTION RecalculateAll() RETURNS trigger AS $$
BEGIN
  TRUNCATE TABLE in_expr;
  TRUNCATE TABLE _mr_up_to_date;
  PERFORM RecalculateExpr(id) FROM identity_expr;
  RETURN NULL;
END
$$ LANGUAGE 'plpgsql';

CREATE TRIGGER recalculate_in_expr AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE
    ON identity_expr_edge
    EXECUTE PROCEDURE RecalculateAll();
