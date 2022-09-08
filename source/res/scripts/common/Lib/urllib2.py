# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/urllib2.py
# Compiled at: 2032-11-03 08:27:42
"""An extensible library for opening URLs using a variety of protocols

The simplest way to use this module is to call the urlopen function,
which accepts a string containing a URL or a Request object (described
below).  It opens the URL and returns the results as file-like
object; the returned object has some extra methods described below.

The OpenerDirector manages a collection of Handler objects that do
all the actual work.  Each Handler implements a particular protocol or
option.  The OpenerDirector is a composite object that invokes the
Handlers needed to open the requested URL.  For example, the
HTTPHandler performs HTTP GET and POST requests and deals with
non-error returns.  The HTTPRedirectHandler automatically deals with
HTTP 301, 302, 303 and 307 redirect errors, and the HTTPDigestAuthHandler
deals with digest authentication.

urlopen(url, data=None) -- Basic usage is the same as original
urllib.  pass the url and optionally data to post to an HTTP URL, and
get a file-like object back.  One difference is that you can also pass
a Request instance instead of URL.  Raises a URLError (subclass of
IOError); for HTTP errors, raises an HTTPError, which can also be
treated as a valid response.

build_opener -- Function that creates a new OpenerDirector instance.
Will install the default handlers.  Accepts one or more Handlers as
arguments, either instances or Handler classes that it will
instantiate.  If one of the argument is a subclass of the default
handler, the argument will be installed instead of the default.

install_opener -- Installs a new opener as the default opener.

objects of interest:

OpenerDirector -- Sets up the User Agent as the Python-urllib client and manages
the Handler classes, while dealing with requests and responses.

Request -- An object that encapsulates the state of a request.  The
state can be as simple as the URL.  It can also include extra HTTP
headers, e.g. a User-Agent.

BaseHandler --

exceptions:
URLError -- A subclass of IOError, individual protocols have their own
specific subclass.

HTTPError -- Also a valid HTTP response, so you can treat an HTTP error
as an exceptional event or valid response.

internals:
BaseHandler and parent
_call_chain conventions

Example usage:

import urllib2

# set up authentication info
authinfo = urllib2.HTTPBasicAuthHandler()
authinfo.add_password(realm='PDQ Application',
                      uri='https://mahler:8092/site-updates.py',
                      user='klem',
                      passwd='geheim$parole')

proxy_support = urllib2.ProxyHandler({"http" : "http://ahad-haam:3128"})

# build a new opener that adds authentication and caching FTP handlers
opener = urllib2.build_opener(proxy_support, authinfo, urllib2.CacheFTPHandler)

# install it
urllib2.install_opener(opener)

f = urllib2.urlopen('http://www.python.org/')


"""
import base64
import hashlib
import httplib
import mimetools
import os
import posixpath
import random
import re
import socket
import sys
import time
import urlparse
import bisect
import warnings
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    import ssl
except ImportError:
    _have_ssl = False
else:
    _have_ssl = True

from urllib import unwrap, unquote, splittype, splithost, quote, addinfourl, splitport, splittag, toBytes, splitattr, ftpwrapper, splituser, splitpasswd, splitvalue
from urllib import localhost, url2pathname, getproxies, proxy_bypass
__version__ = sys.version[:3]
_opener = None

def urlopen(url, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, cafile=None, capath=None, cadefault=False, context=None):
    global _opener
    if cafile or capath or cadefault:
        if context is not None:
            raise ValueError("You can't pass both context and any of cafile, capath, and cadefault")
        if not _have_ssl:
            raise ValueError('SSL support not available')
        context = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=cafile, capath=capath)
        https_handler = HTTPSHandler(context=context)
        opener = build_opener(https_handler)
    elif context:
        https_handler = HTTPSHandler(context=context)
        opener = build_opener(https_handler)
    elif _opener is None:
        _opener = opener = build_opener()
    else:
        opener = _opener
    return opener.open(url, data, timeout)


def install_opener(opener):
    global _opener
    _opener = opener


class URLError(IOError):

    def __init__(self, reason):
        self.args = (reason,)
        self.reason = reason

    def __str__(self):
        return '<urlopen error %s>' % self.reason


class HTTPError(URLError, addinfourl):
    """Raised when HTTP error occurs, but also acts like non-error return"""
    __super_init = addinfourl.__init__

    def __init__(self, url, code, msg, hdrs, fp):
        self.code = code
        self.msg = msg
        self.hdrs = hdrs
        self.fp = fp
        self.filename = url
        if fp is not None:
            self.__super_init(fp, hdrs, url, code)
        return

    def __str__(self):
        return 'HTTP Error %s: %s' % (self.code, self.msg)

    @property
    def reason(self):
        return self.msg

    def info(self):
        return self.hdrs


_cut_port_re = re.compile(':\\d+$')

def request_host(request):
    """Return request-host, as defined by RFC 2965.
    
    Variation from RFC: returned value is lowercased, for convenient
    comparison.
    
    """
    url = request.get_full_url()
    host = urlparse.urlparse(url)[1]
    if host == '':
        host = request.get_header('Host', '')
    host = _cut_port_re.sub('', host, 1)
    return host.lower()


class Request:

    def __init__(self, url, data=None, headers={}, origin_req_host=None, unverifiable=False):
        self.__original = unwrap(url)
        self.__original, self.__fragment = splittag(self.__original)
        self.type = None
        self.host = None
        self.port = None
        self._tunnel_host = None
        self.data = data
        self.headers = {}
        for key, value in headers.items():
            self.add_header(key, value)

        self.unredirected_hdrs = {}
        if origin_req_host is None:
            origin_req_host = request_host(self)
        self.origin_req_host = origin_req_host
        self.unverifiable = unverifiable
        return

    def __getattr__(self, attr):
        if attr in ('_Request__r_type', '_Request__r_host'):
            getattr(self, 'get_' + attr[12:])()
            return self.__dict__[attr]
        raise AttributeError, attr

    def get_method(self):
        if self.has_data():
            return 'POST'
        else:
            return 'GET'

    def add_data(self, data):
        self.data = data

    def has_data(self):
        return self.data is not None

    def get_data(self):
        return self.data

    def get_full_url(self):
        if self.__fragment:
            return '%s#%s' % (self.__original, self.__fragment)
        else:
            return self.__original

    def get_type(self):
        if self.type is None:
            self.type, self.__r_type = splittype(self.__original)
            if self.type is None:
                raise ValueError, 'unknown url type: %s' % self.__original
        return self.type

    def get_host(self):
        if self.host is None:
            self.host, self.__r_host = splithost(self.__r_type)
            if self.host:
                self.host = unquote(self.host)
        return self.host

    def get_selector(self):
        return self.__r_host

    def set_proxy(self, host, type):
        if self.type == 'https' and not self._tunnel_host:
            self._tunnel_host = self.host
        else:
            self.type = type
            self.__r_host = self.__original
        self.host = host

    def has_proxy(self):
        return self.__r_host == self.__original

    def get_origin_req_host(self):
        return self.origin_req_host

    def is_unverifiable(self):
        return self.unverifiable

    def add_header(self, key, val):
        self.headers[key.capitalize()] = val

    def add_unredirected_header(self, key, val):
        self.unredirected_hdrs[key.capitalize()] = val

    def has_header(self, header_name):
        return header_name in self.headers or header_name in self.unredirected_hdrs

    def get_header(self, header_name, default=None):
        return self.headers.get(header_name, self.unredirected_hdrs.get(header_name, default))

    def header_items(self):
        hdrs = self.unredirected_hdrs.copy()
        hdrs.update(self.headers)
        return hdrs.items()


class OpenerDirector:

    def __init__(self):
        client_version = 'Python-urllib/%s' % __version__
        self.addheaders = [('User-agent', client_version)]
        self.handlers = []
        self.handle_open = {}
        self.handle_error = {}
        self.process_response = {}
        self.process_request = {}

    def add_handler(self, handler):
        if not hasattr(handler, 'add_parent'):
            raise TypeError('expected BaseHandler instance, got %r' % type(handler))
        added = False
        for meth in dir(handler):
            if meth in ('redirect_request', 'do_open', 'proxy_open'):
                continue
            i = meth.find('_')
            protocol = meth[:i]
            condition = meth[i + 1:]
            if condition.startswith('error'):
                j = condition.find('_') + i + 1
                kind = meth[j + 1:]
                try:
                    kind = int(kind)
                except ValueError:
                    pass

                lookup = self.handle_error.get(protocol, {})
                self.handle_error[protocol] = lookup
            elif condition == 'open':
                kind = protocol
                lookup = self.handle_open
            elif condition == 'response':
                kind = protocol
                lookup = self.process_response
            elif condition == 'request':
                kind = protocol
                lookup = self.process_request
            else:
                continue
            handlers = lookup.setdefault(kind, [])
            if handlers:
                bisect.insort(handlers, handler)
            else:
                handlers.append(handler)
            added = True

        if added:
            bisect.insort(self.handlers, handler)
            handler.add_parent(self)

    def close(self):
        pass

    def _call_chain(self, chain, kind, meth_name, *args):
        handlers = chain.get(kind, ())
        for handler in handlers:
            func = getattr(handler, meth_name)
            result = func(*args)
            if result is not None:
                return result

        return

    def open(self, fullurl, data=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        if isinstance(fullurl, basestring):
            req = Request(fullurl, data)
        else:
            req = fullurl
            if data is not None:
                req.add_data(data)
        req.timeout = timeout
        protocol = req.get_type()
        meth_name = protocol + '_request'
        for processor in self.process_request.get(protocol, []):
            meth = getattr(processor, meth_name)
            req = meth(req)

        response = self._open(req, data)
        meth_name = protocol + '_response'
        for processor in self.process_response.get(protocol, []):
            meth = getattr(processor, meth_name)
            response = meth(req, response)

        return response

    def _open(self, req, data=None):
        result = self._call_chain(self.handle_open, 'default', 'default_open', req)
        if result:
            return result
        protocol = req.get_type()
        result = self._call_chain(self.handle_open, protocol, protocol + '_open', req)
        return result if result else self._call_chain(self.handle_open, 'unknown', 'unknown_open', req)

    def error(self, proto, *args):
        if proto in ('http', 'https'):
            dict = self.handle_error['http']
            proto = args[2]
            meth_name = 'http_error_%s' % proto
            http_err = 1
            orig_args = args
        else:
            dict = self.handle_error
            meth_name = proto + '_error'
            http_err = 0
        args = (dict, proto, meth_name) + args
        result = self._call_chain(*args)
        if result:
            return result
        if http_err:
            args = (dict, 'default', 'http_error_default') + orig_args
            return self._call_chain(*args)


def build_opener(*handlers):
    """Create an opener object from a list of handlers.
    
    The opener will use several default handlers, including support
    for HTTP, FTP and when applicable, HTTPS.
    
    If any of the handlers passed as arguments are subclasses of the
    default handlers, the default handlers will not be used.
    """
    import types

    def isclass(obj):
        return isinstance(obj, (types.ClassType, type))

    opener = OpenerDirector()
    default_classes = [ProxyHandler,
     UnknownHandler,
     HTTPHandler,
     HTTPDefaultErrorHandler,
     HTTPRedirectHandler,
     FTPHandler,
     FileHandler,
     HTTPErrorProcessor]
    if hasattr(httplib, 'HTTPS'):
        default_classes.append(HTTPSHandler)
    skip = set()
    for klass in default_classes:
        for check in handlers:
            if isclass(check):
                if issubclass(check, klass):
                    skip.add(klass)
            if isinstance(check, klass):
                skip.add(klass)

    for klass in skip:
        default_classes.remove(klass)

    for klass in default_classes:
        opener.add_handler(klass())

    for h in handlers:
        if isclass(h):
            h = h()
        opener.add_handler(h)

    return opener


class BaseHandler:
    handler_order = 500

    def add_parent(self, parent):
        self.parent = parent

    def close(self):
        pass

    def __lt__(self, other):
        return True if not hasattr(other, 'handler_order') else self.handler_order < other.handler_order


class HTTPErrorProcessor(BaseHandler):
    """Process HTTP error responses."""
    handler_order = 1000

    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()
        if not 200 <= code < 300:
            response = self.parent.error('http', request, response, code, msg, hdrs)
        return response

    https_response = http_response


class HTTPDefaultErrorHandler(BaseHandler):

    def http_error_default(self, req, fp, code, msg, hdrs):
        raise HTTPError(req.get_full_url(), code, msg, hdrs, fp)


class HTTPRedirectHandler(BaseHandler):
    max_repeats = 4
    max_redirections = 10

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        """Return a Request or None in response to a redirect.
        
        This is called by the http_error_30x methods when a
        redirection response is received.  If a redirection should
        take place, return a new Request to allow http_error_30x to
        perform the redirect.  Otherwise, raise HTTPError if no-one
        else should try to handle this url.  Return None if you can't
        but another Handler might.
        """
        m = req.get_method()
        if code in (301, 302, 303, 307) and m in ('GET', 'HEAD') or code in (301, 302, 303) and m == 'POST':
            newurl = newurl.replace(' ', '%20')
            newheaders = dict(((k, v) for k, v in req.headers.items() if k.lower() not in ('content-length', 'content-type')))
            return Request(newurl, headers=newheaders, origin_req_host=req.get_origin_req_host(), unverifiable=True)
        raise HTTPError(req.get_full_url(), code, msg, headers, fp)

    def http_error_302(self, req, fp, code, msg, headers):
        if 'location' in headers:
            newurl = headers.getheaders('location')[0]
        elif 'uri' in headers:
            newurl = headers.getheaders('uri')[0]
        else:
            return
        urlparts = urlparse.urlparse(newurl)
        if not urlparts.path and urlparts.netloc:
            urlparts = list(urlparts)
            urlparts[2] = '/'
        newurl = urlparse.urlunparse(urlparts)
        newurl = urlparse.urljoin(req.get_full_url(), newurl)
        newurl_lower = newurl.lower()
        if not (newurl_lower.startswith('http://') or newurl_lower.startswith('https://') or newurl_lower.startswith('ftp://')):
            raise HTTPError(newurl, code, msg + " - Redirection to url '%s' is not allowed" % newurl, headers, fp)
        new = self.redirect_request(req, fp, code, msg, headers, newurl)
        if new is None:
            return
        else:
            if hasattr(req, 'redirect_dict'):
                visited = new.redirect_dict = req.redirect_dict
                if visited.get(newurl, 0) >= self.max_repeats or len(visited) >= self.max_redirections:
                    raise HTTPError(req.get_full_url(), code, self.inf_msg + msg, headers, fp)
            else:
                visited = new.redirect_dict = req.redirect_dict = {}
            visited[newurl] = visited.get(newurl, 0) + 1
            fp.read()
            fp.close()
            return self.parent.open(new, timeout=req.timeout)

    http_error_301 = http_error_303 = http_error_307 = http_error_302
    inf_msg = 'The HTTP server returned a redirect error that would lead to an infinite loop.\nThe last 30x error message was:\n'


def _parse_proxy(proxy):
    """Return (scheme, user, password, host/port) given a URL or an authority.
    
    If a URL is supplied, it must have an authority (host:port) component.
    According to RFC 3986, having an authority component means the URL must
    have two slashes after the scheme:
    
    >>> _parse_proxy('file:/ftp.example.com/')
    Traceback (most recent call last):
    ValueError: proxy URL with no authority: 'file:/ftp.example.com/'
    
    The first three items of the returned tuple may be None.
    
    Examples of authority parsing:
    
    >>> _parse_proxy('proxy.example.com')
    (None, None, None, 'proxy.example.com')
    >>> _parse_proxy('proxy.example.com:3128')
    (None, None, None, 'proxy.example.com:3128')
    
    The authority component may optionally include userinfo (assumed to be
    username:password):
    
    >>> _parse_proxy('joe:password@proxy.example.com')
    (None, 'joe', 'password', 'proxy.example.com')
    >>> _parse_proxy('joe:password@proxy.example.com:3128')
    (None, 'joe', 'password', 'proxy.example.com:3128')
    
    Same examples, but with URLs instead:
    
    >>> _parse_proxy('http://proxy.example.com/')
    ('http', None, None, 'proxy.example.com')
    >>> _parse_proxy('http://proxy.example.com:3128/')
    ('http', None, None, 'proxy.example.com:3128')
    >>> _parse_proxy('http://joe:password@proxy.example.com/')
    ('http', 'joe', 'password', 'proxy.example.com')
    >>> _parse_proxy('http://joe:password@proxy.example.com:3128')
    ('http', 'joe', 'password', 'proxy.example.com:3128')
    
    Everything after the authority is ignored:
    
    >>> _parse_proxy('ftp://joe:password@proxy.example.com/rubbish:3128')
    ('ftp', 'joe', 'password', 'proxy.example.com')
    
    Test for no trailing '/' case:
    
    >>> _parse_proxy('http://joe:password@proxy.example.com')
    ('http', 'joe', 'password', 'proxy.example.com')
    
    """
    scheme, r_scheme = splittype(proxy)
    if not r_scheme.startswith('/'):
        scheme = None
        authority = proxy
    else:
        if not r_scheme.startswith('//'):
            raise ValueError('proxy URL with no authority: %r' % proxy)
        end = r_scheme.find('/', 2)
        if end == -1:
            end = None
        authority = r_scheme[2:end]
    userinfo, hostport = splituser(authority)
    if userinfo is not None:
        user, password = splitpasswd(userinfo)
    else:
        user = password = None
    return (scheme,
     user,
     password,
     hostport)


class ProxyHandler(BaseHandler):
    handler_order = 100

    def __init__(self, proxies=None):
        if proxies is None:
            proxies = getproxies()
        assert hasattr(proxies, 'has_key'), 'proxies must be a mapping'
        self.proxies = proxies
        for type, url in proxies.items():
            setattr(self, '%s_open' % type, lambda r, proxy=url, type=type, meth=self.proxy_open: meth(r, proxy, type))

        return

    def proxy_open(self, req, proxy, type):
        orig_type = req.get_type()
        proxy_type, user, password, hostport = _parse_proxy(proxy)
        if proxy_type is None:
            proxy_type = orig_type
        if req.host and proxy_bypass(req.host):
            return
        else:
            if user and password:
                user_pass = '%s:%s' % (unquote(user), unquote(password))
                creds = base64.b64encode(user_pass).strip()
                req.add_header('Proxy-authorization', 'Basic ' + creds)
            hostport = unquote(hostport)
            req.set_proxy(hostport, proxy_type)
            if orig_type == proxy_type or orig_type == 'https':
                return
            return self.parent.open(req, timeout=req.timeout)
            return


class HTTPPasswordMgr:

    def __init__(self):
        self.passwd = {}

    def add_password(self, realm, uri, user, passwd):
        if isinstance(uri, basestring):
            uri = [uri]
        if realm not in self.passwd:
            self.passwd[realm] = {}
        for default_port in (True, False):
            reduced_uri = tuple([ self.reduce_uri(u, default_port) for u in uri ])
            self.passwd[realm][reduced_uri] = (user, passwd)

    def find_user_password(self, realm, authuri):
        domains = self.passwd.get(realm, {})
        for default_port in (True, False):
            reduced_authuri = self.reduce_uri(authuri, default_port)
            for uris, authinfo in domains.iteritems():
                for uri in uris:
                    if self.is_suburi(uri, reduced_authuri):
                        return authinfo

        return (None, None)

    def reduce_uri(self, uri, default_port=True):
        """Accept authority or URI and extract only the authority and path."""
        parts = urlparse.urlsplit(uri)
        if parts[1]:
            scheme = parts[0]
            authority = parts[1]
            path = parts[2] or '/'
        else:
            scheme = None
            authority = uri
            path = '/'
        host, port = splitport(authority)
        if default_port and port is None and scheme is not None:
            dport = {'http': 80,
             'https': 443}.get(scheme)
            if dport is not None:
                authority = '%s:%d' % (host, dport)
        return (authority, path)

    def is_suburi(self, base, test):
        """Check if test is below base in a URI tree
        
        Both args must be URIs in reduced form.
        """
        if base == test:
            return True
        if base[0] != test[0]:
            return False
        common = posixpath.commonprefix((base[1], test[1]))
        return True if len(common) == len(base[1]) else False


class HTTPPasswordMgrWithDefaultRealm(HTTPPasswordMgr):

    def find_user_password(self, realm, authuri):
        user, password = HTTPPasswordMgr.find_user_password(self, realm, authuri)
        return (user, password) if user is not None else HTTPPasswordMgr.find_user_password(self, None, authuri)


class AbstractBasicAuthHandler:
    rx = re.compile('(?:.*,)*[ \t]*([^ \t]+)[ \t]+realm=(["\']?)([^"\']*)\\2', re.I)

    def __init__(self, password_mgr=None):
        if password_mgr is None:
            password_mgr = HTTPPasswordMgr()
        self.passwd = password_mgr
        self.add_password = self.passwd.add_password
        return

    def http_error_auth_reqed(self, authreq, host, req, headers):
        authreq = headers.get(authreq, None)
        if authreq:
            mo = AbstractBasicAuthHandler.rx.search(authreq)
            if mo:
                scheme, quote, realm = mo.groups()
                if quote not in ('"', "'"):
                    warnings.warn('Basic Auth Realm was unquoted', UserWarning, 2)
                if scheme.lower() == 'basic':
                    return self.retry_http_basic_auth(host, req, realm)
        return

    def retry_http_basic_auth(self, host, req, realm):
        user, pw = self.passwd.find_user_password(realm, host)
        if pw is not None:
            raw = '%s:%s' % (user, pw)
            auth = 'Basic %s' % base64.b64encode(raw).strip()
            if req.get_header(self.auth_header, None) == auth:
                return
            req.add_unredirected_header(self.auth_header, auth)
            return self.parent.open(req, timeout=req.timeout)
        else:
            return
            return


class HTTPBasicAuthHandler(AbstractBasicAuthHandler, BaseHandler):
    auth_header = 'Authorization'

    def http_error_401(self, req, fp, code, msg, headers):
        url = req.get_full_url()
        response = self.http_error_auth_reqed('www-authenticate', url, req, headers)
        return response


class ProxyBasicAuthHandler(AbstractBasicAuthHandler, BaseHandler):
    auth_header = 'Proxy-authorization'

    def http_error_407(self, req, fp, code, msg, headers):
        authority = req.get_host()
        response = self.http_error_auth_reqed('proxy-authenticate', authority, req, headers)
        return response


def randombytes(n):
    """Return n random bytes."""
    if os.path.exists('/dev/urandom'):
        f = open('/dev/urandom')
        s = f.read(n)
        f.close()
        return s
    else:
        L = [ chr(random.randrange(0, 256)) for i in range(n) ]
        return ''.join(L)


class AbstractDigestAuthHandler:

    def __init__(self, passwd=None):
        if passwd is None:
            passwd = HTTPPasswordMgr()
        self.passwd = passwd
        self.add_password = self.passwd.add_password
        self.retried = 0
        self.nonce_count = 0
        self.last_nonce = None
        return

    def reset_retry_count(self):
        self.retried = 0

    def http_error_auth_reqed(self, auth_header, host, req, headers):
        authreq = headers.get(auth_header, None)
        if self.retried > 5:
            raise HTTPError(req.get_full_url(), 401, 'digest auth failed', headers, None)
        else:
            self.retried += 1
        if authreq:
            scheme = authreq.split()[0]
            if scheme.lower() == 'digest':
                return self.retry_http_digest_auth(req, authreq)
        return

    def retry_http_digest_auth(self, req, auth):
        token, challenge = auth.split(' ', 1)
        chal = parse_keqv_list(parse_http_list(challenge))
        auth = self.get_authorization(req, chal)
        if auth:
            auth_val = 'Digest %s' % auth
            if req.headers.get(self.auth_header, None) == auth_val:
                return
            req.add_unredirected_header(self.auth_header, auth_val)
            resp = self.parent.open(req, timeout=req.timeout)
            return resp
        else:
            return

    def get_cnonce(self, nonce):
        dig = hashlib.sha1('%s:%s:%s:%s' % (self.nonce_count,
         nonce,
         time.ctime(),
         randombytes(8))).hexdigest()
        return dig[:16]

    def get_authorization(self, req, chal):
        try:
            realm = chal['realm']
            nonce = chal['nonce']
            qop = chal.get('qop')
            algorithm = chal.get('algorithm', 'MD5')
            opaque = chal.get('opaque', None)
        except KeyError:
            return

        H, KD = self.get_algorithm_impls(algorithm)
        if H is None:
            return
        else:
            user, pw = self.passwd.find_user_password(realm, req.get_full_url())
            if user is None:
                return
            if req.has_data():
                entdig = self.get_entity_digest(req.get_data(), chal)
            else:
                entdig = None
            A1 = '%s:%s:%s' % (user, realm, pw)
            A2 = '%s:%s' % (req.get_method(), req.get_selector())
            if qop == 'auth':
                if nonce == self.last_nonce:
                    self.nonce_count += 1
                else:
                    self.nonce_count = 1
                    self.last_nonce = nonce
                ncvalue = '%08x' % self.nonce_count
                cnonce = self.get_cnonce(nonce)
                noncebit = '%s:%s:%s:%s:%s' % (nonce,
                 ncvalue,
                 cnonce,
                 qop,
                 H(A2))
                respdig = KD(H(A1), noncebit)
            elif qop is None:
                respdig = KD(H(A1), '%s:%s' % (nonce, H(A2)))
            else:
                raise URLError("qop '%s' is not supported." % qop)
            base = 'username="%s", realm="%s", nonce="%s", uri="%s", response="%s"' % (user,
             realm,
             nonce,
             req.get_selector(),
             respdig)
            if opaque:
                base += ', opaque="%s"' % opaque
            if entdig:
                base += ', digest="%s"' % entdig
            base += ', algorithm="%s"' % algorithm
            if qop:
                base += ', qop=auth, nc=%s, cnonce="%s"' % (ncvalue, cnonce)
            return base

    def get_algorithm_impls(self, algorithm):
        algorithm = algorithm.upper()
        if algorithm == 'MD5':
            H = lambda x: hashlib.md5(x).hexdigest()
        elif algorithm == 'SHA':
            H = lambda x: hashlib.sha1(x).hexdigest()
        else:
            raise ValueError('Unsupported digest authentication algorithm %r' % algorithm.lower())
        KD = lambda s, d: H('%s:%s' % (s, d))
        return (H, KD)

    def get_entity_digest(self, data, chal):
        return None


class HTTPDigestAuthHandler(BaseHandler, AbstractDigestAuthHandler):
    """An authentication protocol defined by RFC 2069
    
    Digest authentication improves on basic authentication because it
    does not transmit passwords in the clear.
    """
    auth_header = 'Authorization'
    handler_order = 490

    def http_error_401(self, req, fp, code, msg, headers):
        host = urlparse.urlparse(req.get_full_url())[1]
        retry = self.http_error_auth_reqed('www-authenticate', host, req, headers)
        self.reset_retry_count()
        return retry


class ProxyDigestAuthHandler(BaseHandler, AbstractDigestAuthHandler):
    auth_header = 'Proxy-Authorization'
    handler_order = 490

    def http_error_407(self, req, fp, code, msg, headers):
        host = req.get_host()
        retry = self.http_error_auth_reqed('proxy-authenticate', host, req, headers)
        self.reset_retry_count()
        return retry


class AbstractHTTPHandler(BaseHandler):

    def __init__(self, debuglevel=0):
        self._debuglevel = debuglevel

    def set_http_debuglevel(self, level):
        self._debuglevel = level

    def do_request_(self, request):
        host = request.get_host()
        if not host:
            raise URLError('no host given')
        if request.has_data():
            data = request.get_data()
            if not request.has_header('Content-type'):
                request.add_unredirected_header('Content-type', 'application/x-www-form-urlencoded')
            if not request.has_header('Content-length'):
                request.add_unredirected_header('Content-length', '%d' % len(data))
        sel_host = host
        if request.has_proxy():
            scheme, sel = splittype(request.get_selector())
            sel_host, sel_path = splithost(sel)
        if not request.has_header('Host'):
            request.add_unredirected_header('Host', sel_host)
        for name, value in self.parent.addheaders:
            name = name.capitalize()
            if not request.has_header(name):
                request.add_unredirected_header(name, value)

        return request

    def do_open(self, http_class, req, **http_conn_args):
        """Return an addinfourl object for the request, using http_class.
        
        http_class must implement the HTTPConnection API from httplib.
        The addinfourl return value is a file-like object.  It also
        has methods and attributes including:
            - info(): return a mimetools.Message object for the headers
            - geturl(): return the original request URL
            - code: HTTP status code
        """
        host = req.get_host()
        if not host:
            raise URLError('no host given')
        h = http_class(host, timeout=req.timeout, **http_conn_args)
        h.set_debuglevel(self._debuglevel)
        headers = dict(req.unredirected_hdrs)
        headers.update(dict(((k, v) for k, v in req.headers.items() if k not in headers)))
        headers['Connection'] = 'close'
        headers = dict(((name.title(), val) for name, val in headers.items()))
        if req._tunnel_host:
            tunnel_headers = {}
            proxy_auth_hdr = 'Proxy-Authorization'
            if proxy_auth_hdr in headers:
                tunnel_headers[proxy_auth_hdr] = headers[proxy_auth_hdr]
                del headers[proxy_auth_hdr]
            h.set_tunnel(req._tunnel_host, headers=tunnel_headers)
        try:
            h.request(req.get_method(), req.get_selector(), req.data, headers)
        except socket.error as err:
            h.close()
            raise URLError(err)
        else:
            try:
                r = h.getresponse(buffering=True)
            except TypeError:
                r = h.getresponse()

        r.recv = r.read
        fp = socket._fileobject(r, close=True)
        resp = addinfourl(fp, r.msg, req.get_full_url())
        resp.code = r.status
        resp.msg = r.reason
        return resp


class HTTPHandler(AbstractHTTPHandler):

    def http_open(self, req):
        return self.do_open(httplib.HTTPConnection, req)

    http_request = AbstractHTTPHandler.do_request_


if hasattr(httplib, 'HTTPS'):

    class HTTPSHandler(AbstractHTTPHandler):

        def __init__(self, debuglevel=0, context=None):
            AbstractHTTPHandler.__init__(self, debuglevel)
            self._context = context

        def https_open(self, req):
            return self.do_open(httplib.HTTPSConnection, req, context=self._context)

        https_request = AbstractHTTPHandler.do_request_


class HTTPCookieProcessor(BaseHandler):

    def __init__(self, cookiejar=None):
        import cookielib
        if cookiejar is None:
            cookiejar = cookielib.CookieJar()
        self.cookiejar = cookiejar
        return

    def http_request(self, request):
        self.cookiejar.add_cookie_header(request)
        return request

    def http_response(self, request, response):
        self.cookiejar.extract_cookies(response, request)
        return response

    https_request = http_request
    https_response = http_response


class UnknownHandler(BaseHandler):

    def unknown_open(self, req):
        type = req.get_type()
        raise URLError('unknown url type: %s' % type)


def parse_keqv_list(l):
    """Parse list of key=value strings where keys are not duplicated."""
    parsed = {}
    for elt in l:
        k, v = elt.split('=', 1)
        if v[0] == '"' and v[-1] == '"':
            v = v[1:-1]
        parsed[k] = v

    return parsed


def parse_http_list(s):
    """Parse lists as described by RFC 2068 Section 2.
    
    In particular, parse comma-separated lists where the elements of
    the list may include quoted-strings.  A quoted-string could
    contain a comma.  A non-quoted string could have quotes in the
    middle.  Neither commas nor quotes count if they are escaped.
    Only double-quotes count, not single-quotes.
    """
    res = []
    part = ''
    escape = quote = False
    for cur in s:
        if escape:
            part += cur
            escape = False
            continue
        if quote:
            if cur == '\\':
                escape = True
                continue
            elif cur == '"':
                quote = False
            part += cur
            continue
        if cur == ',':
            res.append(part)
            part = ''
            continue
        if cur == '"':
            quote = True
        part += cur

    if part:
        res.append(part)
    return [ part.strip() for part in res ]


def _safe_gethostbyname(host):
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return None

    return None


class FileHandler(BaseHandler):

    def file_open(self, req):
        url = req.get_selector()
        if url[:2] == '//' and url[2:3] != '/' and req.host and req.host != 'localhost':
            req.type = 'ftp'
            return self.parent.open(req)
        else:
            return self.open_local_file(req)

    names = None

    def get_names(self):
        if FileHandler.names is None:
            try:
                FileHandler.names = tuple(socket.gethostbyname_ex('localhost')[2] + socket.gethostbyname_ex(socket.gethostname())[2])
            except socket.gaierror:
                FileHandler.names = (socket.gethostbyname('localhost'),)

        return FileHandler.names

    def open_local_file(self, req):
        import email.utils
        import mimetypes
        host = req.get_host()
        filename = req.get_selector()
        localfile = url2pathname(filename)
        try:
            stats = os.stat(localfile)
            size = stats.st_size
            modified = email.utils.formatdate(stats.st_mtime, usegmt=True)
            mtype = mimetypes.guess_type(filename)[0]
            headers = mimetools.Message(StringIO('Content-type: %s\nContent-length: %d\nLast-modified: %s\n' % (mtype or 'text/plain', size, modified)))
            if host:
                host, port = splitport(host)
            if not host or not port and _safe_gethostbyname(host) in self.get_names():
                if host:
                    origurl = 'file://' + host + filename
                else:
                    origurl = 'file://' + filename
                return addinfourl(open(localfile, 'rb'), headers, origurl)
        except OSError as msg:
            raise URLError(msg)

        raise URLError('file not on local host')


class FTPHandler(BaseHandler):

    def ftp_open(self, req):
        import ftplib
        import mimetypes
        host = req.get_host()
        if not host:
            raise URLError('ftp error: no host given')
        host, port = splitport(host)
        if port is None:
            port = ftplib.FTP_PORT
        else:
            port = int(port)
        user, host = splituser(host)
        if user:
            user, passwd = splitpasswd(user)
        else:
            passwd = None
        host = unquote(host)
        user = user or ''
        passwd = passwd or ''
        try:
            host = socket.gethostbyname(host)
        except socket.error as msg:
            raise URLError(msg)

        path, attrs = splitattr(req.get_selector())
        dirs = path.split('/')
        dirs = map(unquote, dirs)
        dirs, file = dirs[:-1], dirs[-1]
        if dirs and not dirs[0]:
            dirs = dirs[1:]
        try:
            fw = self.connect_ftp(user, passwd, host, port, dirs, req.timeout)
            type = file and 'I' or 'D'
            for attr in attrs:
                attr, value = splitvalue(attr)
                if attr.lower() == 'type' and value in ('a', 'A', 'i', 'I', 'd', 'D'):
                    type = value.upper()

            fp, retrlen = fw.retrfile(file, type)
            headers = ''
            mtype = mimetypes.guess_type(req.get_full_url())[0]
            if mtype:
                headers += 'Content-type: %s\n' % mtype
            if retrlen is not None and retrlen >= 0:
                headers += 'Content-length: %d\n' % retrlen
            sf = StringIO(headers)
            headers = mimetools.Message(sf)
            return addinfourl(fp, headers, req.get_full_url())
        except ftplib.all_errors as msg:
            raise URLError, 'ftp error: %s' % msg, sys.exc_info()[2]

        return

    def connect_ftp(self, user, passwd, host, port, dirs, timeout):
        fw = ftpwrapper(user, passwd, host, port, dirs, timeout, persistent=False)
        return fw


class CacheFTPHandler(FTPHandler):

    def __init__(self):
        self.cache = {}
        self.timeout = {}
        self.soonest = 0
        self.delay = 60
        self.max_conns = 16

    def setTimeout(self, t):
        self.delay = t

    def setMaxConns(self, m):
        self.max_conns = m

    def connect_ftp(self, user, passwd, host, port, dirs, timeout):
        key = (user,
         host,
         port,
         '/'.join(dirs),
         timeout)
        if key in self.cache:
            self.timeout[key] = time.time() + self.delay
        else:
            self.cache[key] = ftpwrapper(user, passwd, host, port, dirs, timeout)
            self.timeout[key] = time.time() + self.delay
        self.check_cache()
        return self.cache[key]

    def check_cache(self):
        t = time.time()
        if self.soonest <= t:
            for k, v in self.timeout.items():
                if v < t:
                    self.cache[k].close()
                    del self.cache[k]
                    del self.timeout[k]

        self.soonest = min(self.timeout.values())
        if len(self.cache) == self.max_conns:
            for k, v in self.timeout.items():
                if v == self.soonest:
                    del self.cache[k]
                    del self.timeout[k]
                    break

            self.soonest = min(self.timeout.values())

    def clear_cache(self):
        for conn in self.cache.values():
            conn.close()

        self.cache.clear()
        self.timeout.clear()
