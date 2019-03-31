# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/ssl.py
# Compiled at: 2010-10-21 18:49:01
"""This module provides some more Pythonic support for SSL.

Object types:

  SSLSocket -- subtype of socket.socket which does SSL over the socket

Exceptions:

  SSLError -- exception raised for I/O errors

Functions:

  cert_time_to_seconds -- convert time string used for certificate
                          notBefore and notAfter functions to integer
                          seconds past the Epoch (the time values
                          returned from time.time())

  fetch_server_certificate (HOST, PORT) -- fetch the certificate provided
                          by the server running on HOST at port PORT.  No
                          validation of the certificate is performed.

Integer constants:

SSL_ERROR_ZERO_RETURN
SSL_ERROR_WANT_READ
SSL_ERROR_WANT_WRITE
SSL_ERROR_WANT_X509_LOOKUP
SSL_ERROR_SYSCALL
SSL_ERROR_SSL
SSL_ERROR_WANT_CONNECT

SSL_ERROR_EOF
SSL_ERROR_INVALID_ERROR_CODE

The following group define certificate requirements that one side is
allowing/requiring from the other side:

CERT_NONE - no certificates from the other side are required (or will
            be looked at if provided)
CERT_OPTIONAL - certificates are not required, but if provided will be
                validated, and if validation fails, the connection will
                also fail
CERT_REQUIRED - certificates are required, and will be validated, and
                if validation fails, the connection will also fail

The following constants identify various SSL protocol variants:

PROTOCOL_SSLv2
PROTOCOL_SSLv3
PROTOCOL_SSLv23
PROTOCOL_TLSv1
"""
import textwrap
import _ssl
from _ssl import SSLError
from _ssl import CERT_NONE, CERT_OPTIONAL, CERT_REQUIRED
from _ssl import PROTOCOL_SSLv2, PROTOCOL_SSLv3, PROTOCOL_SSLv23, PROTOCOL_TLSv1
from _ssl import RAND_status, RAND_egd, RAND_add
from _ssl import SSL_ERROR_ZERO_RETURN, SSL_ERROR_WANT_READ, SSL_ERROR_WANT_WRITE, SSL_ERROR_WANT_X509_LOOKUP, SSL_ERROR_SYSCALL, SSL_ERROR_SSL, SSL_ERROR_WANT_CONNECT, SSL_ERROR_EOF, SSL_ERROR_INVALID_ERROR_CODE
from socket import socket, _fileobject
from socket import getnameinfo as _getnameinfo
import base64

class SSLSocket(socket):
    """This class implements a subtype of socket.socket that wraps
    the underlying OS socket in an SSL context when necessary, and
    provides read and write methods over that channel."""

    def __init__(self, sock, keyfile=None, certfile=None, server_side=False, cert_reqs=CERT_NONE, ssl_version=PROTOCOL_SSLv23, ca_certs=None, do_handshake_on_connect=True, suppress_ragged_eofs=True):
        socket.__init__(self, _sock=sock._sock)
        self.send = lambda data, flags=0: SSLSocket.send(self, data, flags)
        self.sendto = lambda data, addr, flags=0: SSLSocket.sendto(self, data, addr, flags)
        self.recv = lambda buflen=1024, flags=0: SSLSocket.recv(self, buflen, flags)
        self.recvfrom = lambda addr, buflen=1024, flags=0: SSLSocket.recvfrom(self, addr, buflen, flags)
        self.recv_into = lambda buffer, nbytes=None, flags=0: SSLSocket.recv_into(self, buffer, nbytes, flags)
        self.recvfrom_into = lambda buffer, nbytes=None, flags=0: SSLSocket.recvfrom_into(self, buffer, nbytes, flags)
        if certfile and not keyfile:
            keyfile = certfile
        try:
            socket.getpeername(self)
        except:
            self._sslobj = None
        else:
            self._sslobj = _ssl.sslwrap(self._sock, server_side, keyfile, certfile, cert_reqs, ssl_version, ca_certs)
            if do_handshake_on_connect:
                timeout = self.gettimeout()
                try:
                    self.settimeout(None)
                    self.do_handshake()
                finally:
                    self.settimeout(timeout)

        self.keyfile = keyfile
        self.certfile = certfile
        self.cert_reqs = cert_reqs
        self.ssl_version = ssl_version
        self.ca_certs = ca_certs
        self.do_handshake_on_connect = do_handshake_on_connect
        self.suppress_ragged_eofs = suppress_ragged_eofs
        self._makefile_refs = 0
        return

    def read(self, len=1024):
        """Read up to LEN bytes and return them.
        Return zero-length string on EOF."""
        try:
            return self._sslobj.read(len)
        except SSLError as x:
            if x.args[0] == SSL_ERROR_EOF and self.suppress_ragged_eofs:
                return ''
            raise

    def write(self, data):
        """Write DATA to the underlying SSL channel.  Returns
        number of bytes of DATA actually transmitted."""
        return self._sslobj.write(data)

    def getpeercert(self, binary_form=False):
        """Returns a formatted version of the data in the
        certificate provided by the other end of the SSL channel.
        Return None if no certificate was provided, {} if a
        certificate was provided, but not validated."""
        return self._sslobj.peer_certificate(binary_form)

    def cipher(self):
        if not self._sslobj:
            return None
        else:
            return self._sslobj.cipher()
            return None

    def send--- This code section failed: ---

 167       0	LOAD_FAST         'self'
           3	LOAD_ATTR         '_sslobj'
           6	JUMP_IF_FALSE     '156'

 168       9	LOAD_FAST         'flags'
          12	LOAD_CONST        0
          15	COMPARE_OP        '!='
          18	JUMP_IF_FALSE     '43'

 169      21	LOAD_GLOBAL       'ValueError'

 170      24	LOAD_CONST        'non-zero flags not allowed in calls to send() on %s'

 171      27	LOAD_FAST         'self'
          30	LOAD_ATTR         '__class__'
          33	BINARY_MODULO     ''
          34	CALL_FUNCTION_1   ''
          37	RAISE_VARARGS_1   ''
          40	JUMP_FORWARD      '43'
        43_0	COME_FROM         '40'

 172      43	SETUP_LOOP        '175'
          46	LOAD_GLOBAL       'True'
          49	JUMP_IF_FALSE     '152'

 173      52	SETUP_EXCEPT      '77'

 174      55	LOAD_FAST         'self'
          58	LOAD_ATTR         '_sslobj'
          61	LOAD_ATTR         'write'
          64	LOAD_FAST         'data'
          67	CALL_FUNCTION_1   ''
          70	STORE_FAST        'v'
          73	POP_BLOCK         ''
          74	JUMP_FORWARD      '145'
        77_0	COME_FROM         '52'

 175      77	DUP_TOP           ''
          78	LOAD_GLOBAL       'SSLError'
          81	COMPARE_OP        'exception match'
          84	JUMP_IF_FALSE     '144'
          87	POP_TOP           ''
          88	STORE_FAST        'x'
          91	POP_TOP           ''

 176      92	LOAD_FAST         'x'
          95	LOAD_ATTR         'args'
          98	LOAD_CONST        0
         101	BINARY_SUBSCR     ''
         102	LOAD_GLOBAL       'SSL_ERROR_WANT_READ'
         105	COMPARE_OP        '=='
         108	JUMP_IF_FALSE     '115'

 177     111	LOAD_CONST        0
         114	RETURN_END_IF     ''

 178     115	LOAD_FAST         'x'
         118	LOAD_ATTR         'args'
         121	LOAD_CONST        0
         124	BINARY_SUBSCR     ''
         125	LOAD_GLOBAL       'SSL_ERROR_WANT_WRITE'
         128	COMPARE_OP        '=='
         131	JUMP_IF_FALSE     '138'

 179     134	LOAD_CONST        0
         137	RETURN_END_IF     ''

 181     138	RAISE_VARARGS_0   ''
         141	JUMP_BACK         '46'
         144	END_FINALLY       ''
       145_0	COME_FROM         '74'

 183     145	LOAD_FAST         'v'
         148	RETURN_VALUE      ''
       149_0	COME_FROM         '144'
         149	JUMP_BACK         '46'
         152	POP_BLOCK         ''
       153_0	COME_FROM         '43'
         153	JUMP_FORWARD      '175'

 185     156	LOAD_GLOBAL       'socket'
         159	LOAD_ATTR         'send'
         162	LOAD_FAST         'self'
         165	LOAD_FAST         'data'
         168	LOAD_FAST         'flags'
         171	CALL_FUNCTION_3   ''
         174	RETURN_VALUE      ''
       175_0	COME_FROM         '153'

Syntax error at or near 'POP_BLOCK' token at offset 152

    def sendto(self, data, addr, flags=0):
        if self._sslobj:
            raise ValueError('sendto not allowed on instances of %s' % self.__class__)
        else:
            return socket.sendto(self, data, addr, flags)

    def sendall(self, data, flags=0):
        if self._sslobj:
            if flags != 0:
                raise ValueError('non-zero flags not allowed in calls to sendall() on %s' % self.__class__)
            amount = len(data)
            count = 0
            while 1:
                v = count < amount and self.send(data[count:])
                count += v

            return amount
        else:
            return socket.sendall(self, data, flags)

    def recv--- This code section failed: ---

 210       0	LOAD_FAST         'self'
           3	LOAD_ATTR         '_sslobj'
           6	JUMP_IF_FALSE     '129'

 211       9	LOAD_FAST         'flags'
          12	LOAD_CONST        0
          15	COMPARE_OP        '!='
          18	JUMP_IF_FALSE     '43'

 212      21	LOAD_GLOBAL       'ValueError'

 213      24	LOAD_CONST        'non-zero flags not allowed in calls to sendall() on %s'

 214      27	LOAD_FAST         'self'
          30	LOAD_ATTR         '__class__'
          33	BINARY_MODULO     ''
          34	CALL_FUNCTION_1   ''
          37	RAISE_VARARGS_1   ''
          40	JUMP_FORWARD      '43'
        43_0	COME_FROM         '40'

 215      43	SETUP_LOOP        '148'
          46	LOAD_GLOBAL       'True'
          49	JUMP_IF_FALSE     '125'

 216      52	SETUP_EXCEPT      '72'

 217      55	LOAD_FAST         'self'
          58	LOAD_ATTR         'read'
          61	LOAD_FAST         'buflen'
          64	CALL_FUNCTION_1   ''
          67	RETURN_VALUE      ''
          68	POP_BLOCK         ''
          69	JUMP_BACK         '46'
        72_0	COME_FROM         '52'

 218      72	DUP_TOP           ''
          73	LOAD_GLOBAL       'SSLError'
          76	COMPARE_OP        'exception match'
          79	JUMP_IF_FALSE     '121'
          82	POP_TOP           ''
          83	STORE_FAST        'x'
          86	POP_TOP           ''

 219      87	LOAD_FAST         'x'
          90	LOAD_ATTR         'args'
          93	LOAD_CONST        0
          96	BINARY_SUBSCR     ''
          97	LOAD_GLOBAL       'SSL_ERROR_WANT_READ'
         100	COMPARE_OP        '=='
         103	JUMP_IF_FALSE     '112'

 220     106	CONTINUE          '46'
         109	JUMP_ABSOLUTE     '122'

 222     112	LOAD_FAST         'x'
         115	RAISE_VARARGS_1   ''
         118	JUMP_BACK         '46'
         121	END_FINALLY       ''
       122_0	COME_FROM         '121'
         122	JUMP_BACK         '46'
         125	POP_BLOCK         ''
       126_0	COME_FROM         '43'
         126	JUMP_FORWARD      '148'

 224     129	LOAD_GLOBAL       'socket'
         132	LOAD_ATTR         'recv'
         135	LOAD_FAST         'self'
         138	LOAD_FAST         'buflen'
         141	LOAD_FAST         'flags'
         144	CALL_FUNCTION_3   ''
         147	RETURN_VALUE      ''
       148_0	COME_FROM         '126'

Syntax error at or near 'POP_BLOCK' token at offset 125

    def recv_into--- This code section failed: ---

 227       0	LOAD_FAST         'buffer'
           3	JUMP_IF_FALSE     '33'
           6	LOAD_FAST         'nbytes'
           9	LOAD_CONST        ''
          12	COMPARE_OP        'is'
        15_0	COME_FROM         '3'
          15	JUMP_IF_FALSE     '33'

 228      18	LOAD_GLOBAL       'len'
          21	LOAD_FAST         'buffer'
          24	CALL_FUNCTION_1   ''
          27	STORE_FAST        'nbytes'
          30	JUMP_FORWARD      '54'

 229      33	LOAD_FAST         'nbytes'
          36	LOAD_CONST        ''
          39	COMPARE_OP        'is'
          42	JUMP_IF_FALSE     '54'

 230      45	LOAD_CONST        1024
          48	STORE_FAST        'nbytes'
          51	JUMP_FORWARD      '54'
        54_0	COME_FROM         '30'
        54_1	COME_FROM         '51'

 231      54	LOAD_FAST         'self'
          57	LOAD_ATTR         '_sslobj'
          60	JUMP_IF_FALSE     '211'

 232      63	LOAD_FAST         'flags'
          66	LOAD_CONST        0
          69	COMPARE_OP        '!='
          72	JUMP_IF_FALSE     '97'

 233      75	LOAD_GLOBAL       'ValueError'

 234      78	LOAD_CONST        'non-zero flags not allowed in calls to recv_into() on %s'

 235      81	LOAD_FAST         'self'
          84	LOAD_ATTR         '__class__'
          87	BINARY_MODULO     ''
          88	CALL_FUNCTION_1   ''
          91	RAISE_VARARGS_1   ''
          94	JUMP_FORWARD      '97'
        97_0	COME_FROM         '94'

 236      97	SETUP_LOOP        '233'
         100	LOAD_GLOBAL       'True'
         103	JUMP_IF_FALSE     '207'

 237     106	SETUP_EXCEPT      '154'

 238     109	LOAD_FAST         'self'
         112	LOAD_ATTR         'read'
         115	LOAD_FAST         'nbytes'
         118	CALL_FUNCTION_1   ''
         121	STORE_FAST        'tmp_buffer'

 239     124	LOAD_GLOBAL       'len'
         127	LOAD_FAST         'tmp_buffer'
         130	CALL_FUNCTION_1   ''
         133	STORE_FAST        'v'

 240     136	LOAD_FAST         'tmp_buffer'
         139	LOAD_FAST         'buffer'
         142	LOAD_FAST         'v'
         145	STORE_SLICE+2     ''

 241     146	LOAD_FAST         'v'
         149	RETURN_VALUE      ''
         150	POP_BLOCK         ''
         151	JUMP_BACK         '100'
       154_0	COME_FROM         '106'

 242     154	DUP_TOP           ''
         155	LOAD_GLOBAL       'SSLError'
         158	COMPARE_OP        'exception match'
         161	JUMP_IF_FALSE     '203'
         164	POP_TOP           ''
         165	STORE_FAST        'x'
         168	POP_TOP           ''

 243     169	LOAD_FAST         'x'
         172	LOAD_ATTR         'args'
         175	LOAD_CONST        0
         178	BINARY_SUBSCR     ''
         179	LOAD_GLOBAL       'SSL_ERROR_WANT_READ'
         182	COMPARE_OP        '=='
         185	JUMP_IF_FALSE     '194'

 244     188	CONTINUE          '100'
         191	JUMP_ABSOLUTE     '204'

 246     194	LOAD_FAST         'x'
         197	RAISE_VARARGS_1   ''
         200	JUMP_BACK         '100'
         203	END_FINALLY       ''
       204_0	COME_FROM         '203'
         204	JUMP_BACK         '100'
         207	POP_BLOCK         ''
       208_0	COME_FROM         '97'
         208	JUMP_FORWARD      '233'

 248     211	LOAD_GLOBAL       'socket'
         214	LOAD_ATTR         'recv_into'
         217	LOAD_FAST         'self'
         220	LOAD_FAST         'buffer'
         223	LOAD_FAST         'nbytes'
         226	LOAD_FAST         'flags'
         229	CALL_FUNCTION_4   ''
         232	RETURN_VALUE      ''
       233_0	COME_FROM         '208'
         233	LOAD_CONST        ''
         236	RETURN_VALUE      ''

Syntax error at or near 'POP_BLOCK' token at offset 207

    def recvfrom(self, addr, buflen=1024, flags=0):
        if self._sslobj:
            raise ValueError('recvfrom not allowed on instances of %s' % self.__class__)
        else:
            return socket.recvfrom(self, addr, buflen, flags)

    def recvfrom_into(self, buffer, nbytes=None, flags=0):
        if self._sslobj:
            raise ValueError('recvfrom_into not allowed on instances of %s' % self.__class__)
        else:
            return socket.recvfrom_into(self, buffer, nbytes, flags)

    def pending(self):
        if self._sslobj:
            return self._sslobj.pending()
        else:
            return 0

    def unwrap(self):
        if self._sslobj:
            s = self._sslobj.shutdown()
            self._sslobj = None
            return s
        else:
            raise ValueError('No SSL wrapper around ' + str(self))
            return

    def shutdown(self, how):
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

    def do_handshake(self):
        """Perform a TLS/SSL handshake."""
        self._sslobj.do_handshake()

    def connect(self, addr):
        """Connects to remote ADDR, and then wraps the connection in
        an SSL channel."""
        if self._sslobj:
            raise ValueError('attempt to connect already-connected SSLSocket!')
        socket.connect(self, addr)
        self._sslobj = _ssl.sslwrap(self._sock, False, self.keyfile, self.certfile, self.cert_reqs, self.ssl_version, self.ca_certs)
        if self.do_handshake_on_connect:
            self.do_handshake()

    def accept(self):
        """Accepts a new connection from a remote client, and returns
        a tuple containing that new connection wrapped with a server-side
        SSL channel, and the address of the remote client."""
        newsock, addr = socket.accept(self)
        return (SSLSocket(newsock, keyfile=self.keyfile, certfile=self.certfile, server_side=True, cert_reqs=self.cert_reqs, ssl_version=self.ssl_version, ca_certs=self.ca_certs, do_handshake_on_connect=self.do_handshake_on_connect, suppress_ragged_eofs=self.suppress_ragged_eofs), addr)

    def makefile(self, mode='r', bufsize=-1):
        """Make and return a file-like object that
        works with the SSL connection.  Just use the code
        from the socket module."""
        self._makefile_refs += 1
        return _fileobject(self, mode, bufsize)


def wrap_socket(sock, keyfile=None, certfile=None, server_side=False, cert_reqs=CERT_NONE, ssl_version=PROTOCOL_SSLv23, ca_certs=None, do_handshake_on_connect=True, suppress_ragged_eofs=True):
    return SSLSocket(sock, keyfile=keyfile, certfile=certfile, server_side=server_side, cert_reqs=cert_reqs, ssl_version=ssl_version, ca_certs=ca_certs, do_handshake_on_connect=do_handshake_on_connect, suppress_ragged_eofs=suppress_ragged_eofs)


def cert_time_to_seconds(cert_time):
    """Takes a date-time string in standard ASN1_print form
    ("MON DAY 24HOUR:MINUTE:SEC YEAR TIMEZONE") and return
    a Python time value in seconds past the epoch."""
    import time
    return time.mktime(time.strptime(cert_time, '%b %d %H:%M:%S %Y GMT'))


PEM_HEADER = '-----BEGIN CERTIFICATE-----'
PEM_FOOTER = '-----END CERTIFICATE-----'

def DER_cert_to_PEM_cert(der_cert_bytes):
    """Takes a certificate in binary DER format and returns the
    PEM version of it as a string."""
    if hasattr(base64, 'standard_b64encode'):
        f = base64.standard_b64encode(der_cert_bytes)
        return PEM_HEADER + '\n' + textwrap.fill(f, 64) + PEM_FOOTER + '\n'
    else:
        return PEM_HEADER + '\n' + base64.encodestring(der_cert_bytes) + PEM_FOOTER + '\n'


def PEM_cert_to_DER_cert(pem_cert_string):
    """Takes a certificate in ASCII PEM format and returns the
    DER-encoded version of it as a byte sequence"""
    if not pem_cert_string.startswith(PEM_HEADER):
        raise ValueError('Invalid PEM encoding; must start with %s' % PEM_HEADER)
    if not pem_cert_string.strip().endswith(PEM_FOOTER):
        raise ValueError('Invalid PEM encoding; must end with %s' % PEM_FOOTER)
    d = pem_cert_string.strip()[len(PEM_HEADER):-len(PEM_FOOTER)]
    return base64.decodestring(d)


def get_server_certificate(addr, ssl_version=PROTOCOL_SSLv3, ca_certs=None):
    """Retrieve the certificate from the server at the specified address,
    and return it as a PEM-encoded string.
    If 'ca_certs' is specified, validate the server cert against it.
    If 'ssl_version' is specified, use it in the connection attempt."""
    host, port = addr
    if ca_certs is not None:
        cert_reqs = CERT_REQUIRED
    else:
        cert_reqs = CERT_NONE
    s = wrap_socket(socket(), ssl_version=ssl_version, cert_reqs=cert_reqs, ca_certs=ca_certs)
    s.connect(addr)
    dercert = s.getpeercert(True)
    s.close()
    return DER_cert_to_PEM_cert(dercert)


def get_protocol_name(protocol_code):
    if protocol_code == PROTOCOL_TLSv1:
        return 'TLSv1'
    elif protocol_code == PROTOCOL_SSLv23:
        return 'SSLv23'
    elif protocol_code == PROTOCOL_SSLv2:
        return 'SSLv2'
    elif protocol_code == PROTOCOL_SSLv3:
        return 'SSLv3'
    else:
        return '<unknown>'


def sslwrap_simple(sock, keyfile=None, certfile=None):
    """A replacement for the old socket.ssl function.  Designed
    for compability with Python 2.5 and earlier.  Will disappear in
    Python 3.0."""
    if hasattr(sock, '_sock'):
        sock = sock._sock
    ssl_sock = _ssl.sslwrap(sock, 0, keyfile, certfile, CERT_NONE, PROTOCOL_SSLv23, None)
    try:
        sock.getpeername()
    except:
        pass
    else:
        ssl_sock.do_handshake()

    return ssl_sock