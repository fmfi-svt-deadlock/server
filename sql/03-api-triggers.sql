-- Triggers to NOTIFY on table change -- for EventSource in deadapi
-- Building on 02-triggers.sql -- will not work without it!

-- Note: Don't forget to update WHEN clauses when changing scheme!

-- TODO for now these just say "something changed" and trigger a full reload, but it would be neat
-- to send the diff all the way to client

-- on access log change
CREATE TRIGGER accesslog_change AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON accesslog
               EXECUTE PROCEDURE notify_trigger('accesslog_change');

-- on system status change
CREATE TRIGGER status_change AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON accesslog
               EXECUTE PROCEDURE notify_trigger('status_change');
CREATE TRIGGER status_change AFTER INSERT OR UPDATE OR DELETE OR TRUNCATE ON controller
               EXECUTE PROCEDURE notify_trigger('status_change');
