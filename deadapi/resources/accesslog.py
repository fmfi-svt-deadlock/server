from .. import utils

class AccessLog(utils.Resource):
    default_params = dict(
        limit=200,
    )

    def GET(self, **params):
        # TODO filtering
        params_keys = set(self.default_params).intersection(set(params))
        params = utils.m(self.default_params, params)
        return self.db.query('''
            SELECT a.id, a.time, a.controller, a.card, a.allowed, p.name AS ap, p.id AS ap_id
            FROM accesslog a LEFT OUTER JOIN accesspoint p ON a.controller = p.controller
            ORDER BY time DESC LIMIT :limit
            ''', **params).all()
