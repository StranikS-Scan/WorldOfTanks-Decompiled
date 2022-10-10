# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ssl.py
import textwrap
import re
import sys
import os
from collections import namedtuple
from contextlib import closing
import _ssl
from _ssl import OPENSSL_VERSION_NUMBER, OPENSSL_VERSION_INFO, OPENSSL_VERSION
from _ssl import _SSLContext
from _ssl import SSLError, SSLZeroReturnError, SSLWantReadError, SSLWantWriteError, SSLSyscallError, SSLEOFError
from _ssl import CERT_NONE, CERT_OPTIONAL, CERT_REQUIRED
from _ssl import txt2obj as _txt2obj, nid2obj as _nid2obj
from _ssl import RAND_status, RAND_add
try:
    from _ssl import RAND_egd
except ImportError:
    pass

def _import_symbols(prefix):
    for n in dir(_ssl):
        if n.startswith(prefix):
            globals()[n] = getattr(_ssl, n)


_import_symbols('OP_')
_import_symbols('ALERT_DESCRIPTION_')
_import_symbols('SSL_ERROR_')
_import_symbols('PROTOCOL_')
_import_symbols('VERIFY_')
from _ssl import HAS_SNI, HAS_ECDH, HAS_NPN, HAS_ALPN, HAS_TLSv1_3
from _ssl import _OPENSSL_API_VERSION
_PROTOCOL_NAMES = {value:name for name, value in globals().items() if name.startswith('PROTOCOL_') and name != 'PROTOCOL_SSLv23'}
PROTOCOL_SSLv23 = PROTOCOL_TLS
try:
    _SSLv2_IF_EXISTS = PROTOCOL_SSLv2
except NameError:
    _SSLv2_IF_EXISTS = None

from socket import socket, _fileobject, _delegate_methods, error as socket_error
if sys.platform == 'win32':
    from _ssl import enum_certificates, enum_crls
from socket import socket, AF_INET, SOCK_STREAM, create_connection
from socket import SOL_SOCKET, SO_TYPE
import base64
import errno
import warnings
if _ssl.HAS_TLS_UNIQUE:
    CHANNEL_BINDING_TYPES = ['tls-unique']
else:
    CHANNEL_BINDING_TYPES = []
_DEFAULT_CIPHERS = 'TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:ECDH+AESGCM:ECDH+CHACHA20:DH+AESGCM:DH+CHACHA20:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:DH+HIGH:RSA+AESGCM:RSA+AES:RSA+HIGH:!aNULL:!eNULL:!MD5:!3DES'
_RESTRICTED_SERVER_CIPHERS = 'TLS13-AES-256-GCM-SHA384:TLS13-CHACHA20-POLY1305-SHA256:TLS13-AES-128-GCM-SHA256:ECDH+AESGCM:ECDH+CHACHA20:DH+AESGCM:DH+CHACHA20:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:DH+HIGH:RSA+AESGCM:RSA+AES:RSA+HIGH:!aNULL:!eNULL:!MD5:!DSS:!RC4:!3DES'

class CertificateError(ValueError):
    pass


def _dnsname_match(dn, hostname, max_wildcards=1):
    pats = []
    if not dn:
        return False
    pieces = dn.split('.')
    leftmost = pieces[0]
    remainder = pieces[1:]
    wildcards = leftmost.count('*')
    if wildcards > max_wildcards:
        raise CertificateError('too many wildcards in certificate DNS name: ' + repr(dn))
    if not wildcards:
        return dn.lower() == hostname.lower()
    if leftmost == '*':
        pats.append('[^.]+')
    elif leftmost.startswith('xn--') or hostname.startswith('xn--'):
        pats.append(re.escape(leftmost))
    else:
        pats.append(re.escape(leftmost).replace('\\*', '[^.]*'))
    for frag in remainder:
        pats.append(re.escape(frag))

    pat = re.compile('\\A' + '\\.'.join(pats) + '\\Z', re.IGNORECASE)
    return pat.match(hostname)


def match_hostname(cert, hostname):
    if not cert:
        raise ValueError('empty or no certificate, match_hostname needs a SSL socket or SSL context with either CERT_OPTIONAL or CERT_REQUIRED')
    dnsnames = []
    san = cert.get('subjectAltName', ())
    for key, value in san:
        if key == 'DNS':
            if _dnsname_match(value, hostname):
                return
            dnsnames.append(value)

    if not dnsnames:
        for sub in cert.get('subject', ()):
            for key, value in sub:
                if key == 'commonName':
                    if _dnsname_match(value, hostname):
                        return
                    dnsnames.append(value)

    if len(dnsnames) > 1:
        raise CertificateError("hostname %r doesn't match either of %s" % (hostname, ', '.join(map(repr, dnsnames))))
    elif len(dnsnames) == 1:
        raise CertificateError("hostname %r doesn't match %r" % (hostname, dnsnames[0]))
    else:
        raise CertificateError('no appropriate commonName or subjectAltName fields were found')


DefaultVerifyPaths = namedtuple('DefaultVerifyPaths', 'cafile capath openssl_cafile_env openssl_cafile openssl_capath_env openssl_capath')

def get_default_verify_paths():
    parts = _ssl.get_default_verify_paths()
    cafile = os.environ.get(parts[0], parts[1])
    capath = os.environ.get(parts[2], parts[3])
    return DefaultVerifyPaths((cafile if os.path.isfile(cafile) else None), (capath if os.path.isdir(capath) else None), *parts)


class _ASN1Object(namedtuple('_ASN1Object', 'nid shortname longname oid')):
    __slots__ = ()

    def __new__(cls, oid):
        return super(_ASN1Object, cls).__new__(cls, *_txt2obj(oid, name=False))

    @classmethod
    def fromnid(cls, nid):
        return super(_ASN1Object, cls).__new__(cls, *_nid2obj(nid))

    @classmethod
    def fromname(cls, name):
        return super(_ASN1Object, cls).__new__(cls, *_txt2obj(name, name=True))


class Purpose(_ASN1Object):
    pass


Purpose.SERVER_AUTH = Purpose('1.3.6.1.5.5.7.3.1')
Purpose.CLIENT_AUTH = Purpose('1.3.6.1.5.5.7.3.2')
_certificates = {}

class SSLContext(_SSLContext):
    __slots__ = ('protocol', '__weakref__')
    _windows_cert_stores = ('CA', 'ROOT')

    def __new__(cls, protocol, *args, **kwargs):
        self = _SSLContext.__new__(cls, protocol)
        if protocol != _SSLv2_IF_EXISTS:
            self.set_ciphers(_DEFAULT_CIPHERS)
        return self

    def __init__(self, protocol):
        self.protocol = protocol

    def wrap_socket(self, sock, server_side=False, do_handshake_on_connect=True, suppress_ragged_eofs=True, server_hostname=None):
        return SSLSocket(sock=sock, server_side=server_side, do_handshake_on_connect=do_handshake_on_connect, suppress_ragged_eofs=suppress_ragged_eofs, server_hostname=server_hostname, _context=self)

    def set_npn_protocols(self, npn_protocols):
        protos = bytearray()
        for protocol in npn_protocols:
            b = protocol.encode('ascii')
            if len(b) == 0 or len(b) > 255:
                raise SSLError('NPN protocols must be 1 to 255 in length')
            protos.append(len(b))
            protos.extend(b)

        self._set_npn_protocols(protos)

    def set_alpn_protocols(self, alpn_protocols):
        protos = bytearray()
        for protocol in alpn_protocols:
            b = protocol.encode('ascii')
            if len(b) == 0 or len(b) > 255:
                raise SSLError('ALPN protocols must be 1 to 255 in length')
            protos.append(len(b))
            protos.extend(b)

        self._set_alpn_protocols(protos)

    def _load_windows_store_certs(self, storename, purpose):
        certs = bytearray()
        if _certificates.get(storename) is None:
            try:
                _certificates[storename] = enum_certificates(storename)
            except OSError:
                warnings.warn('unable to enumerate Windows certificate store')
                _certificates[storename] = []

        for cert, encoding, trust in _certificates[storename]:
            if encoding == 'x509_asn':
                if trust is True or purpose.oid in trust:
                    certs.extend(cert)

        if certs:
            self.load_verify_locations(cadata=certs)
        return certs

    def load_default_certs(self, purpose=Purpose.SERVER_AUTH):
        if not isinstance(purpose, _ASN1Object):
            raise TypeError(purpose)
        if sys.platform == 'win32':
            for storename in self._windows_cert_stores:
                self._load_windows_store_certs(storename, purpose)

        self.set_default_verify_paths()


def create_default_context(purpose=Purpose.SERVER_AUTH, cafile=None, capath=None, cadata=None):
    if not isinstance(purpose, _ASN1Object):
        raise TypeError(purpose)
    context = SSLContext(PROTOCOL_TLS)
    if purpose == Purpose.SERVER_AUTH:
        context.verify_mode = CERT_REQUIRED
        context.check_hostname = True
    elif purpose == Purpose.CLIENT_AUTH:
        context.set_ciphers(_RESTRICTED_SERVER_CIPHERS)
    if cafile or capath or cadata:
        context.load_verify_locations(cafile, capath, cadata)
    elif context.verify_mode != CERT_NONE:
        context.load_default_certs(purpose)
    return context


def _create_unverified_context(protocol=PROTOCOL_TLS, cert_reqs=None, check_hostname=False, purpose=Purpose.SERVER_AUTH, certfile=None, keyfile=None, cafile=None, capath=None, cadata=None):
    if not isinstance(purpose, _ASN1Object):
        raise TypeError(purpose)
    context = SSLContext(protocol)
    if cert_reqs is not None:
        context.verify_mode = cert_reqs
    context.check_hostname = check_hostname
    if keyfile and not certfile:
        raise ValueError('certfile must be specified')
    if certfile or keyfile:
        context.load_cert_chain(certfile, keyfile)
    if cafile or capath or cadata:
        context.load_verify_locations(cafile, capath, cadata)
    elif context.verify_mode != CERT_NONE:
        context.load_default_certs(purpose)
    return context


_create_stdlib_context = _create_unverified_context
_https_verify_envvar = 'PYTHONHTTPSVERIFY'

def _get_https_context_factory():
    if not sys.flags.ignore_environment:
        config_setting = os.environ.get(_https_verify_envvar)
        if config_setting == '0':
            return _create_unverified_context
    return create_default_context


_create_default_https_context = _get_https_context_factory()

def _https_verify_certificates(enable=True):
    global _create_default_https_context
    if enable:
        _create_default_https_context = create_default_context
    else:
        _create_default_https_context = _create_unverified_context


class SSLSocket(socket):

    def __init__(self, sock=None, keyfile=None, certfile=None, server_side=False, cert_reqs=CERT_NONE, ssl_version=PROTOCOL_TLS, ca_certs=None, do_handshake_on_connect=True, family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None, suppress_ragged_eofs=True, npn_protocols=None, ciphers=None, server_hostname=None, _context=None):
        self._makefile_refs = 0
        if _context:
            self._context = _context
        else:
            if server_side and not certfile:
                raise ValueError('certfile must be specified for server-side operations')
            if keyfile and not certfile:
                raise ValueError('certfile must be specified')
            if certfile and not keyfile:
                keyfile = certfile
            self._context = SSLContext(ssl_version)
            self._context.verify_mode = cert_reqs
            if ca_certs:
                self._context.load_verify_locations(ca_certs)
            if certfile:
                self._context.load_cert_chain(certfile, keyfile)
            if npn_protocols:
                self._context.set_npn_protocols(npn_protocols)
            if ciphers:
                self._context.set_ciphers(ciphers)
            self.keyfile = keyfile
            self.certfile = certfile
            self.cert_reqs = cert_reqs
            self.ssl_version = ssl_version
            self.ca_certs = ca_certs
            self.ciphers = ciphers
        if sock.getsockopt(SOL_SOCKET, SO_TYPE) != SOCK_STREAM:
            raise NotImplementedError('only stream sockets are supported')
        socket.__init__(self, _sock=sock._sock)
        for attr in _delegate_methods:
            try:
                delattr(self, attr)
            except AttributeError:
                pass

        if server_side and server_hostname:
            raise ValueError('server_hostname can only be specified in client mode')
        if self._context.check_hostname and not server_hostname:
            raise ValueError('check_hostname requires server_hostname')
        self.server_side = server_side
        self.server_hostname = server_hostname
        self.do_handshake_on_connect = do_handshake_on_connect
        self.suppress_ragged_eofs = suppress_ragged_eofs
        try:
            self.getpeername()
        except socket_error as e:
            if e.errno != errno.ENOTCONN:
                raise
            connected = False
        else:
            connected = True

        self._closed = False
        self._sslobj = None
        self._connected = connected
        if connected:
            try:
                self._sslobj = self._context._wrap_socket(self._sock, server_side, server_hostname, ssl_sock=self)
                if do_handshake_on_connect:
                    timeout = self.gettimeout()
                    if timeout == 0.0:
                        raise ValueError('do_handshake_on_connect should not be specified for non-blocking sockets')
                    self.do_handshake()
            except (OSError, ValueError):
                self.close()
                raise

        return

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, ctx):
        self._context = ctx
        self._sslobj.context = ctx

    def dup(self):
        raise NotImplementedError("Can't dup() %s instances" % self.__class__.__name__)

    def _checkClosed(self, msg=None):
        pass

    def _check_connected(self):
        if not self._connected:
            self.getpeername()

    def read(self, len=1024, buffer=None):
        self._checkClosed()
        if not self._sslobj:
            raise ValueError('Read on closed or unwrapped SSL socket.')
        try:
            if buffer is not None:
                v = self._sslobj.read(len, buffer)
            else:
                v = self._sslobj.read(len)
            return v
        except SSLError as x:
            if x.args[0] == SSL_ERROR_EOF and self.suppress_ragged_eofs:
                if buffer is not None:
                    return 0
                else:
                    return ''
            else:
                raise

        return

    def write(self, data):
        self._checkClosed()
        if not self._sslobj:
            raise ValueError('Write on closed or unwrapped SSL socket.')
        return self._sslobj.write(data)

    def getpeercert(self, binary_form=False):
        self._checkClosed()
        self._check_connected()
        return self._sslobj.peer_certificate(binary_form)

    def selected_npn_protocol(self):
        self._checkClosed()
        if not self._sslobj or not _ssl.HAS_NPN:
            return None
        else:
            return self._sslobj.selected_npn_protocol()
            return None

    def selected_alpn_protocol(self):
        self._checkClosed()
        if not self._sslobj or not _ssl.HAS_ALPN:
            return None
        else:
            return self._sslobj.selected_alpn_protocol()
            return None

    def cipher(self):
        self._checkClosed()
        if not self._sslobj:
            return None
        else:
            return self._sslobj.cipher()
            return None

    def compression(self):
        self._checkClosed()
        if not self._sslobj:
            return None
        else:
            return self._sslobj.compression()
            return None

    def send(self, data, flags=0):
        self._checkClosed()
        if self._sslobj:
            if flags != 0:
                raise ValueError('non-zero flags not allowed in calls to send() on %s' % self.__class__)
            try:
                v = self._sslobj.write(data)
            except SSLError as x:
                if x.args[0] == SSL_ERROR_WANT_READ:
                    return 0
                if x.args[0] == SSL_ERROR_WANT_WRITE:
                    return 0
                raise
            else:
                return v

        else:
            return self._sock.send(data, flags)

    def sendto(self, data, flags_or_addr, addr=None):
        self._checkClosed()
        if self._sslobj:
            raise ValueError('sendto not allowed on instances of %s' % self.__class__)
        else:
            if addr is None:
                return self._sock.sendto(data, flags_or_addr)
            return self._sock.sendto(data, flags_or_addr, addr)
        return

    def sendall(self, data, flags=0):
        self._checkClosed()
        if self._sslobj:
            if flags != 0:
                raise ValueError('non-zero flags not allowed in calls to sendall() on %s' % self.__class__)
            amount = len(data)
            count = 0
            while count < amount:
                v = self.send(data[count:])
                count += v

            return amount
        else:
            return socket.sendall(self, data, flags)

    def recv(self, buflen=1024, flags=0):
        self._checkClosed()
        if self._sslobj:
            if flags != 0:
                raise ValueError('non-zero flags not allowed in calls to recv() on %s' % self.__class__)
            return self.read(buflen)
        else:
            return self._sock.recv(buflen, flags)

    def recv_into(self, buffer, nbytes=None, flags=0):
        self._checkClosed()
        if buffer and nbytes is None:
            nbytes = len(buffer)
        elif nbytes is None:
            nbytes = 1024
        if self._sslobj:
            if flags != 0:
                raise ValueError('non-zero flags not allowed in calls to recv_into() on %s' % self.__class__)
            return self.read(nbytes, buffer)
        else:
            return self._sock.recv_into(buffer, nbytes, flags)
            return

    def recvfrom(self, buflen=1024, flags=0):
        self._checkClosed()
        if self._sslobj:
            raise ValueError('recvfrom not allowed on instances of %s' % self.__class__)
        else:
            return self._sock.recvfrom(buflen, flags)

    def recvfrom_into(self, buffer, nbytes=None, flags=0):
        self._checkClosed()
        if self._sslobj:
            raise ValueError('recvfrom_into not allowed on instances of %s' % self.__class__)
        else:
            return self._sock.recvfrom_into(buffer, nbytes, flags)

    def pending(self):
        self._checkClosed()
        if self._sslobj:
            return self._sslobj.pending()
        else:
            return 0

    def shutdown(self, how):
        self._checkClosed()
        self._sslobj = None
        socket.shutdown(self, how)
        return

    def close(self):
        if self._makefile_refs < 1:
            self._sslobj = None
            socket.close(self)
        else:
            self._makefile_refs -= 1
        return

    def unwrap(self):
        if self._sslobj:
            s = self._sslobj.shutdown()
            self._sslobj = None
            return s
        else:
            raise ValueError('No SSL wrapper around ' + str(self))
            return

    def _real_close(self):
        self._sslobj = None
        socket._real_close(self)
        return

    def do_handshake(self, block=False):
        self._check_connected()
        timeout = self.gettimeout()
        try:
            if timeout == 0.0 and block:
                self.settimeout(None)
            self._sslobj.do_handshake()
        finally:
            self.settimeout(timeout)

        if self.context.check_hostname:
            if not self.server_hostname:
                raise ValueError('check_hostname needs server_hostname argument')
            match_hostname(self.getpeercert(), self.server_hostname)
        return

    def _real_connect(self, addr, connect_ex):
        if self.server_side:
            raise ValueError("can't connect in server-side mode")
        if self._connected:
            raise ValueError('attempt to connect already-connected SSLSocket!')
        self._sslobj = self.context._wrap_socket(self._sock, False, self.server_hostname, ssl_sock=self)
        try:
            if connect_ex:
                rc = socket.connect_ex(self, addr)
            else:
                rc = None
                socket.connect(self, addr)
            if not rc:
                self._connected = True
                if self.do_handshake_on_connect:
                    self.do_handshake()
            return rc
        except (OSError, ValueError):
            self._sslobj = None
            raise

        return

    def connect(self, addr):
        self._real_connect(addr, False)

    def connect_ex(self, addr):
        return self._real_connect(addr, True)

    def accept(self):
        newsock, addr = socket.accept(self)
        newsock = self.context.wrap_socket(newsock, do_handshake_on_connect=self.do_handshake_on_connect, suppress_ragged_eofs=self.suppress_ragged_eofs, server_side=True)
        return (newsock, addr)

    def makefile(self, mode='r', bufsize=-1):
        self._makefile_refs += 1
        return _fileobject(self, mode, bufsize, close=True)

    def get_channel_binding(self, cb_type='tls-unique'):
        if cb_type not in CHANNEL_BINDING_TYPES:
            raise ValueError('Unsupported channel binding type')
        if cb_type != 'tls-unique':
            raise NotImplementedError('{0} channel binding type not implemented'.format(cb_type))
        return None if self._sslobj is None else self._sslobj.tls_unique_cb()

    def version(self):
        return None if self._sslobj is None else self._sslobj.version()


def wrap_socket(sock, keyfile=None, certfile=None, server_side=False, cert_reqs=CERT_NONE, ssl_version=PROTOCOL_TLS, ca_certs=None, do_handshake_on_connect=True, suppress_ragged_eofs=True, ciphers=None):
    return SSLSocket(sock=sock, keyfile=keyfile, certfile=certfile, server_side=server_side, cert_reqs=cert_reqs, ssl_version=ssl_version, ca_certs=ca_certs, do_handshake_on_connect=do_handshake_on_connect, suppress_ragged_eofs=suppress_ragged_eofs, ciphers=ciphers)


def cert_time_to_seconds(cert_time):
    from time import strptime
    from calendar import timegm
    months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    time_format = ' %d %H:%M:%S %Y GMT'
    try:
        month_number = months.index(cert_time[:3].title()) + 1
    except ValueError:
        raise ValueError('time data %r does not match format "%%b%s"' % (cert_time, time_format))
    else:
        tt = strptime(cert_time[3:], time_format)
        return timegm((tt[0], month_number) + tt[2:6])


PEM_HEADER = '-----BEGIN CERTIFICATE-----'
PEM_FOOTER = '-----END CERTIFICATE-----'

def DER_cert_to_PEM_cert(der_cert_bytes):
    f = base64.standard_b64encode(der_cert_bytes).decode('ascii')
    return PEM_HEADER + '\n' + textwrap.fill(f, 64) + '\n' + PEM_FOOTER + '\n'


def PEM_cert_to_DER_cert(pem_cert_string):
    if not pem_cert_string.startswith(PEM_HEADER):
        raise ValueError('Invalid PEM encoding; must start with %s' % PEM_HEADER)
    if not pem_cert_string.strip().endswith(PEM_FOOTER):
        raise ValueError('Invalid PEM encoding; must end with %s' % PEM_FOOTER)
    d = pem_cert_string.strip()[len(PEM_HEADER):-len(PEM_FOOTER)]
    return base64.decodestring(d.encode('ASCII', 'strict'))


def get_server_certificate(addr, ssl_version=PROTOCOL_TLS, ca_certs=None):
    host, port = addr
    if ca_certs is not None:
        cert_reqs = CERT_REQUIRED
    else:
        cert_reqs = CERT_NONE
    context = _create_stdlib_context(ssl_version, cert_reqs=cert_reqs, cafile=ca_certs)
    with closing(create_connection(addr)) as sock:
        with closing(context.wrap_socket(sock)) as sslsock:
            dercert = sslsock.getpeercert(True)
    return DER_cert_to_PEM_cert(dercert)


def get_protocol_name(protocol_code):
    return _PROTOCOL_NAMES.get(protocol_code, '<unknown>')


def sslwrap_simple(sock, keyfile=None, certfile=None):
    if hasattr(sock, '_sock'):
        sock = sock._sock
    ctx = SSLContext(PROTOCOL_SSLv23)
    if keyfile or certfile:
        ctx.load_cert_chain(certfile, keyfile)
    ssl_sock = ctx._wrap_socket(sock, server_side=False)
    try:
        sock.getpeername()
    except socket_error:
        pass
    else:
        ssl_sock.do_handshake()

    return ssl_sock
