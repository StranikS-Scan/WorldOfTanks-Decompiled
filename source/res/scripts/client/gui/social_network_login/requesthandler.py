# Embedded file name: scripts/client/gui/social_network_login/RequestHandler.py
import httplib
import base64
from urlparse import urlparse, parse_qsl
from BaseHTTPServer import BaseHTTPRequestHandler
from debug_utils import LOG_DEBUG
from gui import GUI_SETTINGS

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
        TEMPLATE_EMPTY_GIF_BASE64 = 'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='
        if 'token_encrypted' in kwargs:
            token = kwargs['token_encrypted']
        else:
            token = kwargs['token']
        self.send_response(httplib.OK)
        self.send_header('Content-Type', 'image/gif')
        self.end_headers()
        self.wfile.write(base64.decodestring(TEMPLATE_EMPTY_GIF_BASE64))
        self.wfile.close()
        self.server.keepData(token, kwargs['account_id'])

    def onLoginWithRedirect(self, **kwargs):
        if 'token_encrypted' in kwargs:
            token = kwargs['token_encrypted']
        else:
            token = kwargs['token']
        self.send_response(httplib.FOUND)
        self.send_header('Location', kwargs['next'])
        self.end_headers()
        self.server.keepData(token, kwargs['account_id'])

    def log_message(self, request, *args):
        LOG_DEBUG('%s (http://localhost:%s) finished processing %s' % (self.server.name, self.server.server_port, request % args))
