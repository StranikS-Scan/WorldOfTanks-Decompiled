# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/urllib.py
import string
import socket
import os
import time
import sys
import base64
import re
from urlparse import urljoin as basejoin
__all__ = ['urlopen',
 'URLopener',
 'FancyURLopener',
 'urlretrieve',
 'urlcleanup',
 'quote',
 'quote_plus',
 'unquote',
 'unquote_plus',
 'urlencode',
 'url2pathname',
 'pathname2url',
 'splittag',
 'localhost',
 'thishost',
 'ftperrors',
 'basejoin',
 'unwrap',
 'splittype',
 'splithost',
 'splituser',
 'splitpasswd',
 'splitport',
 'splitnport',
 'splitquery',
 'splitattr',
 'splitvalue',
 'getproxies']
__version__ = '1.17'
MAXFTPCACHE = 10
if os.name == 'nt':
    from nturl2path import url2pathname, pathname2url
elif os.name == 'riscos':
    from rourl2path import url2pathname, pathname2url
else:

    def url2pathname(pathname):
        return unquote(pathname)


    def pathname2url(pathname):
        return quote(pathname)


_urlopener = None

def urlopen(url, data=None, proxies=None):
    global _urlopener
    from warnings import warnpy3k
    warnpy3k('urllib.urlopen() has been removed in Python 3.0 in favor of urllib2.urlopen()', stacklevel=2)
    if proxies is not None:
        opener = FancyURLopener(proxies=proxies)
    elif not _urlopener:
        opener = FancyURLopener()
        _urlopener = opener
    else:
        opener = _urlopener
    if data is None:
        return opener.open(url)
    else:
        return opener.open(url, data)
        return


def urlretrieve(url, filename=None, reporthook=None, data=None):
    global _urlopener
    if not _urlopener:
        _urlopener = FancyURLopener()
    return _urlopener.retrieve(url, filename, reporthook, data)


def urlcleanup():
    if _urlopener:
        _urlopener.cleanup()
    _safe_quoters.clear()
    ftpcache.clear()


try:
    import ssl
except:
    _have_ssl = False
else:
    _have_ssl = True

class ContentTooShortError(IOError):

    def __init__(self, message, content):
        IOError.__init__(self, message)
        self.content = content


ftpcache = {}

class URLopener():
    __tempfiles = None
    version = 'Python-urllib/%s' % __version__

    def __init__(self, proxies=None, **x509):
        if proxies is None:
            proxies = getproxies()
        self.proxies = proxies
        self.key_file = x509.get('key_file')
        self.cert_file = x509.get('cert_file')
        self.addheaders = [('User-Agent', self.version)]
        self.__tempfiles = []
        self.__unlink = os.unlink
        self.tempcache = None
        self.ftpcache = ftpcache
        return

    def __del__(self):
        self.close()

    def close(self):
        self.cleanup()

    def cleanup(self):
        if self.__tempfiles:
            for file in self.__tempfiles:
                try:
                    self.__unlink(file)
                except OSError:
                    pass

            del self.__tempfiles[:]
        if self.tempcache:
            self.tempcache.clear()

    def addheader(self, *args):
        self.addheaders.append(args)

    def open(self, fullurl, data=None):
        fullurl = unwrap(toBytes(fullurl))
        fullurl = quote(fullurl, safe="%/:=&?~#+!$,;'@()*[]|")
        if self.tempcache and fullurl in self.tempcache:
            filename, headers = self.tempcache[fullurl]
            fp = open(filename, 'rb')
            return addinfourl(fp, headers, fullurl)
        else:
            urltype, url = splittype(fullurl)
            if not urltype:
                urltype = 'file'
            if urltype in self.proxies:
                proxy = self.proxies[urltype]
                urltype, proxyhost = splittype(proxy)
                host, selector = splithost(proxyhost)
                url = (host, fullurl)
            else:
                proxy = None
            name = 'open_' + urltype
            self.type = urltype
            name = name.replace('-', '_')
            if not hasattr(self, name):
                if proxy:
                    return self.open_unknown_proxy(proxy, fullurl, data)
                else:
                    return self.open_unknown(fullurl, data)
            try:
                if data is None:
                    return getattr(self, name)(url)
                return getattr(self, name)(url, data)
            except socket.error as msg:
                raise IOError, ('socket error', msg), sys.exc_info()[2]

            return

    def open_unknown(self, fullurl, data=None):
        type, url = splittype(fullurl)
        raise IOError, ('url error', 'unknown url type', type)

    def open_unknown_proxy(self, proxy, fullurl, data=None):
        type, url = splittype(fullurl)
        raise IOError, ('url error', 'invalid proxy for %s' % type, proxy)

    def retrieve(self, url, filename=None, reporthook=None, data=None):
        url = unwrap(toBytes(url))
        if self.tempcache and url in self.tempcache:
            return self.tempcache[url]
        else:
            type, url1 = splittype(url)
            if filename is None and (not type or type == 'file'):
                try:
                    fp = self.open_local_file(url1)
                    hdrs = fp.info()
                    fp.close()
                    return (url2pathname(splithost(url1)[1]), hdrs)
                except IOError:
                    pass

            fp = self.open(url, data)
            try:
                headers = fp.info()
                if filename:
                    tfp = open(filename, 'wb')
                else:
                    import tempfile
                    garbage, path = splittype(url)
                    garbage, path = splithost(path or '')
                    path, garbage = splitquery(path or '')
                    path, garbage = splitattr(path or '')
                    suffix = os.path.splitext(path)[1]
                    fd, filename = tempfile.mkstemp(suffix)
                    self.__tempfiles.append(filename)
                    tfp = os.fdopen(fd, 'wb')
                try:
                    result = (filename, headers)
                    if self.tempcache is not None:
                        self.tempcache[url] = result
                    bs = 8192
                    size = -1
                    read = 0
                    blocknum = 0
                    if 'content-length' in headers:
                        size = int(headers['Content-Length'])
                    if reporthook:
                        reporthook(blocknum, bs, size)
                    while 1:
                        block = fp.read(bs)
                        if block == '':
                            break
                        read += len(block)
                        tfp.write(block)
                        blocknum += 1
                        if reporthook:
                            reporthook(blocknum, bs, size)

                finally:
                    tfp.close()

            finally:
                fp.close()

            if size >= 0 and read < size:
                raise ContentTooShortError('retrieval incomplete: got only %i out of %i bytes' % (read, size), result)
            return result

    def open_http(self, url, data=None):
        import httplib
        user_passwd = None
        proxy_passwd = None
        if isinstance(url, str):
            host, selector = splithost(url)
            if host:
                user_passwd, host = splituser(host)
                host = unquote(host)
            realhost = host
        else:
            host, selector = url
            proxy_passwd, host = splituser(host)
            urltype, rest = splittype(selector)
            url = rest
            user_passwd = None
            if urltype.lower() != 'http':
                realhost = None
            else:
                realhost, rest = splithost(rest)
                if realhost:
                    user_passwd, realhost = splituser(realhost)
                if user_passwd:
                    selector = '%s://%s%s' % (urltype, realhost, rest)
                if proxy_bypass(realhost):
                    host = realhost
        if not host:
            raise IOError, ('http error', 'no host given')
        if proxy_passwd:
            proxy_passwd = unquote(proxy_passwd)
            proxy_auth = base64.b64encode(proxy_passwd).strip()
        else:
            proxy_auth = None
        if user_passwd:
            user_passwd = unquote(user_passwd)
            auth = base64.b64encode(user_passwd).strip()
        else:
            auth = None
        h = httplib.HTTP(host)
        if data is not None:
            h.putrequest('POST', selector)
            h.putheader('Content-Type', 'application/x-www-form-urlencoded')
            h.putheader('Content-Length', '%d' % len(data))
        else:
            h.putrequest('GET', selector)
        if proxy_auth:
            h.putheader('Proxy-Authorization', 'Basic %s' % proxy_auth)
        if auth:
            h.putheader('Authorization', 'Basic %s' % auth)
        if realhost:
            h.putheader('Host', realhost)
        for args in self.addheaders:
            h.putheader(*args)

        h.endheaders(data)
        errcode, errmsg, headers = h.getreply()
        fp = h.getfile()
        if errcode == -1:
            if fp:
                fp.close()
            raise IOError, ('http protocol error', 0, 'got a bad status line', None)
        if 200 <= errcode < 300:
            return addinfourl(fp, headers, 'http:' + url, errcode)
        elif data is None:
            return self.http_error(url, fp, errcode, errmsg, headers)
        else:
            return self.http_error(url, fp, errcode, errmsg, headers, data)
            return

    def http_error(self, url, fp, errcode, errmsg, headers, data=None):
        name = 'http_error_%d' % errcode
        if hasattr(self, name):
            method = getattr(self, name)
            if data is None:
                result = method(url, fp, errcode, errmsg, headers)
            else:
                result = method(url, fp, errcode, errmsg, headers, data)
            if result:
                return result
        return self.http_error_default(url, fp, errcode, errmsg, headers)

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        fp.close()
        raise IOError, ('http error',
         errcode,
         errmsg,
         headers)

    if _have_ssl:

        def open_https(self, url, data=None):
            import httplib
            user_passwd = None
            proxy_passwd = None
            if isinstance(url, str):
                host, selector = splithost(url)
                if host:
                    user_passwd, host = splituser(host)
                    host = unquote(host)
                realhost = host
            else:
                host, selector = url
                proxy_passwd, host = splituser(host)
                urltype, rest = splittype(selector)
                url = rest
                user_passwd = None
                if urltype.lower() != 'https':
                    realhost = None
                else:
                    realhost, rest = splithost(rest)
                    if realhost:
                        user_passwd, realhost = splituser(realhost)
                    if user_passwd:
                        selector = '%s://%s%s' % (urltype, realhost, rest)
            if not host:
                raise IOError, ('https error', 'no host given')
            if proxy_passwd:
                proxy_passwd = unquote(proxy_passwd)
                proxy_auth = base64.b64encode(proxy_passwd).strip()
            else:
                proxy_auth = None
            if user_passwd:
                user_passwd = unquote(user_passwd)
                auth = base64.b64encode(user_passwd).strip()
            else:
                auth = None
            h = httplib.HTTPS(host, 0, key_file=self.key_file, cert_file=self.cert_file)
            if data is not None:
                h.putrequest('POST', selector)
                h.putheader('Content-Type', 'application/x-www-form-urlencoded')
                h.putheader('Content-Length', '%d' % len(data))
            else:
                h.putrequest('GET', selector)
            if proxy_auth:
                h.putheader('Proxy-Authorization', 'Basic %s' % proxy_auth)
            if auth:
                h.putheader('Authorization', 'Basic %s' % auth)
            if realhost:
                h.putheader('Host', realhost)
            for args in self.addheaders:
                h.putheader(*args)

            h.endheaders(data)
            errcode, errmsg, headers = h.getreply()
            fp = h.getfile()
            if errcode == -1:
                if fp:
                    fp.close()
                raise IOError, ('http protocol error', 0, 'got a bad status line', None)
            if 200 <= errcode < 300:
                return addinfourl(fp, headers, 'https:' + url, errcode)
            elif data is None:
                return self.http_error(url, fp, errcode, errmsg, headers)
            else:
                return self.http_error(url, fp, errcode, errmsg, headers, data)
                return

    def open_file(self, url):
        if not isinstance(url, str):
            raise IOError, ('file error', 'proxy support for file protocol currently not implemented')
        if url[:2] == '//' and url[2:3] != '/' and url[2:12].lower() != 'localhost/':
            return self.open_ftp(url)
        else:
            return self.open_local_file(url)

    def open_local_file(self, url):
        import mimetypes, mimetools, email.utils
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO

        host, file = splithost(url)
        localname = url2pathname(file)
        try:
            stats = os.stat(localname)
        except OSError as e:
            raise IOError(e.errno, e.strerror, e.filename)

        size = stats.st_size
        modified = email.utils.formatdate(stats.st_mtime, usegmt=True)
        mtype = mimetypes.guess_type(url)[0]
        headers = mimetools.Message(StringIO('Content-Type: %s\nContent-Length: %d\nLast-modified: %s\n' % (mtype or 'text/plain', size, modified)))
        if not host:
            urlfile = file
            if file[:1] == '/':
                urlfile = 'file://' + file
            elif file[:2] == './':
                raise ValueError('local file url may start with / or file:. Unknown url of type: %s' % url)
            return addinfourl(open(localname, 'rb'), headers, urlfile)
        host, port = splitport(host)
        if not port and socket.gethostbyname(host) in (localhost(), thishost()):
            urlfile = file
            if file[:1] == '/':
                urlfile = 'file://' + file
            return addinfourl(open(localname, 'rb'), headers, urlfile)
        raise IOError, ('local file error', 'not on local host')

    def open_ftp(self, url):
        if not isinstance(url, str):
            raise IOError, ('ftp error', 'proxy support for ftp protocol currently not implemented')
        import mimetypes, mimetools
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO

        host, path = splithost(url)
        if not host:
            raise IOError, ('ftp error', 'no host given')
        host, port = splitport(host)
        user, host = splituser(host)
        if user:
            user, passwd = splitpasswd(user)
        else:
            passwd = None
        host = unquote(host)
        user = user or ''
        passwd = passwd or ''
        host = socket.gethostbyname(host)
        if not port:
            import ftplib
            port = ftplib.FTP_PORT
        else:
            port = int(port)
        path, attrs = splitattr(path)
        path = unquote(path)
        dirs = path.split('/')
        dirs, file = dirs[:-1], dirs[-1]
        if dirs and not dirs[0]:
            dirs = dirs[1:]
        if dirs and not dirs[0]:
            dirs[0] = '/'
        key = (user,
         host,
         port,
         '/'.join(dirs))
        if len(self.ftpcache) > MAXFTPCACHE:
            for k in self.ftpcache.keys():
                if k != key:
                    v = self.ftpcache[k]
                    del self.ftpcache[k]
                    v.close()

        try:
            if key not in self.ftpcache:
                self.ftpcache[key] = ftpwrapper(user, passwd, host, port, dirs)
            if not file:
                type = 'D'
            else:
                type = 'I'
            for attr in attrs:
                attr, value = splitvalue(attr)
                if attr.lower() == 'type' and value in ('a', 'A', 'i', 'I', 'd', 'D'):
                    type = value.upper()

            fp, retrlen = self.ftpcache[key].retrfile(file, type)
            mtype = mimetypes.guess_type('ftp:' + url)[0]
            headers = ''
            if mtype:
                headers += 'Content-Type: %s\n' % mtype
            if retrlen is not None and retrlen >= 0:
                headers += 'Content-Length: %d\n' % retrlen
            headers = mimetools.Message(StringIO(headers))
            return addinfourl(fp, headers, 'ftp:' + url)
        except ftperrors() as msg:
            raise IOError, ('ftp error', msg), sys.exc_info()[2]

        return

    def open_data(self, url, data=None):
        if not isinstance(url, str):
            raise IOError, ('data error', 'proxy support for data protocol currently not implemented')
        import mimetools
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO

        try:
            type, data = url.split(',', 1)
        except ValueError:
            raise IOError, ('data error', 'bad data URL')

        if not type:
            type = 'text/plain;charset=US-ASCII'
        semi = type.rfind(';')
        if semi >= 0 and '=' not in type[semi:]:
            encoding = type[semi + 1:]
            type = type[:semi]
        else:
            encoding = ''
        msg = []
        msg.append('Date: %s' % time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(time.time())))
        msg.append('Content-type: %s' % type)
        if encoding == 'base64':
            data = base64.decodestring(data)
        else:
            data = unquote(data)
        msg.append('Content-Length: %d' % len(data))
        msg.append('')
        msg.append(data)
        msg = '\n'.join(msg)
        f = StringIO(msg)
        headers = mimetools.Message(f, 0)
        return addinfourl(f, headers, url)


class FancyURLopener(URLopener):

    def __init__(self, *args, **kwargs):
        URLopener.__init__(self, *args, **kwargs)
        self.auth_cache = {}
        self.tries = 0
        self.maxtries = 10

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        return addinfourl(fp, headers, 'http:' + url, errcode)

    def http_error_302(self, url, fp, errcode, errmsg, headers, data=None):
        self.tries += 1
        if self.maxtries and self.tries >= self.maxtries:
            if hasattr(self, 'http_error_500'):
                meth = self.http_error_500
            else:
                meth = self.http_error_default
            self.tries = 0
            return meth(url, fp, 500, 'Internal Server Error: Redirect Recursion', headers)
        result = self.redirect_internal(url, fp, errcode, errmsg, headers, data)
        self.tries = 0
        return result

    def redirect_internal(self, url, fp, errcode, errmsg, headers, data):
        if 'location' in headers:
            newurl = headers['location']
        elif 'uri' in headers:
            newurl = headers['uri']
        else:
            return
        fp.close()
        newurl = basejoin(self.type + ':' + url, newurl)
        newurl_lower = newurl.lower()
        if not (newurl_lower.startswith('http://') or newurl_lower.startswith('https://') or newurl_lower.startswith('ftp://')):
            raise IOError('redirect error', errcode, errmsg + " - Redirection to url '%s' is not allowed" % newurl, headers)
        return self.open(newurl)

    def http_error_301(self, url, fp, errcode, errmsg, headers, data=None):
        return self.http_error_302(url, fp, errcode, errmsg, headers, data)

    def http_error_303(self, url, fp, errcode, errmsg, headers, data=None):
        return self.http_error_302(url, fp, errcode, errmsg, headers, data)

    def http_error_307(self, url, fp, errcode, errmsg, headers, data=None):
        if data is None:
            return self.http_error_302(url, fp, errcode, errmsg, headers, data)
        else:
            return self.http_error_default(url, fp, errcode, errmsg, headers)
            return

    def http_error_401(self, url, fp, errcode, errmsg, headers, data=None):
        if 'www-authenticate' not in headers:
            URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
        stuff = headers['www-authenticate']
        import re
        match = re.match('[ \t]*([^ \t]+)[ \t]+realm="([^"]*)"', stuff)
        if not match:
            URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
        scheme, realm = match.groups()
        if scheme.lower() != 'basic':
            URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
        name = 'retry_' + self.type + '_basic_auth'
        if data is None:
            return getattr(self, name)(url, realm)
        else:
            return getattr(self, name)(url, realm, data)
            return

    def http_error_407(self, url, fp, errcode, errmsg, headers, data=None):
        if 'proxy-authenticate' not in headers:
            URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
        stuff = headers['proxy-authenticate']
        import re
        match = re.match('[ \t]*([^ \t]+)[ \t]+realm="([^"]*)"', stuff)
        if not match:
            URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
        scheme, realm = match.groups()
        if scheme.lower() != 'basic':
            URLopener.http_error_default(self, url, fp, errcode, errmsg, headers)
        name = 'retry_proxy_' + self.type + '_basic_auth'
        if data is None:
            return getattr(self, name)(url, realm)
        else:
            return getattr(self, name)(url, realm, data)
            return

    def retry_proxy_http_basic_auth(self, url, realm, data=None):
        host, selector = splithost(url)
        newurl = 'http://' + host + selector
        proxy = self.proxies['http']
        urltype, proxyhost = splittype(proxy)
        proxyhost, proxyselector = splithost(proxyhost)
        i = proxyhost.find('@') + 1
        proxyhost = proxyhost[i:]
        user, passwd = self.get_user_passwd(proxyhost, realm, i)
        if not (user or passwd):
            return
        else:
            proxyhost = quote(user, safe='') + ':' + quote(passwd, safe='') + '@' + proxyhost
            self.proxies['http'] = 'http://' + proxyhost + proxyselector
            if data is None:
                return self.open(newurl)
            return self.open(newurl, data)
            return

    def retry_proxy_https_basic_auth(self, url, realm, data=None):
        host, selector = splithost(url)
        newurl = 'https://' + host + selector
        proxy = self.proxies['https']
        urltype, proxyhost = splittype(proxy)
        proxyhost, proxyselector = splithost(proxyhost)
        i = proxyhost.find('@') + 1
        proxyhost = proxyhost[i:]
        user, passwd = self.get_user_passwd(proxyhost, realm, i)
        if not (user or passwd):
            return
        else:
            proxyhost = quote(user, safe='') + ':' + quote(passwd, safe='') + '@' + proxyhost
            self.proxies['https'] = 'https://' + proxyhost + proxyselector
            if data is None:
                return self.open(newurl)
            return self.open(newurl, data)
            return

    def retry_http_basic_auth(self, url, realm, data=None):
        host, selector = splithost(url)
        i = host.find('@') + 1
        host = host[i:]
        user, passwd = self.get_user_passwd(host, realm, i)
        if not (user or passwd):
            return
        else:
            host = quote(user, safe='') + ':' + quote(passwd, safe='') + '@' + host
            newurl = 'http://' + host + selector
            if data is None:
                return self.open(newurl)
            return self.open(newurl, data)
            return

    def retry_https_basic_auth(self, url, realm, data=None):
        host, selector = splithost(url)
        i = host.find('@') + 1
        host = host[i:]
        user, passwd = self.get_user_passwd(host, realm, i)
        if not (user or passwd):
            return
        else:
            host = quote(user, safe='') + ':' + quote(passwd, safe='') + '@' + host
            newurl = 'https://' + host + selector
            if data is None:
                return self.open(newurl)
            return self.open(newurl, data)
            return

    def get_user_passwd(self, host, realm, clear_cache=0):
        key = realm + '@' + host.lower()
        if key in self.auth_cache:
            if clear_cache:
                del self.auth_cache[key]
            else:
                return self.auth_cache[key]
        user, passwd = self.prompt_user_passwd(host, realm)
        if user or passwd:
            self.auth_cache[key] = (user, passwd)
        return (user, passwd)

    def prompt_user_passwd(self, host, realm):
        import getpass
        try:
            user = raw_input('Enter username for %s at %s: ' % (realm, host))
            passwd = getpass.getpass('Enter password for %s in %s at %s: ' % (user, realm, host))
            return (user, passwd)
        except KeyboardInterrupt:
            print
            return (None, None)

        return


_localhost = None

def localhost():
    global _localhost
    if _localhost is None:
        _localhost = socket.gethostbyname('localhost')
    return _localhost


_thishost = None

def thishost():
    global _thishost
    if _thishost is None:
        try:
            _thishost = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            _thishost = socket.gethostbyname('localhost')

    return _thishost


_ftperrors = None

def ftperrors():
    global _ftperrors
    if _ftperrors is None:
        import ftplib
        _ftperrors = ftplib.all_errors
    return _ftperrors


_noheaders = None

def noheaders():
    global _noheaders
    if _noheaders is None:
        import mimetools
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO

        _noheaders = mimetools.Message(StringIO(), 0)
        _noheaders.fp.close()
    return _noheaders


class ftpwrapper():

    def __init__(self, user, passwd, host, port, dirs, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, persistent=True):
        self.user = user
        self.passwd = passwd
        self.host = host
        self.port = port
        self.dirs = dirs
        self.timeout = timeout
        self.refcount = 0
        self.keepalive = persistent
        self.init()

    def init(self):
        import ftplib
        self.busy = 0
        self.ftp = ftplib.FTP()
        self.ftp.connect(self.host, self.port, self.timeout)
        self.ftp.login(self.user, self.passwd)
        _target = '/'.join(self.dirs)
        self.ftp.cwd(_target)

    def retrfile(self, file, type):
        import ftplib
        self.endtransfer()
        if type in ('d', 'D'):
            cmd = 'TYPE A'
            isdir = 1
        else:
            cmd = 'TYPE ' + type
            isdir = 0
        try:
            self.ftp.voidcmd(cmd)
        except ftplib.all_errors:
            self.init()
            self.ftp.voidcmd(cmd)

        conn = None
        if file and not isdir:
            try:
                cmd = 'RETR ' + file
                conn, retrlen = self.ftp.ntransfercmd(cmd)
            except ftplib.error_perm as reason:
                if str(reason)[:3] != '550':
                    raise IOError, ('ftp error', reason), sys.exc_info()[2]

        if not conn:
            self.ftp.voidcmd('TYPE A')
            if file:
                pwd = self.ftp.pwd()
                try:
                    try:
                        self.ftp.cwd(file)
                    except ftplib.error_perm as reason:
                        raise IOError, ('ftp error', reason), sys.exc_info()[2]

                finally:
                    self.ftp.cwd(pwd)

                cmd = 'LIST ' + file
            else:
                cmd = 'LIST'
            conn, retrlen = self.ftp.ntransfercmd(cmd)
        self.busy = 1
        ftpobj = addclosehook(conn.makefile('rb'), self.file_close)
        self.refcount += 1
        conn.close()
        return (ftpobj, retrlen)

    def endtransfer(self):
        if not self.busy:
            return
        self.busy = 0
        try:
            self.ftp.voidresp()
        except ftperrors():
            pass

    def close(self):
        self.keepalive = False
        if self.refcount <= 0:
            self.real_close()

    def file_close(self):
        self.endtransfer()
        self.refcount -= 1
        if self.refcount <= 0 and not self.keepalive:
            self.real_close()

    def real_close(self):
        self.endtransfer()
        try:
            self.ftp.close()
        except ftperrors():
            pass


class addbase():

    def __init__(self, fp):
        self.fp = fp
        self.read = self.fp.read
        self.readline = self.fp.readline
        if hasattr(self.fp, 'readlines'):
            self.readlines = self.fp.readlines
        if hasattr(self.fp, 'fileno'):
            self.fileno = self.fp.fileno
        else:
            self.fileno = lambda : None
        if hasattr(self.fp, '__iter__'):
            self.__iter__ = self.fp.__iter__
            if hasattr(self.fp, 'next'):
                self.next = self.fp.next

    def __repr__(self):
        return '<%s at %r whose fp = %r>' % (self.__class__.__name__, id(self), self.fp)

    def close(self):
        self.read = None
        self.readline = None
        self.readlines = None
        self.fileno = None
        if self.fp:
            self.fp.close()
        self.fp = None
        return


class addclosehook(addbase):

    def __init__(self, fp, closehook, *hookargs):
        addbase.__init__(self, fp)
        self.closehook = closehook
        self.hookargs = hookargs

    def close(self):
        if self.closehook:
            self.closehook(*self.hookargs)
            self.closehook = None
            self.hookargs = None
        addbase.close(self)
        return


class addinfo(addbase):

    def __init__(self, fp, headers):
        addbase.__init__(self, fp)
        self.headers = headers

    def info(self):
        return self.headers


class addinfourl(addbase):

    def __init__(self, fp, headers, url, code=None):
        addbase.__init__(self, fp)
        self.headers = headers
        self.url = url
        self.code = code

    def info(self):
        return self.headers

    def getcode(self):
        return self.code

    def geturl(self):
        return self.url


try:
    unicode
except NameError:

    def _is_unicode(x):
        pass


else:

    def _is_unicode(x):
        return isinstance(x, unicode)


def toBytes(url):
    if _is_unicode(url):
        try:
            url = url.encode('ASCII')
        except UnicodeError:
            raise UnicodeError('URL ' + repr(url) + ' contains non-ASCII characters')

    return url


def unwrap(url):
    url = url.strip()
    if url[:1] == '<' and url[-1:] == '>':
        url = url[1:-1].strip()
    if url[:4] == 'URL:':
        url = url[4:].strip()
    return url


_typeprog = None

def splittype(url):
    global _typeprog
    if _typeprog is None:
        import re
        _typeprog = re.compile('^([^/:]+):')
    match = _typeprog.match(url)
    if match:
        scheme = match.group(1)
        return (scheme.lower(), url[len(scheme) + 1:])
    else:
        return (None, url)


_hostprog = None

def splithost(url):
    global _hostprog
    if _hostprog is None:
        import re
        _hostprog = re.compile('^//([^/?]*)(.*)$')
    match = _hostprog.match(url)
    if match:
        host_port = match.group(1)
        path = match.group(2)
        if path and not path.startswith('/'):
            path = '/' + path
        return (host_port, path)
    else:
        return (None, url)


_userprog = None

def splituser(host):
    global _userprog
    if _userprog is None:
        import re
        _userprog = re.compile('^(.*)@(.*)$')
    match = _userprog.match(host)
    return match.group(1, 2) if match else (None, host)


_passwdprog = None

def splitpasswd(user):
    global _passwdprog
    if _passwdprog is None:
        import re
        _passwdprog = re.compile('^([^:]*):(.*)$', re.S)
    match = _passwdprog.match(user)
    return match.group(1, 2) if match else (user, None)


_portprog = None

def splitport(host):
    global _portprog
    if _portprog is None:
        import re
        _portprog = re.compile('^(.*):([0-9]*)$')
    match = _portprog.match(host)
    if match:
        host, port = match.groups()
        if port:
            return (host, port)
    return (host, None)


_nportprog = None

def splitnport(host, defport=-1):
    global _nportprog
    if _nportprog is None:
        import re
        _nportprog = re.compile('^(.*):(.*)$')
    match = _nportprog.match(host)
    if match:
        host, port = match.group(1, 2)
        if port:
            try:
                nport = int(port)
            except ValueError:
                nport = None

            return (host, nport)
    return (host, defport)


_queryprog = None

def splitquery(url):
    global _queryprog
    if _queryprog is None:
        import re
        _queryprog = re.compile('^(.*)\\?([^?]*)$')
    match = _queryprog.match(url)
    return match.group(1, 2) if match else (url, None)


_tagprog = None

def splittag(url):
    global _tagprog
    if _tagprog is None:
        import re
        _tagprog = re.compile('^(.*)#([^#]*)$')
    match = _tagprog.match(url)
    return match.group(1, 2) if match else (url, None)


def splitattr(url):
    words = url.split(';')
    return (words[0], words[1:])


_valueprog = None

def splitvalue(attr):
    global _valueprog
    if _valueprog is None:
        import re
        _valueprog = re.compile('^([^=]*)=(.*)$')
    match = _valueprog.match(attr)
    return match.group(1, 2) if match else (attr, None)


_hexdig = '0123456789ABCDEFabcdef'
_hextochr = dict(((a + b, chr(int(a + b, 16))) for a in _hexdig for b in _hexdig))
_asciire = re.compile('([\x00-\x7f]+)')

def unquote(s):
    if _is_unicode(s):
        if '%' not in s:
            return s
        bits = _asciire.split(s)
        res = [bits[0]]
        append = res.append
        for i in range(1, len(bits), 2):
            append(unquote(str(bits[i])).decode('latin1'))
            append(bits[i + 1])

        return ''.join(res)
    bits = s.split('%')
    if len(bits) == 1:
        return s
    res = [bits[0]]
    append = res.append
    for item in bits[1:]:
        try:
            append(_hextochr[item[:2]])
            append(item[2:])
        except KeyError:
            append('%')
            append(item)

    return ''.join(res)


def unquote_plus(s):
    s = s.replace('+', ' ')
    return unquote(s)


always_safe = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-'
_safe_map = {}
for i, c in zip(xrange(256), str(bytearray(xrange(256)))):
    _safe_map[c] = c if i < 128 and c in always_safe else '%{:02X}'.format(i)

_safe_quoters = {}

def quote(s, safe='/'):
    if not s:
        if s is None:
            raise TypeError('None object cannot be quoted')
        return s
    else:
        cachekey = (safe, always_safe)
        try:
            quoter, safe = _safe_quoters[cachekey]
        except KeyError:
            safe_map = _safe_map.copy()
            safe_map.update([ (c, c) for c in safe ])
            quoter = safe_map.__getitem__
            safe = always_safe + safe
            _safe_quoters[cachekey] = (quoter, safe)

        return s if not s.rstrip(safe) else ''.join(map(quoter, s))


def quote_plus(s, safe=''):
    if ' ' in s:
        s = quote(s, safe + ' ')
        return s.replace(' ', '+')
    return quote(s, safe)


def urlencode(query, doseq=0):
    if hasattr(query, 'items'):
        query = query.items()
    else:
        try:
            if len(query) and not isinstance(query[0], tuple):
                raise TypeError
        except TypeError:
            ty, va, tb = sys.exc_info()
            raise TypeError, 'not a valid non-string sequence or mapping object', tb

    l = []
    if not doseq:
        for k, v in query:
            k = quote_plus(str(k))
            v = quote_plus(str(v))
            l.append(k + '=' + v)

    else:
        for k, v in query:
            k = quote_plus(str(k))
            if isinstance(v, str):
                v = quote_plus(v)
                l.append(k + '=' + v)
            if _is_unicode(v):
                v = quote_plus(v.encode('ASCII', 'replace'))
                l.append(k + '=' + v)
            try:
                len(v)
            except TypeError:
                v = quote_plus(str(v))
                l.append(k + '=' + v)
            else:
                for elt in v:
                    l.append(k + '=' + quote_plus(str(elt)))

    return '&'.join(l)


def getproxies_environment():
    proxies = {}
    for name, value in os.environ.items():
        name = name.lower()
        if value and name[-6:] == '_proxy':
            proxies[name[:-6]] = value

    return proxies


def proxy_bypass_environment(host):
    no_proxy = os.environ.get('no_proxy', '') or os.environ.get('NO_PROXY', '')
    if no_proxy == '*':
        return 1
    hostonly, port = splitport(host)
    no_proxy_list = [ proxy.strip() for proxy in no_proxy.split(',') ]
    for name in no_proxy_list:
        if name and (hostonly.endswith(name) or host.endswith(name)):
            return 1


if sys.platform == 'darwin':
    from _scproxy import _get_proxy_settings, _get_proxies

    def proxy_bypass_macosx_sysconf(host):
        import re
        import socket
        from fnmatch import fnmatch
        hostonly, port = splitport(host)

        def ip2num(ipAddr):
            parts = ipAddr.split('.')
            parts = map(int, parts)
            if len(parts) != 4:
                parts = (parts + [0,
                 0,
                 0,
                 0])[:4]
            return parts[0] << 24 | parts[1] << 16 | parts[2] << 8 | parts[3]

        proxy_settings = _get_proxy_settings()
        if '.' not in host:
            if proxy_settings['exclude_simple']:
                return True
        hostIP = None
        for value in proxy_settings.get('exceptions', ()):
            if not value:
                continue
            m = re.match('(\\d+(?:\\.\\d+)*)(/\\d+)?', value)
            if m is not None:
                if hostIP is None:
                    try:
                        hostIP = socket.gethostbyname(hostonly)
                        hostIP = ip2num(hostIP)
                    except socket.error:
                        continue

                base = ip2num(m.group(1))
                mask = m.group(2)
                if mask is None:
                    mask = 8 * (m.group(1).count('.') + 1)
                else:
                    mask = int(mask[1:])
                mask = 32 - mask
                if hostIP >> mask == base >> mask:
                    return True
            if fnmatch(host, value):
                return True

        return False


    def getproxies_macosx_sysconf():
        return _get_proxies()


    def proxy_bypass(host):
        if getproxies_environment():
            return proxy_bypass_environment(host)
        else:
            return proxy_bypass_macosx_sysconf(host)


    def getproxies():
        return getproxies_environment() or getproxies_macosx_sysconf()


elif os.name == 'nt':

    def getproxies_registry():
        proxies = {}
        try:
            import _winreg
        except ImportError:
            return proxies

        try:
            internetSettings = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings')
            proxyEnable = _winreg.QueryValueEx(internetSettings, 'ProxyEnable')[0]
            if proxyEnable:
                proxyServer = str(_winreg.QueryValueEx(internetSettings, 'ProxyServer')[0])
                if '=' in proxyServer:
                    for p in proxyServer.split(';'):
                        protocol, address = p.split('=', 1)
                        import re
                        if not re.match('^([^/:]+)://', address):
                            address = '%s://%s' % (protocol, address)
                        proxies[protocol] = address

                elif proxyServer[:5] == 'http:':
                    proxies['http'] = proxyServer
                else:
                    proxies['http'] = 'http://%s' % proxyServer
                    proxies['https'] = 'https://%s' % proxyServer
                    proxies['ftp'] = 'ftp://%s' % proxyServer
            internetSettings.Close()
        except (WindowsError, ValueError, TypeError):
            pass

        return proxies


    def getproxies():
        return getproxies_environment() or getproxies_registry()


    def proxy_bypass_registry(host):
        try:
            import _winreg
            import re
        except ImportError:
            return 0

        try:
            internetSettings = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings')
            proxyEnable = _winreg.QueryValueEx(internetSettings, 'ProxyEnable')[0]
            proxyOverride = str(_winreg.QueryValueEx(internetSettings, 'ProxyOverride')[0])
        except WindowsError:
            return 0

        if not proxyEnable or not proxyOverride:
            return 0
        rawHost, port = splitport(host)
        host = [rawHost]
        try:
            addr = socket.gethostbyname(rawHost)
            if addr != rawHost:
                host.append(addr)
        except socket.error:
            pass

        try:
            fqdn = socket.getfqdn(rawHost)
            if fqdn != rawHost:
                host.append(fqdn)
        except socket.error:
            pass

        proxyOverride = proxyOverride.split(';')
        for test in proxyOverride:
            if test == '<local>':
                if '.' not in rawHost:
                    return 1
            test = test.replace('.', '\\.')
            test = test.replace('*', '.*')
            test = test.replace('?', '.')
            for val in host:
                if re.match(test, val, re.I):
                    return 1


    def proxy_bypass(host):
        if getproxies_environment():
            return proxy_bypass_environment(host)
        else:
            return proxy_bypass_registry(host)


else:
    getproxies = getproxies_environment
    proxy_bypass = proxy_bypass_environment

def test1():
    s = ''
    for i in range(256):
        s = s + chr(i)

    s = s * 4
    t0 = time.time()
    qs = quote(s)
    uqs = unquote(qs)
    t1 = time.time()
    if uqs != s:
        print 'Wrong!'
    print repr(s)
    print repr(qs)
    print repr(uqs)
    print round(t1 - t0, 3), 'sec'


def reporthook(blocknum, blocksize, totalsize):
    print 'Block number: %d, Block size: %d, Total size: %d' % (blocknum, blocksize, totalsize)
