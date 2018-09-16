# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/wsgiref/handlers.py
from types import StringType
from util import FileWrapper, guess_scheme, is_hop_by_hop
from headers import Headers
import sys, os, time
__all__ = ['BaseHandler',
 'SimpleHandler',
 'BaseCGIHandler',
 'CGIHandler']
try:
    dict
except NameError:

    def dict(items):
        d = {}
        for k, v in items:
            d[k] = v

        return d


_weekdayname = ['Mon',
 'Tue',
 'Wed',
 'Thu',
 'Fri',
 'Sat',
 'Sun']
_monthname = [None,
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

def format_date_time(timestamp):
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    return '%s, %02d %3s %4d %02d:%02d:%02d GMT' % (_weekdayname[wd],
     day,
     _monthname[month],
     year,
     hh,
     mm,
     ss)


class BaseHandler():
    wsgi_version = (1, 0)
    wsgi_multithread = True
    wsgi_multiprocess = True
    wsgi_run_once = False
    origin_server = True
    http_version = '1.0'
    server_software = None
    os_environ = dict(os.environ.items())
    wsgi_file_wrapper = FileWrapper
    headers_class = Headers
    traceback_limit = None
    error_status = '500 Internal Server Error'
    error_headers = [('Content-Type', 'text/plain')]
    error_body = 'A server error occurred.  Please contact the administrator.'
    status = result = None
    headers_sent = False
    headers = None
    bytes_sent = 0

    def run(self, application):
        try:
            self.setup_environ()
            self.result = application(self.environ, self.start_response)
            self.finish_response()
        except:
            try:
                self.handle_error()
            except:
                self.close()
                raise

    def setup_environ(self):
        env = self.environ = self.os_environ.copy()
        self.add_cgi_vars()
        env['wsgi.input'] = self.get_stdin()
        env['wsgi.errors'] = self.get_stderr()
        env['wsgi.version'] = self.wsgi_version
        env['wsgi.run_once'] = self.wsgi_run_once
        env['wsgi.url_scheme'] = self.get_scheme()
        env['wsgi.multithread'] = self.wsgi_multithread
        env['wsgi.multiprocess'] = self.wsgi_multiprocess
        if self.wsgi_file_wrapper is not None:
            env['wsgi.file_wrapper'] = self.wsgi_file_wrapper
        if self.origin_server and self.server_software:
            env.setdefault('SERVER_SOFTWARE', self.server_software)
        return

    def finish_response(self):
        try:
            if not self.result_is_file() or not self.sendfile():
                for data in self.result:
                    self.write(data)

                self.finish_content()
        finally:
            self.close()

    def get_scheme(self):
        return guess_scheme(self.environ)

    def set_content_length(self):
        try:
            blocks = len(self.result)
        except (TypeError, AttributeError, NotImplementedError):
            pass
        else:
            if blocks == 1:
                self.headers['Content-Length'] = str(self.bytes_sent)
                return

    def cleanup_headers(self):
        if 'Content-Length' not in self.headers:
            self.set_content_length()

    def start_response(self, status, headers, exc_info=None):
        if exc_info:
            try:
                if self.headers_sent:
                    raise exc_info[0], exc_info[1], exc_info[2]
            finally:
                exc_info = None

        elif self.headers is not None:
            raise AssertionError('Headers already set!')
        self.status = status
        self.headers = self.headers_class(headers)
        return self.write

    def send_preamble(self):
        if self.origin_server:
            if self.client_is_modern():
                self._write('HTTP/%s %s\r\n' % (self.http_version, self.status))
                if 'Date' not in self.headers:
                    self._write('Date: %s\r\n' % format_date_time(time.time()))
                if self.server_software and 'Server' not in self.headers:
                    self._write('Server: %s\r\n' % self.server_software)
        else:
            self._write('Status: %s\r\n' % self.status)

    def write(self, data):
        if not self.status:
            raise AssertionError('write() before start_response()')
        elif not self.headers_sent:
            self.bytes_sent = len(data)
            self.send_headers()
        else:
            self.bytes_sent += len(data)
        self._write(data)
        self._flush()

    def sendfile(self):
        return False

    def finish_content(self):
        if not self.headers_sent:
            self.headers.setdefault('Content-Length', '0')
            self.send_headers()

    def close(self):
        try:
            if hasattr(self.result, 'close'):
                self.result.close()
        finally:
            self.result = self.headers = self.status = self.environ = None
            self.bytes_sent = 0
            self.headers_sent = False

        return

    def send_headers(self):
        self.cleanup_headers()
        self.headers_sent = True
        if not self.origin_server or self.client_is_modern():
            self.send_preamble()
            self._write(str(self.headers))

    def result_is_file(self):
        wrapper = self.wsgi_file_wrapper
        return wrapper is not None and isinstance(self.result, wrapper)

    def client_is_modern(self):
        return self.environ['SERVER_PROTOCOL'].upper() != 'HTTP/0.9'

    def log_exception(self, exc_info):
        try:
            from traceback import print_exception
            stderr = self.get_stderr()
            print_exception(exc_info[0], exc_info[1], exc_info[2], self.traceback_limit, stderr)
            stderr.flush()
        finally:
            exc_info = None

        return

    def handle_error(self):
        self.log_exception(sys.exc_info())
        if not self.headers_sent:
            self.result = self.error_output(self.environ, self.start_response)
            self.finish_response()

    def error_output(self, environ, start_response):
        start_response(self.error_status, self.error_headers[:], sys.exc_info())
        return [self.error_body]

    def _write(self, data):
        raise NotImplementedError

    def _flush(self):
        raise NotImplementedError

    def get_stdin(self):
        raise NotImplementedError

    def get_stderr(self):
        raise NotImplementedError

    def add_cgi_vars(self):
        raise NotImplementedError


class SimpleHandler(BaseHandler):

    def __init__(self, stdin, stdout, stderr, environ, multithread=True, multiprocess=False):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.base_env = environ
        self.wsgi_multithread = multithread
        self.wsgi_multiprocess = multiprocess

    def get_stdin(self):
        return self.stdin

    def get_stderr(self):
        return self.stderr

    def add_cgi_vars(self):
        self.environ.update(self.base_env)

    def _write(self, data):
        self.stdout.write(data)
        self._write = self.stdout.write

    def _flush(self):
        self.stdout.flush()
        self._flush = self.stdout.flush


class BaseCGIHandler(SimpleHandler):
    origin_server = False


class CGIHandler(BaseCGIHandler):
    wsgi_run_once = True
    os_environ = {}

    def __init__(self):
        BaseCGIHandler.__init__(self, sys.stdin, sys.stdout, sys.stderr, dict(os.environ.items()), multithread=False, multiprocess=True)
