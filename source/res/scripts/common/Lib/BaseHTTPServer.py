# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/BaseHTTPServer.py
__version__ = '0.3'
__all__ = ['HTTPServer', 'BaseHTTPRequestHandler']
import sys
import time
import socket
from warnings import filterwarnings, catch_warnings
with catch_warnings():
    if sys.py3kwarning:
        filterwarnings('ignore', '.*mimetools has been removed', DeprecationWarning)
    import mimetools
import SocketServer
DEFAULT_ERROR_MESSAGE = '<head>\n<title>Error response</title>\n</head>\n<body>\n<h1>Error response</h1>\n<p>Error code %(code)d.\n<p>Message: %(message)s.\n<p>Error code explanation: %(code)s = %(explain)s.\n</body>\n'
DEFAULT_ERROR_CONTENT_TYPE = 'text/html'

def _quote_html(html):
    return html.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


class HTTPServer(SocketServer.TCPServer):
    allow_reuse_address = 1

    def server_bind(self):
        SocketServer.TCPServer.server_bind(self)
        host, port = self.socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port


class BaseHTTPRequestHandler(SocketServer.StreamRequestHandler):
    sys_version = 'Python/' + sys.version.split()[0]
    server_version = 'BaseHTTP/' + __version__
    default_request_version = 'HTTP/0.9'

    def parse_request(self):
        self.command = None
        self.request_version = version = self.default_request_version
        self.close_connection = 1
        requestline = self.raw_requestline
        requestline = requestline.rstrip('\r\n')
        self.requestline = requestline
        words = requestline.split()
        if len(words) == 3:
            command, path, version = words
            if version[:5] != 'HTTP/':
                self.send_error(400, 'Bad request version (%r)' % version)
                return False
            try:
                base_version_number = version.split('/', 1)[1]
                version_number = base_version_number.split('.')
                if len(version_number) != 2:
                    raise ValueError
                version_number = (int(version_number[0]), int(version_number[1]))
            except (ValueError, IndexError):
                self.send_error(400, 'Bad request version (%r)' % version)
                return False

            if version_number >= (1, 1) and self.protocol_version >= 'HTTP/1.1':
                self.close_connection = 0
            if version_number >= (2, 0):
                self.send_error(505, 'Invalid HTTP Version (%s)' % base_version_number)
                return False
        elif len(words) == 2:
            command, path = words
            self.close_connection = 1
            if command != 'GET':
                self.send_error(400, 'Bad HTTP/0.9 request type (%r)' % command)
                return False
        else:
            if not words:
                return False
            self.send_error(400, 'Bad request syntax (%r)' % requestline)
            return False
        self.command, self.path, self.request_version = command, path, version
        self.headers = self.MessageClass(self.rfile, 0)
        conntype = self.headers.get('Connection', '')
        if conntype.lower() == 'close':
            self.close_connection = 1
        elif conntype.lower() == 'keep-alive' and self.protocol_version >= 'HTTP/1.1':
            self.close_connection = 0
        return True

    def handle_one_request(self):
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if len(self.raw_requestline) > 65536:
                self.requestline = ''
                self.request_version = ''
                self.command = ''
                self.send_error(414)
                return
            if not self.raw_requestline:
                self.close_connection = 1
                return
            if not self.parse_request():
                return
            mname = 'do_' + self.command
            if not hasattr(self, mname):
                self.send_error(501, 'Unsupported method (%r)' % self.command)
                return
            method = getattr(self, mname)
            method()
            self.wfile.flush()
        except socket.timeout as e:
            self.log_error('Request timed out: %r', e)
            self.close_connection = 1
            return

    def handle(self):
        self.close_connection = 1
        self.handle_one_request()
        while not self.close_connection:
            self.handle_one_request()

    def send_error(self, code, message=None):
        try:
            short, long = self.responses[code]
        except KeyError:
            short, long = ('???', '???')

        if message is None:
            message = short
        explain = long
        self.log_error('code %d, message %s', code, message)
        self.send_response(code, message)
        self.send_header('Connection', 'close')
        content = None
        if code >= 200 and code not in (204, 205, 304):
            content = self.error_message_format % {'code': code,
             'message': _quote_html(message),
             'explain': explain}
            self.send_header('Content-Type', self.error_content_type)
        self.end_headers()
        if self.command != 'HEAD' and content:
            self.wfile.write(content)
        return

    error_message_format = DEFAULT_ERROR_MESSAGE
    error_content_type = DEFAULT_ERROR_CONTENT_TYPE

    def send_response(self, code, message=None):
        self.log_request(code)
        if message is None:
            if code in self.responses:
                message = self.responses[code][0]
            else:
                message = ''
        if self.request_version != 'HTTP/0.9':
            self.wfile.write('%s %d %s\r\n' % (self.protocol_version, code, message))
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())
        return

    def send_header(self, keyword, value):
        if self.request_version != 'HTTP/0.9':
            self.wfile.write('%s: %s\r\n' % (keyword, value))
        if keyword.lower() == 'connection':
            if value.lower() == 'close':
                self.close_connection = 1
            elif value.lower() == 'keep-alive':
                self.close_connection = 0

    def end_headers(self):
        if self.request_version != 'HTTP/0.9':
            self.wfile.write('\r\n')

    def log_request(self, code='-', size='-'):
        self.log_message('"%s" %s %s', self.requestline, str(code), str(size))

    def log_error(self, format, *args):
        self.log_message(format, *args)

    def log_message(self, format, *args):
        sys.stderr.write('%s - - [%s] %s\n' % (self.client_address[0], self.log_date_time_string(), format % args))

    def version_string(self):
        return self.server_version + ' ' + self.sys_version

    def date_time_string(self, timestamp=None):
        if timestamp is None:
            timestamp = time.time()
        year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
        s = '%s, %02d %3s %4d %02d:%02d:%02d GMT' % (self.weekdayname[wd],
         day,
         self.monthname[month],
         year,
         hh,
         mm,
         ss)
        return s

    def log_date_time_string(self):
        now = time.time()
        year, month, day, hh, mm, ss, x, y, z = time.localtime(now)
        s = '%02d/%3s/%04d %02d:%02d:%02d' % (day,
         self.monthname[month],
         year,
         hh,
         mm,
         ss)
        return s

    weekdayname = ['Mon',
     'Tue',
     'Wed',
     'Thu',
     'Fri',
     'Sat',
     'Sun']
    monthname = [None,
     'Jan',
     'Feb',
     'Mar',
     'Apr',
     'May',
     'Jun',
     'Jul',
     'Aug',
     'Sep',
     'Oct',
     'Nov',
     'Dec']

    def address_string(self):
        host, port = self.client_address[:2]
        return socket.getfqdn(host)

    protocol_version = 'HTTP/1.0'
    MessageClass = mimetools.Message
    responses = {100: ('Continue', 'Request received, please continue'),
     101: ('Switching Protocols', 'Switching to new protocol; obey Upgrade header'),
     200: ('OK', 'Request fulfilled, document follows'),
     201: ('Created', 'Document created, URL follows'),
     202: ('Accepted', 'Request accepted, processing continues off-line'),
     203: ('Non-Authoritative Information', 'Request fulfilled from cache'),
     204: ('No Content', 'Request fulfilled, nothing follows'),
     205: ('Reset Content', 'Clear input form for further input.'),
     206: ('Partial Content', 'Partial content follows.'),
     300: ('Multiple Choices', 'Object has several resources -- see URI list'),
     301: ('Moved Permanently', 'Object moved permanently -- see URI list'),
     302: ('Found', 'Object moved temporarily -- see URI list'),
     303: ('See Other', 'Object moved -- see Method and URL list'),
     304: ('Not Modified', 'Document has not changed since given time'),
     305: ('Use Proxy', 'You must use proxy specified in Location to access this resource.'),
     307: ('Temporary Redirect', 'Object moved temporarily -- see URI list'),
     400: ('Bad Request', 'Bad request syntax or unsupported method'),
     401: ('Unauthorized', 'No permission -- see authorization schemes'),
     402: ('Payment Required', 'No payment -- see charging schemes'),
     403: ('Forbidden', 'Request forbidden -- authorization will not help'),
     404: ('Not Found', 'Nothing matches the given URI'),
     405: ('Method Not Allowed', 'Specified method is invalid for this resource.'),
     406: ('Not Acceptable', 'URI not available in preferred format.'),
     407: ('Proxy Authentication Required', 'You must authenticate with this proxy before proceeding.'),
     408: ('Request Timeout', 'Request timed out; try again later.'),
     409: ('Conflict', 'Request conflict.'),
     410: ('Gone', 'URI no longer exists and has been permanently removed.'),
     411: ('Length Required', 'Client must specify Content-Length.'),
     412: ('Precondition Failed', 'Precondition in headers is false.'),
     413: ('Request Entity Too Large', 'Entity is too large.'),
     414: ('Request-URI Too Long', 'URI is too long.'),
     415: ('Unsupported Media Type', 'Entity body in unsupported format.'),
     416: ('Requested Range Not Satisfiable', 'Cannot satisfy request range.'),
     417: ('Expectation Failed', 'Expect condition could not be satisfied.'),
     500: ('Internal Server Error', 'Server got itself in trouble'),
     501: ('Not Implemented', 'Server does not support this operation'),
     502: ('Bad Gateway', 'Invalid responses from another server/proxy.'),
     503: ('Service Unavailable', 'The server cannot process the request due to a high load'),
     504: ('Gateway Timeout', 'The gateway server did not receive a timely response'),
     505: ('HTTP Version Not Supported', 'Cannot fulfill request.')}


def test(HandlerClass=BaseHTTPRequestHandler, ServerClass=HTTPServer, protocol='HTTP/1.0'):
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 8000
    server_address = ('', port)
    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)
    sa = httpd.socket.getsockname()
    print 'Serving HTTP on', sa[0], 'port', sa[1], '...'
    httpd.serve_forever()


if __name__ == '__main__':
    test()
