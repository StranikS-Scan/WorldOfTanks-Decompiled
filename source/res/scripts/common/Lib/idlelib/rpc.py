# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/rpc.py
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
    return co


def pickle_code(co):
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
        pass

    def server_activate(self):
        self.socket.connect(self.server_address)

    def get_request(self):
        return (self.socket, self.server_address)

    def handle_error(self, request, client_address):
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
        os._exit(0)

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

        if oid not in self.objtable:
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
        raise EOFError

    def mainloop(self):
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
        return map(self._proxify, obj) if isinstance(obj, types.ListType) else obj

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
            while myseq not in self.responses:
                cvar.wait()

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

    def putmessage(self, message):
        self.debug('putmessage:%d:' % message[0])
        try:
            s = pickle.dumps(message)
        except pickle.PicklingError:
            print >> sys.__stderr__, 'Cannot pickle:', repr(message)
            raise

        s = struct.pack('<i', len(s)) + s
        while len(s) > 0:
            try:
                r, w, x = select.select([], [self.sock], [])
                n = self.sock.send(s[:BUFSIZE])
            except (AttributeError, TypeError):
                raise IOError, 'socket no longer exists'

            s = s[n:]

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
                if how == 'QUEUE':
                    pass
                continue
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
        self.mainloop()

    def get_remote_proxy(self, oid):
        return RPCProxy(self, oid)


class RPCClient(SocketIO):
    debugging = False
    location = '#C'
    nextseq = 1

    def __init__(self, address, family=socket.AF_INET, type=socket.SOCK_STREAM):
        self.listening_sock = socket.socket(family, type)
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
            if name in self.__attributes:
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
        if hasattr(attr, '__call__'):
            methods[name] = 1

    if type(obj) == types.InstanceType:
        _getmethods(obj.__class__, methods)
    if type(obj) == types.ClassType:
        for super in obj.__bases__:
            _getmethods(super, methods)


def _getattributes(obj, attributes):
    for name in dir(obj):
        attr = getattr(obj, name)
        if not hasattr(attr, '__call__'):
            attributes[name] = 1


class MethodProxy(object):

    def __init__(self, sockio, oid, name):
        self.sockio = sockio
        self.oid = oid
        self.name = name

    def __call__(self, *args, **kwargs):
        value = self.sockio.remotecall(self.oid, self.name, args, kwargs)
        return value
