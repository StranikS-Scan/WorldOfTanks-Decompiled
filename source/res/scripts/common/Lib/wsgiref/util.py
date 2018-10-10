# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/wsgiref/util.py
import posixpath
__all__ = ['FileWrapper',
 'guess_scheme',
 'application_uri',
 'request_uri',
 'shift_path_info',
 'setup_testing_defaults']

class FileWrapper:

    def __init__(self, filelike, blksize=8192):
        self.filelike = filelike
        self.blksize = blksize
        if hasattr(filelike, 'close'):
            self.close = filelike.close

    def __getitem__(self, key):
        data = self.filelike.read(self.blksize)
        if data:
            return data
        raise IndexError

    def __iter__(self):
        return self

    def next(self):
        data = self.filelike.read(self.blksize)
        if data:
            return data
        raise StopIteration


def guess_scheme(environ):
    if environ.get('HTTPS') in ('yes', 'on', '1'):
        return 'https'
    else:
        return 'http'


def application_uri(environ):
    url = environ['wsgi.url_scheme'] + '://'
    from urllib import quote
    if environ.get('HTTP_HOST'):
        url += environ['HTTP_HOST']
    else:
        url += environ['SERVER_NAME']
        if environ['wsgi.url_scheme'] == 'https':
            if environ['SERVER_PORT'] != '443':
                url += ':' + environ['SERVER_PORT']
        elif environ['SERVER_PORT'] != '80':
            url += ':' + environ['SERVER_PORT']
    url += quote(environ.get('SCRIPT_NAME') or '/')
    return url


def request_uri(environ, include_query=1):
    url = application_uri(environ)
    from urllib import quote
    path_info = quote(environ.get('PATH_INFO', ''), safe='/;=,')
    if not environ.get('SCRIPT_NAME'):
        url += path_info[1:]
    else:
        url += path_info
    if include_query and environ.get('QUERY_STRING'):
        url += '?' + environ['QUERY_STRING']
    return url


def shift_path_info(environ):
    path_info = environ.get('PATH_INFO', '')
    if not path_info:
        return
    else:
        path_parts = path_info.split('/')
        path_parts[1:-1] = [ p for p in path_parts[1:-1] if p and p != '.' ]
        name = path_parts[1]
        del path_parts[1]
        script_name = environ.get('SCRIPT_NAME', '')
        script_name = posixpath.normpath(script_name + '/' + name)
        if script_name.endswith('/'):
            script_name = script_name[:-1]
        if not name and not script_name.endswith('/'):
            script_name += '/'
        environ['SCRIPT_NAME'] = script_name
        environ['PATH_INFO'] = '/'.join(path_parts)
        if name == '.':
            name = None
        return name


def setup_testing_defaults(environ):
    environ.setdefault('SERVER_NAME', '127.0.0.1')
    environ.setdefault('SERVER_PROTOCOL', 'HTTP/1.0')
    environ.setdefault('HTTP_HOST', environ['SERVER_NAME'])
    environ.setdefault('REQUEST_METHOD', 'GET')
    if 'SCRIPT_NAME' not in environ and 'PATH_INFO' not in environ:
        environ.setdefault('SCRIPT_NAME', '')
        environ.setdefault('PATH_INFO', '/')
    environ.setdefault('wsgi.version', (1, 0))
    environ.setdefault('wsgi.run_once', 0)
    environ.setdefault('wsgi.multithread', 0)
    environ.setdefault('wsgi.multiprocess', 0)
    from StringIO import StringIO
    environ.setdefault('wsgi.input', StringIO(''))
    environ.setdefault('wsgi.errors', StringIO())
    environ.setdefault('wsgi.url_scheme', guess_scheme(environ))
    if environ['wsgi.url_scheme'] == 'http':
        environ.setdefault('SERVER_PORT', '80')
    elif environ['wsgi.url_scheme'] == 'https':
        environ.setdefault('SERVER_PORT', '443')


_hoppish = {'connection': 1,
 'keep-alive': 1,
 'proxy-authenticate': 1,
 'proxy-authorization': 1,
 'te': 1,
 'trailers': 1,
 'transfer-encoding': 1,
 'upgrade': 1}.__contains__

def is_hop_by_hop(header_name):
    return _hoppish(header_name.lower())
