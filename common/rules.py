"""Evaluates access rules.

Depends on the `in_expr` table being alive and well -- see `sql/01-materialize-rules.sql`.
"""

def ask(db, accesspoint, when, identity):
    """Evaluate the rules and return True iff access is allowed.

    Parameters:
    db: something with a `records.Database`-like interface
    accesspoint: ID of the accesspoint, as specified in the DB
    time: `datetime.datetime`
    identity: ID of the identity, as specified in the DB

    You probably want to use this with `common.utils.db.transaction`.
    """
    r = db.query(
        '''
        SELECT (rkind = 'ALLOW')
        FROM rule r
             JOIN accesspoint p ON p.type = r.aptype
             JOIN time_spec t ON r.time_spec = t.id
             JOIN in_expr e ON r.expr = e.expr_id
        WHERE p.id = :accesspoint
              AND (t.time_from IS NULL OR (t.time_from <= :time AND :time <= t.time_to))
              AND (t.date_from IS NULL OR (t.date_from <= :date AND :date <= t.date_to))
              AND (t.weekday_mask IS NULL OR (get_bit(t.weekday_mask, :weekday) = 1))
              AND e.identity_id = :identity
        ORDER BY r.priority DESC LIMIT 1
        ''',
        accesspoint=accesspoint, date=when.date(), time=when.time(), weekday=when.weekday(),
        identity=identity).all()
    if not r: return False
    return r[0][0]
