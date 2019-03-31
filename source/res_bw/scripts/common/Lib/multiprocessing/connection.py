# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/multiprocessing/connection.py
# Compiled at: 2010-08-25 17:58:21
__all__ = ['Client', 'Listener', 'Pipe']
import os
import sys
import socket
import errno
import time
import tempfile
import itertools
import _multiprocessing
from multiprocessing import current_process, AuthenticationError
from multiprocessing.util import get_temp_dir, Finalize, sub_debug, debug
from multiprocessing.forking import duplicate, close
BUFSIZE = 8192
_mmap_counter = itertools.count()
default_family = 'AF_INET'
families = ['AF_INET']
if hasattr(socket, 'AF_UNIX'):
    default_family = 'AF_UNIX'
    families += ['AF_UNIX']
if sys.platform == 'win32':
    default_family = 'AF_PIPE'
    families += ['AF_PIPE']

def arbitrary_address(family):
    """
    Return an arbitrary free address for the given family
    """
    if family == 'AF_INET':
        return ('localhost', 0)
    if family == 'AF_UNIX':
        return tempfile.mktemp(prefix='listener-', dir=get_temp_dir())
    if family == 'AF_PIPE':
        return tempfile.mktemp(prefix='\\\\.\\pipe\\pyc-%d-%d-' % (os.getpid(), _mmap_counter.next()))
    raise ValueError('unrecognized family')


def address_type(address):
    """
    Return the types of the address
    
    This can be 'AF_INET', 'AF_UNIX', or 'AF_PIPE'
    """
    if type(address) == tuple:
        return 'AF_INET'
    if type(address) is str and address.startswith('\\\\'):
        return 'AF_PIPE'
    if type(address) is str:
        return 'AF_UNIX'
    raise ValueError('address type of %r unrecognized' % address)


class Listener(object):
    """
    Returns a listener object.
    
    This is a wrapper for a bound socket which is 'listening' for
    connections, or for a Windows named pipe.
    """

    def __init__(self, address=None, family=None, backlog=1, authkey=None):
        if not family:
            if not (address and address_type(address)):
                family = default_family
                address = address or arbitrary_address(family)
                self._listener = family == 'AF_PIPE' and PipeListener(address, backlog)
            else:
                self._listener = SocketListener(address, family, backlog)
            raise authkey is not None and not isinstance(authkey, bytes) and TypeError, 'authkey should be a byte string'
        self._authkey = authkey
        return

    def accept(self):
        """
        Accept a connection on the bound socket or named pipe of `self`.
        
        Returns a `Connection` object.
        """
        c = self._listener.accept()
        if self._authkey:
            deliver_challenge(c, self._authkey)
            answer_challenge(c, self._authkey)
        return c

    def close(self):
        """
        Close the bound socket or named pipe of `self`.
        """
        return self._listener.close()

    address = property(lambda self: self._listener._address)
    last_accepted = property(lambda self: self._listener._last_accepted)


def Client(address, family=None, authkey=None):
    """
    Returns a connection to the address of a `Listener`
    """
    if not family:
        family = address_type(address)
        if family == 'AF_PIPE':
            c = PipeClient(address)
        else:
            c = SocketClient(address)
        if authkey is not None and not isinstance(authkey, bytes):
            raise TypeError, 'authkey should be a byte string'
        authkey is not None and answer_challenge(c, authkey)
        deliver_challenge(c, authkey)
    return c


if sys.platform != 'win32':

    def Pipe(duplex=True):
        """
        Returns pair of connection objects at either end of a pipe
        """
        if duplex:
            s1, s2 = socket.socketpair()
            c1 = _multiprocessing.Connection(os.dup(s1.fileno()))
            c2 = _multiprocessing.Connection(os.dup(s2.fileno()))
            s1.close()
            s2.close()
        else:
            fd1, fd2 = os.pipe()
            c1 = _multiprocessing.Connection(fd1, writable=False)
            c2 = _multiprocessing.Connection(fd2, readable=False)
        return (c1, c2)


else:
    from ._multiprocessing import win32

    def Pipe(duplex=True):
        """
        Returns pair of connection objects at either end of a pipe
        """
        address = arbitrary_address('AF_PIPE')
        if duplex:
            openmode = win32.PIPE_ACCESS_DUPLEX
            access = win32.GENERIC_READ | win32.GENERIC_WRITE
            obsize, ibsize = BUFSIZE, BUFSIZE
        else:
            openmode = win32.PIPE_ACCESS_INBOUND
            access = win32.GENERIC_WRITE
            obsize, ibsize = 0, BUFSIZE
        h1 = win32.CreateNamedPipe(address, openmode, win32.PIPE_TYPE_MESSAGE | win32.PIPE_READMODE_MESSAGE | win32.PIPE_WAIT, 1, obsize, ibsize, win32.NMPWAIT_WAIT_FOREVER, win32.NULL)
        h2 = win32.CreateFile(address, access, 0, win32.NULL, win32.OPEN_EXISTING, 0, win32.NULL)
        win32.SetNamedPipeHandleState(h2, win32.PIPE_READMODE_MESSAGE, None, None)
        try:
            win32.ConnectNamedPipe(h1, win32.NULL)
        except WindowsError as e:
            if e.args[0] != win32.ERROR_PIPE_CONNECTED:
                raise

        c1 = _multiprocessing.PipeConnection(h1, writable=duplex)
        c2 = _multiprocessing.PipeConnection(h2, readable=duplex)
        return (c1, c2)


class SocketListener(object):
    """
    Representation of a socket which is bound to an address and listening
    """

    def __init__(self, address, family, backlog=1):
        self._socket = socket.socket(getattr(socket, family))
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(address)
        self._socket.listen(backlog)
        self._address = self._socket.getsockname()
        self._family = family
        self._last_accepted = None
        if family == 'AF_UNIX':
            self._unlink = Finalize(self, os.unlink, args=(address,), exitpriority=0)
        else:
            self._unlink = None
        return

    def accept(self):
        s, self._last_accepted = self._socket.accept()
        fd = duplicate(s.fileno())
        conn = _multiprocessing.Connection(fd)
        s.close()
        return conn

    def close(self):
        self._socket.close()
        if self._unlink is not None:
            self._unlink()
        return


def SocketClient--- This code section failed: ---

 248       0	LOAD_GLOBAL       'address_type'
           3	LOAD_FAST         'address'
           6	CALL_FUNCTION_1   ''
           9	STORE_FAST        'family'

 249      12	LOAD_GLOBAL       'socket'
          15	LOAD_ATTR         'socket'
          18	LOAD_GLOBAL       'getattr'
          21	LOAD_GLOBAL       'socket'
          24	LOAD_FAST         'family'
          27	CALL_FUNCTION_2   ''
          30	CALL_FUNCTION_1   ''
          33	STORE_FAST        's'

 251      36	SETUP_LOOP        '142'

 252      39	SETUP_EXCEPT      '59'

 253      42	LOAD_FAST         's'
          45	LOAD_ATTR         'connect'
          48	LOAD_FAST         'address'
          51	CALL_FUNCTION_1   ''
          54	POP_TOP           ''
          55	POP_BLOCK         ''
          56	JUMP_FORWARD      '135'
        59_0	COME_FROM         '39'

 254      59	DUP_TOP           ''
          60	LOAD_GLOBAL       'socket'
          63	LOAD_ATTR         'error'
          66	COMPARE_OP        'exception match'
          69	JUMP_IF_FALSE     '134'
          72	POP_TOP           ''
          73	STORE_FAST        'e'
          76	POP_TOP           ''

 255      77	LOAD_FAST         'e'
          80	LOAD_ATTR         'args'
          83	LOAD_CONST        0
          86	BINARY_SUBSCR     ''
          87	LOAD_GLOBAL       'errno'
          90	LOAD_ATTR         'ECONNREFUSED'
          93	COMPARE_OP        '!='
          96	JUMP_IF_FALSE     '118'

 256      99	LOAD_GLOBAL       'debug'
         102	LOAD_CONST        'failed to connect to address %s'
         105	LOAD_FAST         'address'
         108	CALL_FUNCTION_2   ''
         111	POP_TOP           ''

 257     112	RAISE_VARARGS_0   ''
         115	JUMP_FORWARD      '118'
       118_0	COME_FROM         '115'

 258     118	LOAD_GLOBAL       'time'
         121	LOAD_ATTR         'sleep'
         124	LOAD_CONST        0.01
         127	CALL_FUNCTION_1   ''
         130	POP_TOP           ''
         131	JUMP_BACK         '39'
         134	END_FINALLY       ''
       135_0	COME_FROM         '56'

 260     135	BREAK_LOOP        ''
       136_0	COME_FROM         '134'
         136	JUMP_BACK         '39'

 262     139	RAISE_VARARGS_0   ''
       142_0	COME_FROM         '36'

 264     142	LOAD_GLOBAL       'duplicate'
         145	LOAD_FAST         's'
         148	LOAD_ATTR         'fileno'
         151	CALL_FUNCTION_0   ''
         154	CALL_FUNCTION_1   ''
         157	STORE_FAST        'fd'

 265     160	LOAD_GLOBAL       '_multiprocessing'
         163	LOAD_ATTR         'Connection'
         166	LOAD_FAST         'fd'
         169	CALL_FUNCTION_1   ''
         172	STORE_FAST        'conn'

 266     175	LOAD_FAST         's'
         178	LOAD_ATTR         'close'
         181	CALL_FUNCTION_0   ''
         184	POP_TOP           ''

 267     185	LOAD_FAST         'conn'
         188	RETURN_VALUE      ''
          -1	RETURN_LAST       ''

Syntax error at or near 'RAISE_VARARGS_0' token at offset 139


if sys.platform == 'win32':

    class PipeListener(object):
        """
        Representation of a named pipe
        """

        def __init__(self, address, backlog=None):
            self._address = address
            handle = win32.CreateNamedPipe(address, win32.PIPE_ACCESS_DUPLEX, win32.PIPE_TYPE_MESSAGE | win32.PIPE_READMODE_MESSAGE | win32.PIPE_WAIT, win32.PIPE_UNLIMITED_INSTANCES, BUFSIZE, BUFSIZE, win32.NMPWAIT_WAIT_FOREVER, win32.NULL)
            self._handle_queue = [handle]
            self._last_accepted = None
            sub_debug('listener created with address=%r', self._address)
            self.close = Finalize(self, PipeListener._finalize_pipe_listener, args=(self._handle_queue, self._address), exitpriority=0)
            return

        def accept(self):
            newhandle = win32.CreateNamedPipe(self._address, win32.PIPE_ACCESS_DUPLEX, win32.PIPE_TYPE_MESSAGE | win32.PIPE_READMODE_MESSAGE | win32.PIPE_WAIT, win32.PIPE_UNLIMITED_INSTANCES, BUFSIZE, BUFSIZE, win32.NMPWAIT_WAIT_FOREVER, win32.NULL)
            self._handle_queue.append(newhandle)
            handle = self._handle_queue.pop(0)
            try:
                win32.ConnectNamedPipe(handle, win32.NULL)
            except WindowsError as e:
                if e.args[0] != win32.ERROR_PIPE_CONNECTED:
                    raise

            return _multiprocessing.PipeConnection(handle)

        @staticmethod
        def _finalize_pipe_listener(queue, address):
            sub_debug('closing listener with address=%r', address)
            for handle in queue:
                close(handle)


    def PipeClient--- This code section failed: ---

 325       0	SETUP_LOOP        '141'

 326       3	SETUP_EXCEPT      '78'

 327       6	LOAD_GLOBAL       'win32'
           9	LOAD_ATTR         'WaitNamedPipe'
          12	LOAD_FAST         'address'
          15	LOAD_CONST        1000
          18	CALL_FUNCTION_2   ''
          21	POP_TOP           ''

 328      22	LOAD_GLOBAL       'win32'
          25	LOAD_ATTR         'CreateFile'

 329      28	LOAD_FAST         'address'
          31	LOAD_GLOBAL       'win32'
          34	LOAD_ATTR         'GENERIC_READ'
          37	LOAD_GLOBAL       'win32'
          40	LOAD_ATTR         'GENERIC_WRITE'
          43	BINARY_OR         ''

 330      44	LOAD_CONST        0
          47	LOAD_GLOBAL       'win32'
          50	LOAD_ATTR         'NULL'
          53	LOAD_GLOBAL       'win32'
          56	LOAD_ATTR         'OPEN_EXISTING'
          59	LOAD_CONST        0
          62	LOAD_GLOBAL       'win32'
          65	LOAD_ATTR         'NULL'
          68	CALL_FUNCTION_7   ''
          71	STORE_FAST        'h'
          74	POP_BLOCK         ''
          75	JUMP_FORWARD      '134'
        78_0	COME_FROM         '3'

 332      78	DUP_TOP           ''
          79	LOAD_GLOBAL       'WindowsError'
          82	COMPARE_OP        'exception match'
          85	JUMP_IF_FALSE     '133'
          88	POP_TOP           ''
          89	STORE_FAST        'e'
          92	POP_TOP           ''

 333      93	LOAD_FAST         'e'
          96	LOAD_ATTR         'args'
          99	LOAD_CONST        0
         102	BINARY_SUBSCR     ''
         103	LOAD_GLOBAL       'win32'
         106	LOAD_ATTR         'ERROR_SEM_TIMEOUT'

 334     109	LOAD_GLOBAL       'win32'
         112	LOAD_ATTR         'ERROR_PIPE_BUSY'
         115	BUILD_TUPLE_2     ''
         118	COMPARE_OP        'not in'
         121	JUMP_IF_FALSE     '130'

 335     124	RAISE_VARARGS_0   ''
         127	JUMP_ABSOLUTE     '135'
         130	JUMP_BACK         '3'
         133	END_FINALLY       ''
       134_0	COME_FROM         '75'

 337     134	BREAK_LOOP        ''
       135_0	COME_FROM         '133'
         135	JUMP_BACK         '3'

 339     138	RAISE_VARARGS_0   ''
       141_0	COME_FROM         '0'

 341     141	LOAD_GLOBAL       'win32'
         144	LOAD_ATTR         'SetNamedPipeHandleState'

 342     147	LOAD_FAST         'h'
         150	LOAD_GLOBAL       'win32'
         153	LOAD_ATTR         'PIPE_READMODE_MESSAGE'
         156	LOAD_CONST        ''
         159	LOAD_CONST        ''
         162	CALL_FUNCTION_4   ''
         165	POP_TOP           ''

 344     166	LOAD_GLOBAL       '_multiprocessing'
         169	LOAD_ATTR         'PipeConnection'
         172	LOAD_FAST         'h'
         175	CALL_FUNCTION_1   ''
         178	RETURN_VALUE      ''

Syntax error at or near 'RAISE_VARARGS_0' token at offset 138


MESSAGE_LENGTH = 20
CHALLENGE = '#CHALLENGE#'
WELCOME = '#WELCOME#'
FAILURE = '#FAILURE#'

def deliver_challenge(connection, authkey):
    import hmac
    assert isinstance(authkey, bytes)
    message = os.urandom(MESSAGE_LENGTH)
    connection.send_bytes(CHALLENGE + message)
    digest = hmac.new(authkey, message).digest()
    response = connection.recv_bytes(256)
    if response == digest:
        connection.send_bytes(WELCOME)
    else:
        connection.send_bytes(FAILURE)
        raise AuthenticationError('digest received was wrong')


def answer_challenge(connection, authkey):
    import hmac
    assert isinstance(authkey, bytes)
    message = connection.recv_bytes(256)
    assert message[:len(CHALLENGE)] == CHALLENGE, 'message = %r' % message
    message = message[len(CHALLENGE):]
    digest = hmac.new(authkey, message).digest()
    connection.send_bytes(digest)
    response = connection.recv_bytes(256)
    if response != WELCOME:
        raise AuthenticationError('digest sent was rejected')


class ConnectionWrapper(object):

    def __init__(self, conn, dumps, loads):
        self._conn = conn
        self._dumps = dumps
        self._loads = loads
        for attr in ('fileno', 'close', 'poll', 'recv_bytes', 'send_bytes'):
            obj = getattr(conn, attr)
            setattr(self, attr, obj)

    def send(self, obj):
        s = self._dumps(obj)
        self._conn.send_bytes(s)

    def recv(self):
        s = self._conn.recv_bytes()
        return self._loads(s)


def _xml_dumps(obj):
    return xmlrpclib.dumps((obj,), None, None, None, 1).encode('utf8')


def _xml_loads(s):
    (obj), method = xmlrpclib.loads(s.decode('utf8'))
    return obj


class XmlListener(Listener):

    def accept(self):
        global xmlrpclib
        import xmlrpclib
        obj = Listener.accept(self)
        return ConnectionWrapper(obj, _xml_dumps, _xml_loads)


def XmlClient(*args, **kwds):
    global xmlrpclib
    import xmlrpclib
    return ConnectionWrapper(Client(*args, **kwds), _xml_dumps, _xml_loads)