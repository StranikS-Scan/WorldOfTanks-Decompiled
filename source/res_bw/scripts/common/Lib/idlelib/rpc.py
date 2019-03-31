# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/rpc.py
# Compiled at: 2010-05-25 20:46:16
"""RPC Implemention, originally written for the Python Idle IDE

For security reasons, GvR requested that Idle's Python execution server process
connect to the Idle process, which listens for the connection.  Since Idle has
has only one client per server, this was not a limitation.

   +---------------------------------+ +-------------+
   | SocketServer.BaseRequestHandler | | SocketIO    |
   +---------------------------------+ +-------------+
                   ^                   | register()  |
                   |                   | unregister()|
                   |                   +-------------+
                   |                      ^  ^
                   |                      |  |
                   | + -------------------+  |
                   | |                       |
   +-------------------------+        +-----------------+
   | RPCHandler              |        | RPCClient       |
   | [attribute of RPCServer]|        |                 |
   +-------------------------+        +-----------------+

The RPCServer handler class is expected to provide register/unregister methods.
RPCHandler inherits the mix-in class SocketIO, which provides these methods.

See the Idle run.main() docstring for further information on how this was
accomplished in Idle.

"""
import sys
import os
import socket
import select
import SocketServer
import struct
import cPickle as pickle
import threading
import Queue
import traceback
import copy_reg
import types
import marshal

def unpickle_code(ms):
    co = marshal.loads(ms)
    assert isinstance(co, types.CodeType)
    return co


def pickle_code(co):
    assert isinstance(co, types.CodeType)
    ms = marshal.dumps(co)
    return (unpickle_code, (ms,))


copy_reg.pickle(types.CodeType, pickle_code, unpickle_code)
BUFSIZE = 8 * 1024
LOCALHOST = '127.0.0.1'

class RPCServer(SocketServer.TCPServer):

    def __init__(self, addr, handlerclass=None):
        if handlerclass is None:
            handlerclass = RPCHandler
        SocketServer.TCPServer.__init__(self, addr, handlerclass)
        return

    def server_bind(self):
        """Override TCPServer method, no bind() phase for connecting entity"""
        pass

    def server_activate(self):
        """Override TCPServer method, connect() instead of listen()
        
        Due to the reversed connection, self.server_address is actually the
        address of the Idle Client to which we are connecting.
        
        """
        self.socket.connect(self.server_address)

    def get_request(self):
        """Override TCPServer method, return already connected socket"""
        return (self.socket, self.server_address)

    def handle_error(self, request, client_address):
        """Override TCPServer method
        
        Error message goes to __stderr__.  No error message if exiting
        normally or socket raised EOF.  Other exceptions not handled in
        server code will cause os._exit.
        
        """
        try:
            raise
        except SystemExit:
            raise
        except:
            erf = sys.__stderr__
            print >> erf, '\n' + '-' * 40
            print >> erf, 'Unhandled server exception!'
            print >> erf, 'Thread: %s' % threading.currentThread().getName()
            print >> erf, 'Client Address: ', client_address
            print >> erf, 'Request: ', repr(request)
            traceback.print_exc(file=erf)
            print >> erf, '\n*** Unrecoverable, server exiting!'
            print >> erf, '-' * 40
            os._exit(0)


objecttable = {}
request_queue = Queue.Queue(0)
response_queue = Queue.Queue(0)

class SocketIO(object):
    nextseq = 0

    def __init__(self, sock, objtable=None, debugging=None):
        self.sockthread = threading.currentThread()
        if debugging is not None:
            self.debugging = debugging
        self.sock = sock
        if objtable is None:
            objtable = objecttable
        self.objtable = objtable
        self.responses = {}
        self.cvars = {}
        return

    def close(self):
        sock = self.sock
        self.sock = None
        if sock is not None:
            sock.close()
        return

    def exithook(self):
        """override for specific exit action"""
        os._exit()

    def debug(self, *args):
        if not self.debugging:
            return
        s = self.location + ' ' + str(threading.currentThread().getName())
        for a in args:
            s = s + ' ' + str(a)

        print >> sys.__stderr__, s

    def register(self, oid, object):
        self.objtable[oid] = object

    def unregister(self, oid):
        try:
            del self.objtable[oid]
        except KeyError:
            pass

    def localcall(self, seq, request):
        self.debug('localcall:', request)
        try:
            how, (oid, methodname, args, kwargs) = request
        except TypeError:
            return ('ERROR', 'Bad request format')

        if not self.objtable.has_key(oid):
            return ('ERROR', 'Unknown object id: %r' % (oid,))
        else:
            obj = self.objtable[oid]
            if methodname == '__methods__':
                methods = {}
                _getmethods(obj, methods)
                return ('OK', methods)
            if methodname == '__attributes__':
                attributes = {}
                _getattributes(obj, attributes)
                return ('OK', attributes)
            if not hasattr(obj, methodname):
                return ('ERROR', 'Unsupported method name: %r' % (methodname,))
            method = getattr(obj, methodname)
            try:
                if how == 'CALL':
                    ret = method(*args, **kwargs)
                    if isinstance(ret, RemoteObject):
                        ret = remoteref(ret)
                    return ('OK', ret)
                if how == 'QUEUE':
                    request_queue.put((seq, (method, args, kwargs)))
                    return ('QUEUED', None)
                return ('ERROR', 'Unsupported message type: %s' % how)
            except SystemExit:
                raise
            except socket.error:
                raise
            except:
                msg = '*** Internal Error: rpc.py:SocketIO.localcall()\n\n Object: %s \n Method: %s \n Args: %s\n'
                print >> sys.__stderr__, msg % (oid, method, args)
                traceback.print_exc(file=sys.__stderr__)
                return ('EXCEPTION', None)

            return None

    def remotecall(self, oid, methodname, args, kwargs):
        self.debug('remotecall:asynccall: ', oid, methodname)
        seq = self.asynccall(oid, methodname, args, kwargs)
        return self.asyncreturn(seq)

    def remotequeue(self, oid, methodname, args, kwargs):
        self.debug('remotequeue:asyncqueue: ', oid, methodname)
        seq = self.asyncqueue(oid, methodname, args, kwargs)
        return self.asyncreturn(seq)

    def asynccall(self, oid, methodname, args, kwargs):
        request = ('CALL', (oid,
          methodname,
          args,
          kwargs))
        seq = self.newseq()
        if threading.currentThread() != self.sockthread:
            cvar = threading.Condition()
            self.cvars[seq] = cvar
        self.debug('asynccall:%d:' % seq, oid, methodname, args, kwargs)
        self.putmessage((seq, request))
        return seq

    def asyncqueue(self, oid, methodname, args, kwargs):
        request = ('QUEUE', (oid,
          methodname,
          args,
          kwargs))
        seq = self.newseq()
        if threading.currentThread() != self.sockthread:
            cvar = threading.Condition()
            self.cvars[seq] = cvar
        self.debug('asyncqueue:%d:' % seq, oid, methodname, args, kwargs)
        self.putmessage((seq, request))
        return seq

    def asyncreturn(self, seq):
        self.debug('asyncreturn:%d:call getresponse(): ' % seq)
        response = self.getresponse(seq, wait=0.05)
        self.debug('asyncreturn:%d:response: ' % seq, response)
        return self.decoderesponse(response)

    def decoderesponse(self, response):
        how, what = response
        if how == 'OK':
            return what
        elif how == 'QUEUED':
            return None
        elif how == 'EXCEPTION':
            self.debug('decoderesponse: EXCEPTION')
            return None
        elif how == 'EOF':
            self.debug('decoderesponse: EOF')
            self.decode_interrupthook()
            return None
        else:
            if how == 'ERROR':
                self.debug('decoderesponse: Internal ERROR:', what)
                raise RuntimeError, what
            raise SystemError, (how, what)
            return None

    def decode_interrupthook(self):
        """"""
        raise EOFError

    def mainloop(self):
        """Listen on socket until I/O not ready or EOF
        
        pollresponse() will loop looking for seq number None, which
        never comes, and exit on EOFError.
        
        """
        try:
            self.getresponse(myseq=None, wait=0.05)
        except EOFError:
            self.debug('mainloop:return')
            return

        return

    def getresponse(self, myseq, wait):
        response = self._getresponse(myseq, wait)
        if response is not None:
            how, what = response
            if how == 'OK':
                response = (how, self._proxify(what))
        return response

    def _proxify(self, obj):
        if isinstance(obj, RemoteProxy):
            return RPCProxy(self, obj.oid)
        if isinstance(obj, types.ListType):
            return map(self._proxify, obj)
        return obj

    def _getresponse(self, myseq, wait):
        self.debug('_getresponse:myseq:', myseq)
        if threading.currentThread() is self.sockthread:
            while 1:
                response = self.pollresponse(myseq, wait)
                if response is not None:
                    return response

        else:
            cvar = self.cvars[myseq]
            cvar.acquire()
            while 1:
                self.responses.has_key(myseq) or cvar.wait()

            response = self.responses[myseq]
            self.debug('_getresponse:%s: thread woke up: response: %s' % (myseq, response))
            del self.responses[myseq]
            del self.cvars[myseq]
            cvar.release()
            return response
        return

    def newseq(self):
        self.nextseq = seq = self.nextseq + 2
        return seq

    def putmessage--- This code section failed: ---

 322       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'debug'
           6	LOAD_CONST        'putmessage:%d:'
           9	LOAD_FAST         'message'
          12	LOAD_CONST        0
          15	BINARY_SUBSCR     ''
          16	BINARY_MODULO     ''
          17	CALL_FUNCTION_1   ''
          20	POP_TOP           ''

 323      21	SETUP_EXCEPT      '43'

 324      24	LOAD_GLOBAL       'pickle'
          27	LOAD_ATTR         'dumps'
          30	LOAD_FAST         'message'
          33	CALL_FUNCTION_1   ''
          36	STORE_FAST        's'
          39	POP_BLOCK         ''
          40	JUMP_FORWARD      '91'
        43_0	COME_FROM         '21'

 325      43	DUP_TOP           ''
          44	LOAD_GLOBAL       'pickle'
          47	LOAD_ATTR         'PicklingError'
          50	COMPARE_OP        'exception match'
          53	JUMP_IF_FALSE     '90'
          56	POP_TOP           ''
          57	POP_TOP           ''
          58	POP_TOP           ''

 326      59	LOAD_GLOBAL       'sys'
          62	LOAD_ATTR         '__stderr__'
          65	DUP_TOP           ''
          66	LOAD_CONST        'Cannot pickle:'
          69	ROT_TWO           ''
          70	PRINT_ITEM_TO     ''
          71	DUP_TOP           ''
          72	LOAD_GLOBAL       'repr'
          75	LOAD_FAST         'message'
          78	CALL_FUNCTION_1   ''
          81	ROT_TWO           ''
          82	PRINT_ITEM_TO     ''
          83	PRINT_NEWLINE_TO  ''

 327      84	RAISE_VARARGS_0   ''
          87	JUMP_FORWARD      '91'
          90	END_FINALLY       ''
        91_0	COME_FROM         '40'
        91_1	COME_FROM         '90'

 328      91	LOAD_GLOBAL       'struct'
          94	LOAD_ATTR         'pack'
          97	LOAD_CONST        '<i'
         100	LOAD_GLOBAL       'len'
         103	LOAD_FAST         's'
         106	CALL_FUNCTION_1   ''
         109	CALL_FUNCTION_2   ''
         112	LOAD_FAST         's'
         115	BINARY_ADD        ''
         116	STORE_FAST        's'

 329     119	SETUP_LOOP        '273'
         122	LOAD_GLOBAL       'len'
         125	LOAD_FAST         's'
         128	CALL_FUNCTION_1   ''
         131	LOAD_CONST        0
         134	COMPARE_OP        '>'
         137	JUMP_IF_FALSE     '272'

 330     140	SETUP_EXCEPT      '205'

 331     143	LOAD_GLOBAL       'select'
         146	LOAD_ATTR         'select'
         149	BUILD_LIST_0      ''
         152	LOAD_FAST         'self'
         155	LOAD_ATTR         'sock'
         158	BUILD_LIST_1      ''
         161	BUILD_LIST_0      ''
         164	CALL_FUNCTION_3   ''
         167	UNPACK_SEQUENCE_3 ''
         170	STORE_FAST        'r'
         173	STORE_FAST        'w'
         176	STORE_FAST        'x'

 332     179	LOAD_FAST         'self'
         182	LOAD_ATTR         'sock'
         185	LOAD_ATTR         'send'
         188	LOAD_FAST         's'
         191	LOAD_GLOBAL       'BUFSIZE'
         194	SLICE+2           ''
         195	CALL_FUNCTION_1   ''
         198	STORE_FAST        'n'
         201	POP_BLOCK         ''
         202	JUMP_FORWARD      '259'
       205_0	COME_FROM         '140'

 333     205	DUP_TOP           ''
         206	LOAD_GLOBAL       'AttributeError'
         209	LOAD_GLOBAL       'TypeError'
         212	BUILD_TUPLE_2     ''
         215	COMPARE_OP        'exception match'
         218	JUMP_IF_FALSE     '236'
         221	POP_TOP           ''
         222	POP_TOP           ''
         223	POP_TOP           ''

 334     224	LOAD_GLOBAL       'IOError'
         227	LOAD_CONST        'socket no longer exists'
         230	RAISE_VARARGS_2   ''
         233	JUMP_BACK         '122'

 335     236	DUP_TOP           ''
         237	LOAD_GLOBAL       'socket'
         240	LOAD_ATTR         'error'
         243	COMPARE_OP        'exception match'
         246	JUMP_IF_FALSE     '258'
         249	POP_TOP           ''
         250	POP_TOP           ''
         251	POP_TOP           ''

 336     252	RAISE_VARARGS_0   ''
         255	JUMP_BACK         '122'
         258	END_FINALLY       ''
       259_0	COME_FROM         '202'

 338     259	LOAD_FAST         's'
         262	LOAD_FAST         'n'
         265	SLICE+1           ''
         266	STORE_FAST        's'
       269_0	COME_FROM         '258'
         269	JUMP_BACK         '122'
         272	POP_BLOCK         ''
       273_0	COME_FROM         '119'

Syntax error at or near 'POP_BLOCK' token at offset 272

    buffer = ''
    bufneed = 4
    bufstate = 0

    def pollpacket(self, wait):
        self._stage0()
        if len(self.buffer) < self.bufneed:
            r, w, x = select.select([self.sock.fileno()], [], [], wait)
            if len(r) == 0:
                return None
            try:
                s = self.sock.recv(BUFSIZE)
            except socket.error:
                raise EOFError

            if len(s) == 0:
                raise EOFError
            self.buffer += s
            self._stage0()
        return self._stage1()

    def _stage0(self):
        if self.bufstate == 0 and len(self.buffer) >= 4:
            s = self.buffer[:4]
            self.buffer = self.buffer[4:]
            self.bufneed = struct.unpack('<i', s)[0]
            self.bufstate = 1

    def _stage1(self):
        if self.bufstate == 1 and len(self.buffer) >= self.bufneed:
            packet = self.buffer[:self.bufneed]
            self.buffer = self.buffer[self.bufneed:]
            self.bufneed = 4
            self.bufstate = 0
            return packet

    def pollmessage(self, wait):
        packet = self.pollpacket(wait)
        if packet is None:
            return
        else:
            try:
                message = pickle.loads(packet)
            except pickle.UnpicklingError:
                print >> sys.__stderr__, '-----------------------'
                print >> sys.__stderr__, 'cannot unpickle packet:', repr(packet)
                traceback.print_stack(file=sys.__stderr__)
                print >> sys.__stderr__, '-----------------------'
                raise

            return message

    def pollresponse(self, myseq, wait):
        """Handle messages received on the socket.
        
        Some messages received may be asynchronous 'call' or 'queue' requests,
        and some may be responses for other threads.
        
        'call' requests are passed to self.localcall() with the expectation of
        immediate execution, during which time the socket is not serviced.
        
        'queue' requests are used for tasks (which may block or hang) to be
        processed in a different thread.  These requests are fed into
        request_queue by self.localcall().  Responses to queued requests are
        taken from response_queue and sent across the link with the associated
        sequence numbers.  Messages in the queues are (sequence_number,
        request/response) tuples and code using this module removing messages
        from the request_queue is responsible for returning the correct
        sequence number in the response_queue.
        
        pollresponse() will loop until a response message with the myseq
        sequence number is received, and will save other responses in
        self.responses and notify the owning thread.
        
        """
        while 1:
            try:
                qmsg = response_queue.get(0)
            except Queue.Empty:
                pass
            else:
                seq, response = qmsg
                message = (seq, ('OK', response))
                self.putmessage(message)

            try:
                message = self.pollmessage(wait)
                if message is None:
                    return
            except EOFError:
                self.handle_EOF()
                return
            except AttributeError:
                return

            seq, resq = message
            how = resq[0]
            self.debug('pollresponse:%d:myseq:%s' % (seq, myseq))
            if how in ('CALL', 'QUEUE'):
                self.debug('pollresponse:%d:localcall:call:' % seq)
                response = self.localcall(seq, resq)
                self.debug('pollresponse:%d:localcall:response:%s' % (seq, response))
                if how == 'CALL':
                    self.putmessage((seq, response))
                elif how == 'QUEUE':
                    pass
                continue
            else:
                if seq == myseq:
                    return resq
                cv = self.cvars.get(seq, None)
                if cv is not None:
                    cv.acquire()
                    self.responses[seq] = resq
                    cv.notify()
                    cv.release()
                else:
                    continue

        return

    def handle_EOF(self):
        """action taken upon link being closed by peer"""
        self.EOFhook()
        self.debug('handle_EOF')
        for key in self.cvars:
            cv = self.cvars[key]
            cv.acquire()
            self.responses[key] = ('EOF', None)
            cv.notify()
            cv.release()

        self.exithook()
        return None

    def EOFhook(self):
        """Classes using rpc client/server can override to augment EOF action"""
        pass


class RemoteObject(object):
    pass


def remoteref(obj):
    oid = id(obj)
    objecttable[oid] = obj
    return RemoteProxy(oid)


class RemoteProxy(object):

    def __init__(self, oid):
        self.oid = oid


class RPCHandler(SocketServer.BaseRequestHandler, SocketIO):
    debugging = False
    location = '#S'

    def __init__(self, sock, addr, svr):
        svr.current_handler = self
        SocketIO.__init__(self, sock)
        SocketServer.BaseRequestHandler.__init__(self, sock, addr, svr)

    def handle(self):
        """handle() method required by SocketServer"""
        self.mainloop()

    def get_remote_proxy(self, oid):
        return RPCProxy(self, oid)


class RPCClient(SocketIO):
    debugging = False
    location = '#C'
    nextseq = 1

    def __init__(self, address, family=socket.AF_INET, type=socket.SOCK_STREAM):
        self.listening_sock = socket.socket(family, type)
        self.listening_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listening_sock.bind(address)
        self.listening_sock.listen(1)

    def accept(self):
        working_sock, address = self.listening_sock.accept()
        if self.debugging:
            print >> sys.__stderr__, '****** Connection request from ', address
        if address[0] == LOCALHOST:
            SocketIO.__init__(self, working_sock)
        else:
            print >> sys.__stderr__, '** Invalid host: ', address
            raise socket.error

    def get_remote_proxy(self, oid):
        return RPCProxy(self, oid)


class RPCProxy(object):
    __methods = None
    __attributes = None

    def __init__(self, sockio, oid):
        self.sockio = sockio
        self.oid = oid

    def __getattr__(self, name):
        if self.__methods is None:
            self.__getmethods()
        if self.__methods.get(name):
            return MethodProxy(self.sockio, self.oid, name)
        else:
            if self.__attributes is None:
                self.__getattributes()
            if self.__attributes.has_key(name):
                value = self.sockio.remotecall(self.oid, '__getattribute__', (name,), {})
                return value
            raise AttributeError, name
            return

    def __getattributes(self):
        self.__attributes = self.sockio.remotecall(self.oid, '__attributes__', (), {})

    def __getmethods(self):
        self.__methods = self.sockio.remotecall(self.oid, '__methods__', (), {})


def _getmethods(obj, methods):
    for name in dir(obj):
        attr = getattr(obj, name)
        if callable(attr):
            methods[name] = 1

    if type(obj) == types.InstanceType:
        _getmethods(obj.__class__, methods)
    if type(obj) == types.ClassType:
        for super in obj.__bases__:
            _getmethods(super, methods)


def _getattributes(obj, attributes):
    for name in dir(obj):
        attr = getattr(obj, name)
        if not callable(attr):
            attributes[name] = 1


class MethodProxy(object):

    def __init__(self, sockio, oid, name):
        self.sockio = sockio
        self.oid = oid
        self.name = name

    def __call__(self, *args, **kwargs):
        value = self.sockio.remotecall(self.oid, self.name, args, kwargs)
        return value