# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/httplib.py
from array import array
import os
import re
import socket
from sys import py3kwarning
from urlparse import urlsplit
import warnings
with warnings.catch_warnings():
    if py3kwarning:
        warnings.filterwarnings('ignore', '.*mimetools has been removed', DeprecationWarning)
    import mimetools
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

__all__ = ['HTTP',
 'HTTPResponse',
 'HTTPConnection',
 'HTTPException',
 'NotConnected',
 'UnknownProtocol',
 'UnknownTransferEncoding',
 'UnimplementedFileMode',
 'IncompleteRead',
 'InvalidURL',
 'ImproperConnectionState',
 'CannotSendRequest',
 'CannotSendHeader',
 'ResponseNotReady',
 'BadStatusLine',
 'error',
 'responses']
HTTP_PORT = 80
HTTPS_PORT = 443
_UNKNOWN = 'UNKNOWN'
_CS_IDLE = 'Idle'
_CS_REQ_STARTED = 'Request-started'
_CS_REQ_SENT = 'Request-sent'
CONTINUE = 100
SWITCHING_PROTOCOLS = 101
PROCESSING = 102
OK = 200
CREATED = 201
ACCEPTED = 202
NON_AUTHORITATIVE_INFORMATION = 203
NO_CONTENT = 204
RESET_CONTENT = 205
PARTIAL_CONTENT = 206
MULTI_STATUS = 207
IM_USED = 226
MULTIPLE_CHOICES = 300
MOVED_PERMANENTLY = 301
FOUND = 302
SEE_OTHER = 303
NOT_MODIFIED = 304
USE_PROXY = 305
TEMPORARY_REDIRECT = 307
BAD_REQUEST = 400
UNAUTHORIZED = 401
PAYMENT_REQUIRED = 402
FORBIDDEN = 403
NOT_FOUND = 404
METHOD_NOT_ALLOWED = 405
NOT_ACCEPTABLE = 406
PROXY_AUTHENTICATION_REQUIRED = 407
REQUEST_TIMEOUT = 408
CONFLICT = 409
GONE = 410
LENGTH_REQUIRED = 411
PRECONDITION_FAILED = 412
REQUEST_ENTITY_TOO_LARGE = 413
REQUEST_URI_TOO_LONG = 414
UNSUPPORTED_MEDIA_TYPE = 415
REQUESTED_RANGE_NOT_SATISFIABLE = 416
EXPECTATION_FAILED = 417
UNPROCESSABLE_ENTITY = 422
LOCKED = 423
FAILED_DEPENDENCY = 424
UPGRADE_REQUIRED = 426
INTERNAL_SERVER_ERROR = 500
NOT_IMPLEMENTED = 501
BAD_GATEWAY = 502
SERVICE_UNAVAILABLE = 503
GATEWAY_TIMEOUT = 504
HTTP_VERSION_NOT_SUPPORTED = 505
INSUFFICIENT_STORAGE = 507
NOT_EXTENDED = 510
responses = {100: 'Continue',
 101: 'Switching Protocols',
 200: 'OK',
 201: 'Created',
 202: 'Accepted',
 203: 'Non-Authoritative Information',
 204: 'No Content',
 205: 'Reset Content',
 206: 'Partial Content',
 300: 'Multiple Choices',
 301: 'Moved Permanently',
 302: 'Found',
 303: 'See Other',
 304: 'Not Modified',
 305: 'Use Proxy',
 306: '(Unused)',
 307: 'Temporary Redirect',
 400: 'Bad Request',
 401: 'Unauthorized',
 402: 'Payment Required',
 403: 'Forbidden',
 404: 'Not Found',
 405: 'Method Not Allowed',
 406: 'Not Acceptable',
 407: 'Proxy Authentication Required',
 408: 'Request Timeout',
 409: 'Conflict',
 410: 'Gone',
 411: 'Length Required',
 412: 'Precondition Failed',
 413: 'Request Entity Too Large',
 414: 'Request-URI Too Long',
 415: 'Unsupported Media Type',
 416: 'Requested Range Not Satisfiable',
 417: 'Expectation Failed',
 500: 'Internal Server Error',
 501: 'Not Implemented',
 502: 'Bad Gateway',
 503: 'Service Unavailable',
 504: 'Gateway Timeout',
 505: 'HTTP Version Not Supported'}
MAXAMOUNT = 1048576
_MAXLINE = 65536
_MAXHEADERS = 100
_is_legal_header_name = re.compile('\\A[^:\\s][^:\\r\\n]*\\Z').match
_is_illegal_header_value = re.compile('\\n(?![ \\t])|\\r(?![ \\t\\n])').search
_contains_disallowed_url_pchar_re = re.compile('[\x00- \x7f-\xff]')
_METHODS_EXPECTING_BODY = {'PATCH', 'POST', 'PUT'}

class HTTPMessage(mimetools.Message):

    def addheader(self, key, value):
        prev = self.dict.get(key)
        if prev is None:
            self.dict[key] = value
        else:
            combined = ', '.join((prev, value))
            self.dict[key] = combined
        return

    def addcontinue(self, key, more):
        prev = self.dict[key]
        self.dict[key] = prev + '\n ' + more

    def readheaders(self):
        self.dict = {}
        self.unixfrom = ''
        self.headers = hlist = []
        self.status = ''
        headerseen = ''
        firstline = 1
        tell = None
        if not hasattr(self.fp, 'unread') and self.seekable:
            tell = self.fp.tell
        while True:
            if len(hlist) > _MAXHEADERS:
                raise HTTPException('got more than %d headers' % _MAXHEADERS)
            if tell:
                try:
                    tell()
                except IOError:
                    tell = None
                    self.seekable = 0

            line = self.fp.readline(_MAXLINE + 1)
            if len(line) > _MAXLINE:
                raise LineTooLong('header line')
            if not line:
                self.status = 'EOF in headers'
                break
            if firstline and line.startswith('From '):
                self.unixfrom = self.unixfrom + line
                continue
            firstline = 0
            if headerseen and line[0] in ' \t':
                hlist.append(line)
                self.addcontinue(headerseen, line.strip())
                continue
            elif self.iscomment(line):
                continue
            elif self.islast(line):
                break
            headerseen = self.isheader(line)
            if headerseen:
                hlist.append(line)
                self.addheader(headerseen, line[len(headerseen) + 1:].strip())
            if headerseen is not None:
                pass
            self.status = 'Non-header line where header expected'

        return


class HTTPResponse():

    def __init__(self, sock, debuglevel=0, strict=0, method=None, buffering=False):
        if buffering:
            self.fp = sock.makefile('rb')
        else:
            self.fp = sock.makefile('rb', 0)
        self.debuglevel = debuglevel
        self.strict = strict
        self._method = method
        self.msg = None
        self.version = _UNKNOWN
        self.status = _UNKNOWN
        self.reason = _UNKNOWN
        self.chunked = _UNKNOWN
        self.chunk_left = _UNKNOWN
        self.length = _UNKNOWN
        self.will_close = _UNKNOWN
        return

    def _read_status(self):
        line = self.fp.readline(_MAXLINE + 1)
        if len(line) > _MAXLINE:
            raise LineTooLong('header line')
        if self.debuglevel > 0:
            print 'reply:', repr(line)
        if not line:
            raise BadStatusLine('No status line received - the server has closed the connection')
        try:
            version, status, reason = line.split(None, 2)
        except ValueError:
            try:
                version, status = line.split(None, 1)
                reason = ''
            except ValueError:
                version = ''

        if not version.startswith('HTTP/'):
            if self.strict:
                self.close()
                raise BadStatusLine(line)
            else:
                self.fp = LineAndFileWrapper(line, self.fp)
                return ('HTTP/0.9', 200, '')
        try:
            status = int(status)
            if status < 100 or status > 999:
                raise BadStatusLine(line)
        except ValueError:
            raise BadStatusLine(line)

        return (version, status, reason)

    def begin(self):
        if self.msg is not None:
            return
        else:
            while True:
                version, status, reason = self._read_status()
                if status != CONTINUE:
                    break
                while True:
                    skip = self.fp.readline(_MAXLINE + 1)
                    if len(skip) > _MAXLINE:
                        raise LineTooLong('header line')
                    skip = skip.strip()
                    if not skip:
                        break
                    if self.debuglevel > 0:
                        print 'header:', skip

            self.status = status
            self.reason = reason.strip()
            if version == 'HTTP/1.0':
                self.version = 10
            elif version.startswith('HTTP/1.'):
                self.version = 11
            elif version == 'HTTP/0.9':
                self.version = 9
            else:
                raise UnknownProtocol(version)
            if self.version == 9:
                self.length = None
                self.chunked = 0
                self.will_close = 1
                self.msg = HTTPMessage(StringIO())
                return
            self.msg = HTTPMessage(self.fp, 0)
            if self.debuglevel > 0:
                for hdr in self.msg.headers:
                    print 'header:', hdr,

            self.msg.fp = None
            tr_enc = self.msg.getheader('transfer-encoding')
            if tr_enc and tr_enc.lower() == 'chunked':
                self.chunked = 1
                self.chunk_left = None
            else:
                self.chunked = 0
            self.will_close = self._check_close()
            length = self.msg.getheader('content-length')
            if length and not self.chunked:
                try:
                    self.length = int(length)
                except ValueError:
                    self.length = None
                else:
                    if self.length < 0:
                        self.length = None
            else:
                self.length = None
            if status == NO_CONTENT or status == NOT_MODIFIED or 100 <= status < 200 or self._method == 'HEAD':
                self.length = 0
            if not self.will_close and not self.chunked and self.length is None:
                self.will_close = 1
            return

    def _check_close(self):
        conn = self.msg.getheader('connection')
        if self.version == 11:
            conn = self.msg.getheader('connection')
            if conn and 'close' in conn.lower():
                return True
            return False
        if self.msg.getheader('keep-alive'):
            return False
        if conn and 'keep-alive' in conn.lower():
            return False
        pconn = self.msg.getheader('proxy-connection')
        return False if pconn and 'keep-alive' in pconn.lower() else True

    def close(self):
        fp = self.fp
        if fp:
            self.fp = None
            fp.close()
        return

    def isclosed(self):
        return self.fp is None

    def read(self, amt=None):
        if self.fp is None:
            return ''
        elif self._method == 'HEAD':
            self.close()
            return ''
        elif self.chunked:
            return self._read_chunked(amt)
        elif amt is None:
            if self.length is None:
                s = self.fp.read()
            else:
                try:
                    s = self._safe_read(self.length)
                except IncompleteRead:
                    self.close()
                    raise

                self.length = 0
            self.close()
            return s
        else:
            if self.length is not None:
                if amt > self.length:
                    amt = self.length
            s = self.fp.read(amt)
            if not s and amt:
                self.close()
            if self.length is not None:
                self.length -= len(s)
                if not self.length:
                    self.close()
            return s

    def _read_chunked(self, amt):
        chunk_left = self.chunk_left
        value = []
        while True:
            if chunk_left is None:
                line = self.fp.readline(_MAXLINE + 1)
                if len(line) > _MAXLINE:
                    raise LineTooLong('chunk size')
                i = line.find(';')
                if i >= 0:
                    line = line[:i]
                try:
                    chunk_left = int(line, 16)
                except ValueError:
                    self.close()
                    raise IncompleteRead(''.join(value))

                if chunk_left == 0:
                    break
            if amt is None:
                value.append(self._safe_read(chunk_left))
            else:
                if amt < chunk_left:
                    value.append(self._safe_read(amt))
                    self.chunk_left = chunk_left - amt
                    return ''.join(value)
                if amt == chunk_left:
                    value.append(self._safe_read(amt))
                    self._safe_read(2)
                    self.chunk_left = None
                    return ''.join(value)
                value.append(self._safe_read(chunk_left))
                amt -= chunk_left
            self._safe_read(2)
            chunk_left = None

        while True:
            line = self.fp.readline(_MAXLINE + 1)
            if len(line) > _MAXLINE:
                raise LineTooLong('trailer line')
            if not line:
                break
            if line == '\r\n':
                break

        self.close()
        return ''.join(value)

    def _safe_read(self, amt):
        s = []
        while amt > 0:
            chunk = self.fp.read(min(amt, MAXAMOUNT))
            if not chunk:
                raise IncompleteRead(''.join(s), amt)
            s.append(chunk)
            amt -= len(chunk)

        return ''.join(s)

    def fileno(self):
        return self.fp.fileno()

    def getheader(self, name, default=None):
        if self.msg is None:
            raise ResponseNotReady()
        return self.msg.getheader(name, default)

    def getheaders(self):
        if self.msg is None:
            raise ResponseNotReady()
        return self.msg.items()


class HTTPConnection():
    _http_vsn = 11
    _http_vsn_str = 'HTTP/1.1'
    response_class = HTTPResponse
    default_port = HTTP_PORT
    auto_open = 1
    debuglevel = 0
    strict = 0

    def __init__(self, host, port=None, strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None):
        self.timeout = timeout
        self.source_address = source_address
        self.sock = None
        self._buffer = []
        self.__response = None
        self.__state = _CS_IDLE
        self._method = None
        self._tunnel_host = None
        self._tunnel_port = None
        self._tunnel_headers = {}
        if strict is not None:
            self.strict = strict
        self.host, self.port = self._get_hostport(host, port)
        self._validate_host(self.host)
        self._create_connection = socket.create_connection
        return

    def set_tunnel(self, host, port=None, headers=None):
        if self.sock:
            raise RuntimeError("Can't setup tunnel for established connection.")
        self._tunnel_host, self._tunnel_port = self._get_hostport(host, port)
        if headers:
            self._tunnel_headers = headers
        else:
            self._tunnel_headers.clear()

    def _get_hostport(self, host, port):
        if port is None:
            i = host.rfind(':')
            j = host.rfind(']')
            if i > j:
                try:
                    port = int(host[i + 1:])
                except ValueError:
                    if host[i + 1:] == '':
                        port = self.default_port
                    else:
                        raise InvalidURL("nonnumeric port: '%s'" % host[i + 1:])

                host = host[:i]
            else:
                port = self.default_port
            if host and host[0] == '[' and host[-1] == ']':
                host = host[1:-1]
        return (host, port)

    def set_debuglevel(self, level):
        self.debuglevel = level

    def _tunnel(self):
        self.send('CONNECT %s:%d HTTP/1.0\r\n' % (self._tunnel_host, self._tunnel_port))
        for header, value in self._tunnel_headers.iteritems():
            self.send('%s: %s\r\n' % (header, value))

        self.send('\r\n')
        response = self.response_class(self.sock, strict=self.strict, method=self._method)
        version, code, message = response._read_status()
        if version == 'HTTP/0.9':
            self.close()
            raise socket.error('Invalid response from tunnel request')
        if code != 200:
            self.close()
            raise socket.error('Tunnel connection failed: %d %s' % (code, message.strip()))
        while True:
            line = response.fp.readline(_MAXLINE + 1)
            if len(line) > _MAXLINE:
                raise LineTooLong('header line')
            if not line:
                break
            if line == '\r\n':
                break

    def connect(self):
        self.sock = self._create_connection((self.host, self.port), self.timeout, self.source_address)
        if self._tunnel_host:
            self._tunnel()

    def close(self):
        self.__state = _CS_IDLE
        try:
            sock = self.sock
            if sock:
                self.sock = None
                sock.close()
        finally:
            response = self.__response
            if response:
                self.__response = None
                response.close()

        return

    def send(self, data):
        if self.sock is None:
            if self.auto_open:
                self.connect()
            else:
                raise NotConnected()
        if self.debuglevel > 0:
            print 'send:', repr(data)
        blocksize = 8192
        if hasattr(data, 'read') and not isinstance(data, array):
            if self.debuglevel > 0:
                print 'sendIng a read()able'
            datablock = data.read(blocksize)
            while datablock:
                self.sock.sendall(datablock)
                datablock = data.read(blocksize)

        else:
            self.sock.sendall(data)
        return

    def _output(self, s):
        self._buffer.append(s)

    def _send_output(self, message_body=None):
        self._buffer.extend(('', ''))
        msg = '\r\n'.join(self._buffer)
        del self._buffer[:]
        if isinstance(message_body, str):
            msg += message_body
            message_body = None
        self.send(msg)
        if message_body is not None:
            self.send(message_body)
        return

    def putrequest(self, method, url, skip_host=0, skip_accept_encoding=0):
        if self.__response and self.__response.isclosed():
            self.__response = None
        if self.__state == _CS_IDLE:
            self.__state = _CS_REQ_STARTED
        else:
            raise CannotSendRequest()
        self._method = method
        url = url or '/'
        self._validate_path(url)
        request = '%s %s %s' % (method, url, self._http_vsn_str)
        self._output(self._encode_request(request))
        if self._http_vsn == 11:
            if not skip_host:
                netloc = ''
                if url.startswith('http'):
                    nil, netloc, nil, nil, nil = urlsplit(url)
                if netloc:
                    try:
                        netloc_enc = netloc.encode('ascii')
                    except UnicodeEncodeError:
                        netloc_enc = netloc.encode('idna')

                    self.putheader('Host', netloc_enc)
                else:
                    if self._tunnel_host:
                        host = self._tunnel_host
                        port = self._tunnel_port
                    else:
                        host = self.host
                        port = self.port
                    try:
                        host_enc = host.encode('ascii')
                    except UnicodeEncodeError:
                        host_enc = host.encode('idna')

                    if host_enc.find(':') >= 0:
                        host_enc = '[' + host_enc + ']'
                    if port == self.default_port:
                        self.putheader('Host', host_enc)
                    else:
                        self.putheader('Host', '%s:%s' % (host_enc, port))
            if not skip_accept_encoding:
                self.putheader('Accept-Encoding', 'identity')
        return

    def _encode_request(self, request):
        return request

    def _validate_path(self, url):
        match = _contains_disallowed_url_pchar_re.search(url)
        if match:
            msg = "URL can't contain control characters. {url!r} (found at least {matched!r})".format(matched=match.group(), url=url)
            raise InvalidURL(msg)

    def _validate_host(self, host):
        match = _contains_disallowed_url_pchar_re.search(host)
        if match:
            msg = "URL can't contain control characters. {host!r} (found at least {matched!r})".format(matched=match.group(), host=host)
            raise InvalidURL(msg)

    def putheader(self, header, *values):
        if self.__state != _CS_REQ_STARTED:
            raise CannotSendHeader()
        header = '%s' % header
        if not _is_legal_header_name(header):
            raise ValueError('Invalid header name %r' % (header,))
        values = [ str(v) for v in values ]
        for one_value in values:
            if _is_illegal_header_value(one_value):
                raise ValueError('Invalid header value %r' % (one_value,))

        hdr = '%s: %s' % (header, '\r\n\t'.join(values))
        self._output(hdr)

    def endheaders(self, message_body=None):
        if self.__state == _CS_REQ_STARTED:
            self.__state = _CS_REQ_SENT
        else:
            raise CannotSendHeader()
        self._send_output(message_body)

    def request(self, method, url, body=None, headers={}):
        self._send_request(method, url, body, headers)

    def _set_content_length(self, body, method):
        thelen = None
        if body is None and method.upper() in _METHODS_EXPECTING_BODY:
            thelen = '0'
        elif body is not None:
            try:
                thelen = str(len(body))
            except (TypeError, AttributeError):
                try:
                    thelen = str(os.fstat(body.fileno()).st_size)
                except (AttributeError, OSError):
                    if self.debuglevel > 0:
                        print 'Cannot stat!!'

        if thelen is not None:
            self.putheader('Content-Length', thelen)
        return

    def _send_request(self, method, url, body, headers):
        header_names = dict.fromkeys([ k.lower() for k in headers ])
        skips = {}
        if 'host' in header_names:
            skips['skip_host'] = 1
        if 'accept-encoding' in header_names:
            skips['skip_accept_encoding'] = 1
        self.putrequest(method, url, **skips)
        if 'content-length' not in header_names:
            self._set_content_length(body, method)
        for hdr, value in headers.iteritems():
            self.putheader(hdr, value)

        self.endheaders(body)

    def getresponse(self, buffering=False):
        if self.__response and self.__response.isclosed():
            self.__response = None
        if self.__state != _CS_REQ_SENT or self.__response:
            raise ResponseNotReady()
        args = (self.sock,)
        kwds = {'strict': self.strict,
         'method': self._method}
        if self.debuglevel > 0:
            args += (self.debuglevel,)
        if buffering:
            kwds['buffering'] = True
        response = self.response_class(*args, **kwds)
        try:
            response.begin()
            self.__state = _CS_IDLE
            if response.will_close:
                self.close()
            else:
                self.__response = response
            return response
        except:
            response.close()
            raise

        return


class HTTP():
    _http_vsn = 10
    _http_vsn_str = 'HTTP/1.0'
    debuglevel = 0
    _connection_class = HTTPConnection

    def __init__(self, host='', port=None, strict=None):
        if port == 0:
            port = None
        self._setup(self._connection_class(host, port, strict))
        return

    def _setup(self, conn):
        self._conn = conn
        self.send = conn.send
        self.putrequest = conn.putrequest
        self.putheader = conn.putheader
        self.endheaders = conn.endheaders
        self.set_debuglevel = conn.set_debuglevel
        conn._http_vsn = self._http_vsn
        conn._http_vsn_str = self._http_vsn_str
        self.file = None
        return

    def connect(self, host=None, port=None):
        if host is not None:
            self._conn.host, self._conn.port = self._conn._get_hostport(host, port)
        self._conn.connect()
        return

    def getfile(self):
        return self.file

    def getreply(self, buffering=False):
        try:
            if not buffering:
                response = self._conn.getresponse()
            else:
                response = self._conn.getresponse(buffering)
        except BadStatusLine as e:
            self.file = self._conn.sock.makefile('rb', 0)
            self.close()
            self.headers = None
            return (-1, e.line, None)

        self.headers = response.msg
        self.file = response.fp
        return (response.status, response.reason, response.msg)

    def close(self):
        self._conn.close()
        self.file = None
        return


try:
    import ssl
except ImportError:
    pass
else:

    class HTTPSConnection(HTTPConnection):
        default_port = HTTPS_PORT

        def __init__(self, host, port=None, key_file=None, cert_file=None, strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, source_address=None, context=None):
            HTTPConnection.__init__(self, host, port, strict, timeout, source_address)
            self.key_file = key_file
            self.cert_file = cert_file
            if context is None:
                context = ssl._create_default_https_context()
            if key_file or cert_file:
                context.load_cert_chain(cert_file, key_file)
            self._context = context
            return

        def connect(self):
            HTTPConnection.connect(self)
            if self._tunnel_host:
                server_hostname = self._tunnel_host
            else:
                server_hostname = self.host
            self.sock = self._context.wrap_socket(self.sock, server_hostname=server_hostname)


    __all__.append('HTTPSConnection')

    class HTTPS(HTTP):
        _connection_class = HTTPSConnection

        def __init__(self, host='', port=None, key_file=None, cert_file=None, strict=None, context=None):
            if port == 0:
                port = None
            self._setup(self._connection_class(host, port, key_file, cert_file, strict, context=context))
            self.key_file = key_file
            self.cert_file = cert_file
            return


    def FakeSocket(sock, sslobj):
        warnings.warn("FakeSocket is deprecated, and won't be in 3.x.  " + 'Use the result of ssl.wrap_socket() directly instead.', DeprecationWarning, stacklevel=2)
        return sslobj


class HTTPException(Exception):
    pass


class NotConnected(HTTPException):
    pass


class InvalidURL(HTTPException):
    pass


class UnknownProtocol(HTTPException):

    def __init__(self, version):
        self.args = (version,)
        self.version = version


class UnknownTransferEncoding(HTTPException):
    pass


class UnimplementedFileMode(HTTPException):
    pass


class IncompleteRead(HTTPException):

    def __init__(self, partial, expected=None):
        self.args = (partial,)
        self.partial = partial
        self.expected = expected

    def __repr__(self):
        if self.expected is not None:
            e = ', %i more expected' % self.expected
        else:
            e = ''
        return 'IncompleteRead(%i bytes read%s)' % (len(self.partial), e)

    def __str__(self):
        return repr(self)


class ImproperConnectionState(HTTPException):
    pass


class CannotSendRequest(ImproperConnectionState):
    pass


class CannotSendHeader(ImproperConnectionState):
    pass


class ResponseNotReady(ImproperConnectionState):
    pass


class BadStatusLine(HTTPException):

    def __init__(self, line):
        if not line:
            line = repr(line)
        self.args = (line,)
        self.line = line


class LineTooLong(HTTPException):

    def __init__(self, line_type):
        HTTPException.__init__(self, 'got more than %d bytes when reading %s' % (_MAXLINE, line_type))


error = HTTPException

class LineAndFileWrapper():

    def __init__(self, line, file):
        self._line = line
        self._file = file
        self._line_consumed = 0
        self._line_offset = 0
        self._line_left = len(line)

    def __getattr__(self, attr):
        return getattr(self._file, attr)

    def _done(self):
        self._line_consumed = 1
        self.read = self._file.read
        self.readline = self._file.readline
        self.readlines = self._file.readlines

    def read(self, amt=None):
        if self._line_consumed:
            return self._file.read(amt)
        else:
            if amt is None or amt > self._line_left:
                s = self._line[self._line_offset:]
                self._done()
                if amt is None:
                    return s + self._file.read()
                else:
                    return s + self._file.read(amt - len(s))
            else:
                i = self._line_offset
                j = i + amt
                s = self._line[i:j]
                self._line_offset = j
                self._line_left -= amt
                if self._line_left == 0:
                    self._done()
                return s
            return

    def readline(self):
        if self._line_consumed:
            return self._file.readline()
        s = self._line[self._line_offset:]
        self._done()
        return s

    def readlines(self, size=None):
        if self._line_consumed:
            return self._file.readlines(size)
        else:
            L = [self._line[self._line_offset:]]
            self._done()
            if size is None:
                return L + self._file.readlines()
            return L + self._file.readlines(size)
            return
