-- Automatically pre-evaluates and materializes access rules.
-- The current implementations of offlinedb and OPEN packet handler depend on this.

-- TODO currently I just recalculate everything on change, but incremental updating would be easy to
-- implement. Do it one day.

-- identity is in expr. (This whole file is about making this table contain that.)
CREATE TABLE in_expr (
    identity integer NOT NULL REFERENCES identity,
    expr     integer NOT NULL REFERENCES identity_expr,
    UNIQUE (identity, expr)
);

-- if expr in here, it is up-to-date, otherwise it needs to be recalculated
CREATE TABLE _mr_up_to_date (
    expr integer UNIQUE NOT NULL REFERENCES identity_expr
);

-- "is there a path through operands from identity to this expr", this view is over the materialized
-- in_expr table
CREATE VIEW _mr_expr_edge AS
    SELECT parent AS expr, identity, operation AS op
    FROM identity_expr_edge
    WHERE identity IS NOT NULL
UNION
    SELECT parent AS expr, m.identity AS identity, e.operation AS op
    FROM identity_expr_edge e JOIN in_expr m ON m.expr = e.child
    WHERE e.child IS NOT NULL;

-- Recalculates in_expr for the given expression id, recursing top to bottom.
--
-- Works almost like the obvious WITH RECURSIVE query, but stuff is added procedurally, so that we
-- don't have that silly "ill-defined fixed point" problem.
CREATE FUNCTION RecalculateExpr(e integer) RETURNS void AS $$
BEGIN
    IF e IN (SELECT expr FROM _mr_up_to_date) THEN RETURN; END IF;
    INSERT INTO _mr_up_to_date VALUES(e);

    PERFORM RecalculateExpr(child)
        FROM identity_expr_edge
        WHERE parent = e AND child IS NOT NULL;

    INSERT INTO in_expr (identity, expr)
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
