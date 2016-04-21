"""TODO"""

import cherrypy

@cherrypy.tools.json_in()
@cherrypy.tools.json_out()
class Root(object):
    exposed = True

    def GET(self, *args):
        return [
            {
                'id':          42,
                'time':        4742,
                'accesspoint': 'mrkva',
                'controller':  'mrkvactrl',
                'card':        'Jozef Mrkva',
                'allowed':     True,
            },
            {
                'id':          47,
                'time':        4747,
                'accesspoint': 'mrkva',
                'controller':  'mrkvactrl',
                'card':        'Jozef Mrkva',
                'allowed':     False,
            },
        ]

cpconfig = {
    '/': {
        'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
    },
}
