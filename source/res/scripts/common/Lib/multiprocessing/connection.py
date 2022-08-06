# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/multiprocessing/connection.py
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
CONNECTION_TIMEOUT = 20.0
_mmap_counter = itertools.count()
default_family = 'AF_INET'
families = ['AF_INET']
if hasattr(socket, 'AF_UNIX'):
    default_family = 'AF_UNIX'
    families += ['AF_UNIX']
if sys.platform == 'win32':
    default_family = 'AF_PIPE'
    families += ['AF_PIPE']

def _init_timeout(timeout=CONNECTION_TIMEOUT):
    return time.time() + timeout


def _check_timeout(t):
    return time.time() > t


def arbitrary_address(family):
    if family == 'AF_INET':
        return ('localhost', 0)
    if family == 'AF_UNIX':
        return tempfile.mktemp(prefix='listener-', dir=get_temp_dir())
    if family == 'AF_PIPE':
        return tempfile.mktemp(prefix='\\\\.\\pipe\\pyc-%d-%d-' % (os.getpid(), _mmap_counter.next()), dir='')
    raise ValueError('unrecognized family')


def address_type(address):
    if type(address) == tuple:
        return 'AF_INET'
    if type(address) is str and address.startswith('\\\\'):
        return 'AF_PIPE'
    if type(address) is str:
        return 'AF_UNIX'
    raise ValueError('address type of %r unrecognized' % address)


class Listener(object):

    def __init__(self, address=None, family=None, backlog=1, authkey=None):
        family = family or address and address_type(address) or default_family
        address = address or arbitrary_address(family)
        if family == 'AF_PIPE':
            self._listener = PipeListener(address, backlog)
        else:
            self._listener = SocketListener(address, family, backlog)
        if authkey is not None and not isinstance(authkey, bytes):
            raise TypeError, 'authkey should be a byte string'
        self._authkey = authkey
        return

    def accept(self):
        c = self._listener.accept()
        if self._authkey:
            deliver_challenge(c, self._authkey)
            answer_challenge(c, self._authkey)
        return c

    def close(self):
        return self._listener.close()

    address = property(lambda self: self._listener._address)
    last_accepted = property(lambda self: self._listener._last_accepted)


def Client(address, family=None, authkey=None):
    family = family or address_type(address)
    if family == 'AF_PIPE':
        c = PipeClient(address)
    else:
        c = SocketClient(address)
    if authkey is not None and not isinstance(authkey, bytes):
        raise TypeError, 'authkey should be a byte string'
    if authkey is not None:
        answer_challenge(c, authkey)
        deliver_challenge(c, authkey)
    return c


if sys.platform != 'win32':

    def Pipe(duplex=True):
        if duplex:
            s1, s2 = socket.socketpair()
            s1.setblocking(True)
            s2.setblocking(True)
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
    from _multiprocessing import win32

    def Pipe(duplex=True):
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

    def __init__(self, address, family, backlog=1):
        self._socket = socket.socket(getattr(socket, family))
        try:
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.setblocking(True)
            self._socket.bind(address)
            self._socket.listen(backlog)
            self._address = self._socket.getsockname()
        except socket.error:
            self._socket.close()
            raise

        self._family = family
        self._last_accepted = None
        if family == 'AF_UNIX':
            self._unlink = Finalize(self, os.unlink, args=(address,), exitpriority=0)
        else:
            self._unlink = None
        return

    def accept(self):
        while True:
            try:
                s, self._last_accepted = self._socket.accept()
            except socket.error as e:
                if e.args[0] != errno.EINTR:
                    raise
            else:
                break

        s.setblocking(True)
        fd = duplicate(s.fileno())
        conn = _multiprocessing.Connection(fd)
        s.close()
        return conn

    def close(self):
        try:
            self._socket.close()
        finally:
            unlink = self._unlink
            if unlink is not None:
                self._unlink = None
                unlink()

        return


def SocketClient(address):
    family = getattr(socket, address_type(address))
    t = _init_timeout()
    while 1:
        s = socket.socket(family)
        s.setblocking(True)
        try:
            s.connect(address)
        except socket.error as e:
            s.close()
            if e.args[0] != errno.ECONNREFUSED or _check_timeout(t):
                debug('failed to connect to address %s', address)
                raise
            time.sleep(0.01)
        else:
            break

    else:
        raise

    fd = duplicate(s.fileno())
    conn = _multiprocessing.Connection(fd)
    s.close()
    return conn


if sys.platform == 'win32':

    class PipeListener(object):

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
                if e.args[0] not in (win32.ERROR_PIPE_CONNECTED, win32.ERROR_NO_DATA):
                    raise

            return _multiprocessing.PipeConnection(handle)

        @staticmethod
        def _finalize_pipe_listener(queue, address):
            sub_debug('closing listener with address=%r', address)
            for handle in queue:
                close(handle)


    def PipeClient(address):
        t = _init_timeout()
        while 1:
            try:
                win32.WaitNamedPipe(address, 1000)
                h = win32.CreateFile(address, win32.GENERIC_READ | win32.GENERIC_WRITE, 0, win32.NULL, win32.OPEN_EXISTING, 0, win32.NULL)
            except WindowsError as e:
                if e.args[0] not in (win32.ERROR_SEM_TIMEOUT, win32.ERROR_PIPE_BUSY) or _check_timeout(t):
                    raise
            else:
                break

        else:
            raise

        win32.SetNamedPipeHandleState(h, win32.PIPE_READMODE_MESSAGE, None, None)
        return _multiprocessing.PipeConnection(h)


MESSAGE_LENGTH = 20
CHALLENGE = '#CHALLENGE#'
WELCOME = '#WELCOME#'
FAILURE = '#FAILURE#'

def deliver_challenge(connection, authkey):
    import hmac
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
    message = connection.recv_bytes(256)
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
    return xmlrpclib.dumps((obj,), None, None, None, 1)


def _xml_loads(s):
    (obj), method = xmlrpclib.loads(s)
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
