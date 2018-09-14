# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/login/social_networks/RequestHandler.py
import httplib
import base64
from urlparse import urlparse, parse_qsl
from BaseHTTPServer import BaseHTTPRequestHandler
from gui import GUI_SETTINGS
_TEMPLATE_EMPTY_GIF_BASE64 = 'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = dict(parse_qsl(parsed.query))
        if ('token' in params or 'token_encrypted' in params) and path == '/login/' and 'account_id' in params:
            if 'next' in params and params['next'] == GUI_SETTINGS.socialNetworkLogin['redirectURL']:
                self.onLoginWithRedirect(**params)
            else:
                self.onLogin(**params)
        else:
            self.send_response(httplib.NOT_FOUND)
            self.end_headers()

    def onLogin(self, **kwargs):
        token, accountId, socialNetwork = self.__fetchParams(kwargs)
        self.send_response(httplib.OK)
        self.send_header('Content-Type', 'image/gif')
        self.end_headers()
        self.wfile.write(base64.decodestring(_TEMPLATE_EMPTY_GIF_BASE64))
        self.wfile.close()
        self.server.keepData(token, accountId, socialNetwork)

    def onLoginWithRedirect(self, **kwargs):
        token, accountId, socialNetwork = self.__fetchParams(kwargs)
        self.send_response(httplib.FOUND)
        self.send_header('Location', kwargs['next'])
        self.end_headers()
        self.server.keepData(token, accountId, socialNetwork)

    def __fetchParams(self, params):
        if 'token_encrypted' in params:
            token = params['token_encrypted']
        else:
            token = params['token']
        socialNetwork = params.get('authentication_method', '').partition(':')[2]
        return (token, params['account_id'], socialNetwork)

    def log_request(self, code='-', size='-'):
        pass
