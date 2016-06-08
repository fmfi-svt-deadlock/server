from .. import utils

class Status(utils.Resource):
    def GET(self):
        return self.db.query('''
            SELECT p.id, p.name, t.id AS type_id, t.name AS type, controller,
                   last_seen, controller_time, db_version, fw_version
            FROM accesspoint p
                 LEFT OUTER JOIN aptype t ON p.type = t.id
                 LEFT OUTER JOIN controller c ON p.controller = c.id
            ORDER BY type''').all()
