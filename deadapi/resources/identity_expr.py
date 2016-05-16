from .. import utils

class IdentityExpr(utils.Resource):
    # TODO POST, PUT
    def GET(self, id):
        meta = self.db.query('SELECT id, name FROM identity_expr WHERE id = :id', id=id).all()
        if not meta: raise cherrypy.NotFound
        children = [{k: v for k, v in x.as_dict().items() if v} for x in self.db.query(
            'SELECT operation, child, identity FROM identity_expr_edge WHERE parent = :id',
            id=id)]
        return dict(id=meta[0]['id'], name=meta[0]['name'], children=children)
