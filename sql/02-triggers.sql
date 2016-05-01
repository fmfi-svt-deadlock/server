-- Triggers to NOTIFY on table change -- required by offlinedb
--
-- While other notification methods or polling or whatever would work as well, the current offlinedb
-- implementation uses Postgres's LISTEN on these notifications.
--
-- Some of these fire on change of the calculated in_expr table (as defined in
-- `01-materialize-rules.sql`) instead of the source data. Also, they fire many times and the client
-- is expected to debounce them.

-- Note: Don't forget to update WHEN clauses when changing scheme!

-- TODO for now these just say "something changed" and trigger a full rebuild, but it would be neat
-- to rebuild only as needed

CREATE FUNCTION notify_trigger() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify(TG_ARGV[0], '');
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- on identity_expr / profile change
CREATE TRIGGER in_expr_change AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON in_expr
               EXECUTE PROCEDURE notify_trigger('identity_expr_change');

-- on rule change
CREATE TRIGGER time_spec_change AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON time_spec
               EXECUTE PROCEDURE notify_trigger('rule_change');
CREATE TRIGGER rule_change AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON rule
               EXECUTE PROCEDURE notify_trigger('rule_change');

CREATE TRIGGER time_spec_change AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON ruleset
               EXECUTE PROCEDURE notify_trigger('rule_change');

-- on controller or accesspoint change
CREATE TRIGGER controller_change AFTER INSERT OR DELETE OR TRUNCATE ON controller
               EXECUTE PROCEDURE notify_trigger('controller_change');
CREATE TRIGGER controller_update AFTER UPDATE ON controller FOR EACH ROW
               WHEN (OLD.mac IS DISTINCT FROM NEW.mac)
               EXECUTE PROCEDURE notify_trigger('controller_change');

CREATE TRIGGER accesspoint_change AFTER INSERT OR DELETE OR TRUNCATE ON accesspoint
               EXECUTE PROCEDURE notify_trigger('controller_change');
CREATE TRIGGER accesspoint_update AFTER UPDATE ON accesspoint FOR EACH ROW
               WHEN ((OLD.ip, OLD.type, OLD.controller) IS DISTINCT FROM
                     (NEW.ip, NEW.type, NEW.controller))
               EXECUTE PROCEDURE notify_trigger('controller_change');
