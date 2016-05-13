-- note: don't use the same key in production ;-)
INSERT INTO controller (id, key) VALUES (1, '\x07fc9b73448cb53f45233e6db92ab6a6c7f3f8a998acf103fbab1c947c5f2a68');
INSERT INTO controller (id, key) VALUES (2, '\x07fc9b73448cb53f45233e6db92ab6a6c7f3f8a998acf103fbab1c947c5f2a68');
INSERT INTO controller (id, key) VALUES (3, '\x07fc9b73448cb53f45233e6db92ab6a6c7f3f8a998acf103fbab1c947c5f2a68');
INSERT INTO controller (id, key) VALUES (4, '\x07fc9b73448cb53f45233e6db92ab6a6c7f3f8a998acf103fbab1c947c5f2a68');
INSERT INTO controller (id, key) VALUES (5, '\x07fc9b73448cb53f45233e6db92ab6a6c7f3f8a998acf103fbab1c947c5f2a68');
INSERT INTO controller (id, key) VALUES (6, '\x07fc9b73448cb53f45233e6db92ab6a6c7f3f8a998acf103fbab1c947c5f2a68');
INSERT INTO controller (id, key) VALUES (7, '\x07fc9b73448cb53f45233e6db92ab6a6c7f3f8a998acf103fbab1c947c5f2a68');
INSERT INTO controller (id, key) VALUES (8, '\x07fc9b73448cb53f45233e6db92ab6a6c7f3f8a998acf103fbab1c947c5f2a68');
INSERT INTO controller (id, key) VALUES (47,'\x07fc9b73448cb53f45233e6db92ab6a6c7f3f8a998acf103fbab1c947c5f2a68');
ALTER SEQUENCE controller_id_seq RESTART WITH 256;

INSERT INTO aptype (id, name) VALUES (1, 't1');
INSERT INTO aptype (id, name) VALUES (2, 't2');
ALTER SEQUENCE aptype_id_seq RESTART WITH 256;

INSERT INTO accesspoint (id, name, type, controller) VALUES (1, 'door1', 1, 1);
INSERT INTO accesspoint (id, name, type, controller) VALUES (2, 'door2', 1, 2);
INSERT INTO accesspoint (id, name, type, controller) VALUES (3, 'door3', 2, 3);
INSERT INTO accesspoint (id, name, type)             VALUES (4, 'noctrl', 2);
INSERT INTO accesspoint (id, name)                   VALUES (5, 'notype');
INSERT INTO accesspoint (id, name, type, controller) VALUES (47,'testing', 2, 47);
ALTER SEQUENCE accesspoint_id_seq RESTART WITH 256;

-- Encode the following:
--
-- group 'testX'
-- group 'ugly': test2 and test3
-- profile 'test1 only'
-- profile 'all but ugly': testX or hello except ugly
--
-- accesspoint type 1:
-- workdays 07:00 - 20:00: use 'all but ugly' profile
-- holiday: use 'test1 only' profile
--
-- accesspoint type 2:
-- always allow testX

INSERT INTO identity (id, card) VALUES (0, 'hello');
INSERT INTO identity (id, card) VALUES (1, 'test1');
INSERT INTO identity (id, card) VALUES (2, 'test2');
INSERT INTO identity (id, card) VALUES (3, 'test3');
ALTER SEQUENCE identity_id_seq RESTART WITH 256;

INSERT INTO identity_expr (id, name) VALUES (0, 'testX');
INSERT INTO identity_expr_edge (parent, operation, identity) VALUES (0, 'INCLUDE', 1);
INSERT INTO identity_expr_edge (parent, operation, identity) VALUES (0, 'INCLUDE', 2);
INSERT INTO identity_expr_edge (parent, operation, identity) VALUES (0, 'INCLUDE', 3);


INSERT INTO identity_expr (id, name) VALUES (1, 'tests or hello');
INSERT INTO identity_expr_edge (parent, operation, child) VALUES (1, 'INCLUDE', 0);
INSERT INTO identity_expr_edge (parent, operation, identity) VALUES (1, 'INCLUDE', 0);

INSERT INTO identity_expr (id, name) VALUES (2, 'ugly');
INSERT INTO identity_expr_edge (parent, operation, identity) VALUES (2, 'INCLUDE', 2);
INSERT INTO identity_expr_edge (parent, operation, identity) VALUES (2, 'INCLUDE', 3);

INSERT INTO identity_expr (id, name) VALUES (3, 'except ugly');
INSERT INTO identity_expr_edge (parent, operation, child) VALUES (3, 'INCLUDE', 1);
INSERT INTO identity_expr_edge (parent, operation, child) VALUES (3, 'EXCLUDE', 2);

INSERT INTO identity_expr (id, name) VALUES (4, 'test1 only');
INSERT INTO identity_expr_edge (parent, operation, identity) VALUES (4, 'INCLUDE', 1);

ALTER SEQUENCE identity_expr_id_seq RESTART WITH 256;

INSERT INTO time_spec (id, name, weekday_mask, time_from, time_to) VALUES (0, 'pracovný deň', B'1111100', '07:00', '20:00');
INSERT INTO time_spec (id, name, date_from, date_to) VALUES (1, 'prázdniny', 'July 1, 2016', 'September 2, 2016');
INSERT INTO time_spec (id, name) VALUES (2, 'always');
INSERT INTO time_spec (id, name, time_from, time_to) VALUES (3, 'príjemný podvečer', '22:00', '23:59:59');
ALTER SEQUENCE time_spec_id_seq RESTART WITH 256;

INSERT INTO ruleset (id, name) VALUES (1, 'ruleset1');
ALTER SEQUENCE ruleset_id_seq RESTART WITH 256;

INSERT INTO rule (ruleset, priority, aptype, time_spec, expr, rkind) VALUES (1, 10, 1, 0, 3, 'ALLOW');
INSERT INTO rule (ruleset, priority, aptype, time_spec, expr, rkind) VALUES (1, 30, 1, 1, 4, 'ALLOW');
INSERT INTO rule (ruleset, priority, aptype, time_spec, expr, rkind) VALUES (1, 10, 2, 2, 0, 'ALLOW');
INSERT INTO rule (ruleset, priority, aptype, time_spec, expr, rkind) VALUES (1, 47, 1, 3, 3, 'ALLOW');


INSERT INTO accesslog (time, controller, card, allowed) VALUES (current_timestamp, 1, 'hello', true);
INSERT INTO accesslog (time, controller, card, allowed) VALUES (current_timestamp, 2, 'world', false);
