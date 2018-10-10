# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/multiprocessing/managers.py
__all__ = ['BaseManager',
 'SyncManager',
 'BaseProxy',
 'Token']
import os
import sys
import weakref
import threading
import array
import Queue
from traceback import format_exc
from multiprocessing import Process, current_process, active_children, Pool, util, connection
from multiprocessing.process import AuthenticationString
from multiprocessing.forking import exit, Popen, assert_spawning, ForkingPickler
from multiprocessing.util import Finalize, info
try:
    from cPickle import PicklingError
except ImportError:
    from pickle import PicklingError

def reduce_array(a):
    return (array.array, (a.typecode, a.tostring()))


ForkingPickler.register(array.array, reduce_array)
view_types = [ type(getattr({}, name)()) for name in ('items', 'keys', 'values') ]

class Token(object):
    __slots__ = ('typeid', 'address', 'id')

    def __init__(self, typeid, address, id):
        self.typeid, self.address, self.id = typeid, address, id

    def __getstate__(self):
        return (self.typeid, self.address, self.id)

    def __setstate__(self, state):
        self.typeid, self.address, self.id = state

    def __repr__(self):
        return 'Token(typeid=%r, address=%r, id=%r)' % (self.typeid, self.address, self.id)


def dispatch(c, id, methodname, args=(), kwds={}):
    c.send((id,
     methodname,
     args,
     kwds))
    kind, result = c.recv()
    if kind == '#RETURN':
        return result
    raise convert_to_error(kind, result)


def convert_to_error(kind, result):
    if kind == '#ERROR':
        return result
    elif kind == '#TRACEBACK':
        return RemoteError(result)
    elif kind == '#UNSERIALIZABLE':
        return RemoteError('Unserializable message: %s\n' % result)
    else:
        return ValueError('Unrecognized message type')


class RemoteError(Exception):

    def __str__(self):
        return '\n' + '-' * 75 + '\n' + str(self.args[0]) + '-' * 75


def all_methods(obj):
    temp = []
    for name in dir(obj):
        func = getattr(obj, name)
        if hasattr(func, '__call__'):
            temp.append(name)

    return temp


def public_methods(obj):
    return [ name for name in all_methods(obj) if name[0] != '_' ]


class Server(object):
    public = ['shutdown',
     'create',
     'accept_connection',
     'get_methods',
     'debug_info',
     'number_of_objects',
     'dummy',
     'incref',
     'decref']

    def __init__(self, registry, address, authkey, serializer):
        self.registry = registry
        self.authkey = AuthenticationString(authkey)
        Listener, Client = listener_client[serializer]
        self.listener = Listener(address=address, backlog=16)
        self.address = self.listener.address
        self.id_to_obj = {'0': (None, ())}
        self.id_to_refcount = {}
        self.mutex = threading.RLock()
        self.stop = 0
        return

    def serve_forever(self):
        current_process()._manager_server = self
        try:
            try:
                while 1:
                    try:
                        c = self.listener.accept()
                    except (OSError, IOError):
                        continue

                    t = threading.Thread(target=self.handle_request, args=(c,))
                    t.daemon = True
                    t.start()

            except (KeyboardInterrupt, SystemExit):
                pass

        finally:
            self.stop = 999
            self.listener.close()

    def handle_request(self, c):
        funcname = result = request = None
        try:
            connection.deliver_challenge(c, self.authkey)
            connection.answer_challenge(c, self.authkey)
            request = c.recv()
            ignore, funcname, args, kwds = request
            func = getattr(self, funcname)
        except Exception:
            msg = ('#TRACEBACK', format_exc())
        else:
            try:
                result = func(c, *args, **kwds)
            except Exception:
                msg = ('#TRACEBACK', format_exc())
            else:
                msg = ('#RETURN', result)

        try:
            c.send(msg)
        except Exception as e:
            try:
                c.send(('#TRACEBACK', format_exc()))
            except Exception:
                pass

            util.info('Failure to send message: %r', msg)
            util.info(' ... request was %r', request)
            util.info(' ... exception was %r', e)

        c.close()
        return

    def serve_client(self, conn):
        util.debug('starting server thread to service %r', threading.current_thread().name)
        recv = conn.recv
        send = conn.send
        id_to_obj = self.id_to_obj
        while not self.stop:
            try:
                methodname = obj = None
                request = recv()
                ident, methodname, args, kwds = request
                obj, exposed, gettypeid = id_to_obj[ident]
                if methodname not in exposed:
                    raise AttributeError('method %r of %r object is not in exposed=%r' % (methodname, type(obj), exposed))
                function = getattr(obj, methodname)
                try:
                    res = function(*args, **kwds)
                except Exception as e:
                    msg = ('#ERROR', e)
                else:
                    typeid = gettypeid and gettypeid.get(methodname, None)
                    if typeid:
                        rident, rexposed = self.create(conn, typeid, res)
                        token = Token(typeid, self.address, rident)
                        msg = ('#PROXY', (rexposed, token))
                    else:
                        msg = ('#RETURN', res)

            except AttributeError:
                if methodname is None:
                    msg = ('#TRACEBACK', format_exc())
                else:
                    try:
                        fallback_func = self.fallback_mapping[methodname]
                        result = fallback_func(self, conn, ident, obj, *args, **kwds)
                        msg = ('#RETURN', result)
                    except Exception:
                        msg = ('#TRACEBACK', format_exc())

            except EOFError:
                util.debug('got EOF -- exiting thread serving %r', threading.current_thread().name)
                sys.exit(0)
            except Exception:
                msg = ('#TRACEBACK', format_exc())

            try:
                try:
                    send(msg)
                except Exception as e:
                    send(('#UNSERIALIZABLE', repr(msg)))

            except Exception as e:
                util.info('exception in thread serving %r', threading.current_thread().name)
                util.info(' ... message was %r', msg)
                util.info(' ... exception was %r', e)
                conn.close()
                sys.exit(1)

        return

    def fallback_getvalue(self, conn, ident, obj):
        return obj

    def fallback_str(self, conn, ident, obj):
        return str(obj)

    def fallback_repr(self, conn, ident, obj):
        return repr(obj)

    fallback_mapping = {'__str__': fallback_str,
     '__repr__': fallback_repr,
     '#GETVALUE': fallback_getvalue}

    def dummy(self, c):
        pass

    def debug_info(self, c):
        self.mutex.acquire()
        try:
            result = []
            keys = self.id_to_obj.keys()
            keys.sort()
            for ident in keys:
                if ident != '0':
                    result.append('  %s:       refcount=%s\n    %s' % (ident, self.id_to_refcount[ident], str(self.id_to_obj[ident][0])[:75]))

            return '\n'.join(result)
        finally:
            self.mutex.release()

    def number_of_objects(self, c):
        return len(self.id_to_obj) - 1

    def shutdown(self, c):
        try:
            try:
                util.debug('manager received shutdown message')
                c.send(('#RETURN', None))
                if sys.stdout != sys.__stdout__:
                    util.debug('resetting stdout, stderr')
                    sys.stdout = sys.__stdout__
                    sys.stderr = sys.__stderr__
                util._run_finalizers(0)
                for p in active_children():
                    util.debug('terminating a child process of manager')
                    p.terminate()

                for p in active_children():
                    util.debug('terminating a child process of manager')
                    p.join()

                util._run_finalizers()
                util.info('manager exiting with exitcode 0')
            except:
                import traceback
                traceback.print_exc()

        finally:
            exit(0)

        return

    def create(self, c, typeid, *args, **kwds):
        self.mutex.acquire()
        try:
            callable, exposed, method_to_typeid, proxytype = self.registry[typeid]
            if callable is None:
                obj = args[0]
            else:
                obj = callable(*args, **kwds)
            if exposed is None:
                exposed = public_methods(obj)
            if method_to_typeid is not None:
                exposed = list(exposed) + list(method_to_typeid)
            ident = '%x' % id(obj)
            util.debug('%r callable returned object with id %r', typeid, ident)
            self.id_to_obj[ident] = (obj, set(exposed), method_to_typeid)
            if ident not in self.id_to_refcount:
                self.id_to_refcount[ident] = 0
            self.incref(c, ident)
            return (ident, tuple(exposed))
        finally:
            self.mutex.release()

        return

    def get_methods(self, c, token):
        return tuple(self.id_to_obj[token.id][1])

    def accept_connection(self, c, name):
        threading.current_thread().name = name
        c.send(('#RETURN', None))
        self.serve_client(c)
        return None

    def incref(self, c, ident):
        self.mutex.acquire()
        try:
            self.id_to_refcount[ident] += 1
        finally:
            self.mutex.release()

    def decref(self, c, ident):
        self.mutex.acquire()
        try:
            self.id_to_refcount[ident] -= 1
            if self.id_to_refcount[ident] == 0:
                del self.id_to_obj[ident]
                del self.id_to_refcount[ident]
                util.debug('disposing of obj with id %r', ident)
        finally:
            self.mutex.release()


class State(object):
    __slots__ = ['value']
    INITIAL = 0
    STARTED = 1
    SHUTDOWN = 2


listener_client = {'pickle': (connection.Listener, connection.Client),
 'xmlrpclib': (connection.XmlListener, connection.XmlClient)}

class BaseManager(object):
    _registry = {}
    _Server = Server

    def __init__(self, address=None, authkey=None, serializer='pickle'):
        if authkey is None:
            authkey = current_process().authkey
        self._address = address
        self._authkey = AuthenticationString(authkey)
        self._state = State()
        self._state.value = State.INITIAL
        self._serializer = serializer
        self._Listener, self._Client = listener_client[serializer]
        return

    def __reduce__(self):
        return (type(self).from_address, (self._address, self._authkey, self._serializer))

    def get_server(self):
        return Server(self._registry, self._address, self._authkey, self._serializer)

    def connect(self):
        Listener, Client = listener_client[self._serializer]
        conn = Client(self._address, authkey=self._authkey)
        dispatch(conn, None, 'dummy')
        self._state.value = State.STARTED
        return

    def start(self, initializer=None, initargs=()):
        if initializer is not None and not hasattr(initializer, '__call__'):
            raise TypeError('initializer must be a callable')
        reader, writer = connection.Pipe(duplex=False)
        self._process = Process(target=type(self)._run_server, args=(self._registry,
         self._address,
         self._authkey,
         self._serializer,
         writer,
         initializer,
         initargs))
        ident = ':'.join((str(i) for i in self._process._identity))
        self._process.name = type(self).__name__ + '-' + ident
        self._process.start()
        writer.close()
        self._address = reader.recv()
        reader.close()
        self._state.value = State.STARTED
        self.shutdown = util.Finalize(self, type(self)._finalize_manager, args=(self._process,
         self._address,
         self._authkey,
         self._state,
         self._Client), exitpriority=0)
        return

    @classmethod
    def _run_server(cls, registry, address, authkey, serializer, writer, initializer=None, initargs=()):
        if initializer is not None:
            initializer(*initargs)
        server = cls._Server(registry, address, authkey, serializer)
        writer.send(server.address)
        writer.close()
        util.info('manager serving at %r', server.address)
        server.serve_forever()
        return

    def _create(self, typeid, *args, **kwds):
        conn = self._Client(self._address, authkey=self._authkey)
        try:
            id, exposed = dispatch(conn, None, 'create', (typeid,) + args, kwds)
        finally:
            conn.close()

        return (Token(typeid, self._address, id), exposed)

    def join(self, timeout=None):
        self._process.join(timeout)

    def _debug_info(self):
        conn = self._Client(self._address, authkey=self._authkey)
        try:
            return dispatch(conn, None, 'debug_info')
        finally:
            conn.close()

        return

    def _number_of_objects(self):
        conn = self._Client(self._address, authkey=self._authkey)
        try:
            return dispatch(conn, None, 'number_of_objects')
        finally:
            conn.close()

        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    @staticmethod
    def _finalize_manager(process, address, authkey, state, _Client):
        if process.is_alive():
            util.info('sending shutdown message to manager')
            try:
                conn = _Client(address, authkey=authkey)
                try:
                    dispatch(conn, None, 'shutdown')
                finally:
                    conn.close()

            except Exception:
                pass

            process.join(timeout=0.2)
            if process.is_alive():
                util.info('manager still alive')
                if hasattr(process, 'terminate'):
                    util.info('trying to `terminate()` manager process')
                    process.terminate()
                    process.join(timeout=0.1)
                    if process.is_alive():
                        util.info('manager still alive after terminate')
        state.value = State.SHUTDOWN
        try:
            del BaseProxy._address_to_local[address]
        except KeyError:
            pass

        return

    address = property(lambda self: self._address)

    @classmethod
    def register(cls, typeid, callable=None, proxytype=None, exposed=None, method_to_typeid=None, create_method=True):
        if '_registry' not in cls.__dict__:
            cls._registry = cls._registry.copy()
        if proxytype is None:
            proxytype = AutoProxy
        exposed = exposed or getattr(proxytype, '_exposed_', None)
        method_to_typeid = method_to_typeid or getattr(proxytype, '_method_to_typeid_', None)
        if method_to_typeid:
            for key, value in method_to_typeid.items():
                pass

        cls._registry[typeid] = (callable,
         exposed,
         method_to_typeid,
         proxytype)
        if create_method:

            def temp(self, *args, **kwds):
                util.debug('requesting creation of a shared %r object', typeid)
                token, exp = self._create(typeid, *args, **kwds)
                proxy = proxytype(token, self._serializer, manager=self, authkey=self._authkey, exposed=exp)
                conn = self._Client(token.address, authkey=self._authkey)
                dispatch(conn, None, 'decref', (token.id,))
                return proxy

            temp.__name__ = typeid
            setattr(cls, typeid, temp)
        return


class ProcessLocalSet(set):

    def __init__(self):
        util.register_after_fork(self, lambda obj: obj.clear())

    def __reduce__(self):
        return (type(self), ())


class BaseProxy(object):
    _address_to_local = {}
    _mutex = util.ForkAwareThreadLock()

    def __init__(self, token, serializer, manager=None, authkey=None, exposed=None, incref=True):
        BaseProxy._mutex.acquire()
        try:
            tls_idset = BaseProxy._address_to_local.get(token.address, None)
            if tls_idset is None:
                tls_idset = (util.ForkAwareLocal(), ProcessLocalSet())
                BaseProxy._address_to_local[token.address] = tls_idset
        finally:
            BaseProxy._mutex.release()

        self._tls = tls_idset[0]
        self._idset = tls_idset[1]
        self._token = token
        self._id = self._token.id
        self._manager = manager
        self._serializer = serializer
        self._Client = listener_client[serializer][1]
        if authkey is not None:
            self._authkey = AuthenticationString(authkey)
        elif self._manager is not None:
            self._authkey = self._manager._authkey
        else:
            self._authkey = current_process().authkey
        if incref:
            self._incref()
        util.register_after_fork(self, BaseProxy._after_fork)
        return

    def _connect(self):
        util.debug('making connection to manager')
        name = current_process().name
        if threading.current_thread().name != 'MainThread':
            name += '|' + threading.current_thread().name
        conn = self._Client(self._token.address, authkey=self._authkey)
        dispatch(conn, None, 'accept_connection', (name,))
        self._tls.connection = conn
        return

    def _callmethod(self, methodname, args=(), kwds={}):
        try:
            conn = self._tls.connection
        except AttributeError:
            util.debug('thread %r does not own a connection', threading.current_thread().name)
            self._connect()
            conn = self._tls.connection

        conn.send((self._id,
         methodname,
         args,
         kwds))
        kind, result = conn.recv()
        if kind == '#RETURN':
            return result
        elif kind == '#PROXY':
            exposed, token = result
            proxytype = self._manager._registry[token.typeid][-1]
            token.address = self._token.address
            proxy = proxytype(token, self._serializer, manager=self._manager, authkey=self._authkey, exposed=exposed)
            conn = self._Client(token.address, authkey=self._authkey)
            dispatch(conn, None, 'decref', (token.id,))
            return proxy
        else:
            raise convert_to_error(kind, result)
            return

    def _getvalue(self):
        return self._callmethod('#GETVALUE')

    def _incref(self):
        conn = self._Client(self._token.address, authkey=self._authkey)
        dispatch(conn, None, 'incref', (self._id,))
        util.debug('INCREF %r', self._token.id)
        self._idset.add(self._id)
        state = self._manager and self._manager._state
        self._close = util.Finalize(self, BaseProxy._decref, args=(self._token,
         self._authkey,
         state,
         self._tls,
         self._idset,
         self._Client), exitpriority=10)
        return

    @staticmethod
    def _decref(token, authkey, state, tls, idset, _Client):
        idset.discard(token.id)
        if state is None or state.value == State.STARTED:
            try:
                util.debug('DECREF %r', token.id)
                conn = _Client(token.address, authkey=authkey)
                dispatch(conn, None, 'decref', (token.id,))
            except Exception as e:
                util.debug('... decref failed %s', e)

        else:
            util.debug('DECREF %r -- manager already shutdown', token.id)
        if not idset and hasattr(tls, 'connection'):
            util.debug('thread %r has no more proxies so closing conn', threading.current_thread().name)
            tls.connection.close()
            del tls.connection
        return

    def _after_fork(self):
        self._manager = None
        try:
            self._incref()
        except Exception as e:
            util.info('incref failed: %s' % e)

        return

    def __reduce__(self):
        kwds = {}
        if Popen.thread_is_spawning():
            kwds['authkey'] = self._authkey
        if getattr(self, '_isauto', False):
            kwds['exposed'] = self._exposed_
            return (RebuildProxy, (AutoProxy,
              self._token,
              self._serializer,
              kwds))
        else:
            return (RebuildProxy, (type(self),
              self._token,
              self._serializer,
              kwds))

    def __deepcopy__(self, memo):
        return self._getvalue()

    def __repr__(self):
        return '<%s object, typeid %r at %s>' % (type(self).__name__, self._token.typeid, '0x%x' % id(self))

    def __str__(self):
        try:
            return self._callmethod('__repr__')
        except Exception:
            return repr(self)[:-1] + "; '__str__()' failed>"


def RebuildProxy(func, token, serializer, kwds):
    server = getattr(current_process(), '_manager_server', None)
    if server and server.address == token.address:
        return server.id_to_obj[token.id][0]
    else:
        incref = kwds.pop('incref', True) and not getattr(current_process(), '_inheriting', False)
        return func(token, serializer, incref=incref, **kwds)
        return


def MakeProxyType(name, exposed, _cache={}):
    exposed = tuple(exposed)
    try:
        return _cache[name, exposed]
    except KeyError:
        pass

    dic = {}
    for meth in exposed:
        exec 'def %s(self, *args, **kwds):\n        return self._callmethod(%r, args, kwds)' % (meth, meth) in dic

    ProxyType = type(name, (BaseProxy,), dic)
    ProxyType._exposed_ = exposed
    _cache[name, exposed] = ProxyType
    return ProxyType


def AutoProxy(token, serializer, manager=None, authkey=None, exposed=None, incref=True):
    _Client = listener_client[serializer][1]
    if exposed is None:
        conn = _Client(token.address, authkey=authkey)
        try:
            exposed = dispatch(conn, None, 'get_methods', (token,))
        finally:
            conn.close()

    if authkey is None and manager is not None:
        authkey = manager._authkey
    if authkey is None:
        authkey = current_process().authkey
    ProxyType = MakeProxyType('AutoProxy[%s]' % token.typeid, exposed)
    proxy = ProxyType(token, serializer, manager=manager, authkey=authkey, incref=incref)
    proxy._isauto = True
    return proxy


class Namespace(object):

    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __repr__(self):
        items = self.__dict__.items()
        temp = []
        for name, value in items:
            if not name.startswith('_'):
                temp.append('%s=%r' % (name, value))

        temp.sort()
        return 'Namespace(%s)' % str.join(', ', temp)


class Value(object):

    def __init__(self, typecode, value, lock=True):
        self._typecode = typecode
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value

    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self._typecode, self._value)

    value = property(get, set)


def Array(typecode, sequence, lock=True):
    return array.array(typecode, sequence)


class IteratorProxy(BaseProxy):
    _exposed_ = ('__next__', 'next', 'send', 'throw', 'close')

    def __iter__(self):
        return self

    def __next__(self, *args):
        return self._callmethod('__next__', args)

    def next(self, *args):
        return self._callmethod('next', args)

    def send(self, *args):
        return self._callmethod('send', args)

    def throw(self, *args):
        return self._callmethod('throw', args)

    def close(self, *args):
        return self._callmethod('close', args)


class AcquirerProxy(BaseProxy):
    _exposed_ = ('acquire', 'release')

    def acquire(self, blocking=True):
        return self._callmethod('acquire', (blocking,))

    def release(self):
        return self._callmethod('release')

    def __enter__(self):
        return self._callmethod('acquire')

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._callmethod('release')


class ConditionProxy(AcquirerProxy):
    _exposed_ = ('acquire', 'release', 'wait', 'notify', 'notify_all')

    def wait(self, timeout=None):
        return self._callmethod('wait', (timeout,))

    def notify(self):
        return self._callmethod('notify')

    def notify_all(self):
        return self._callmethod('notify_all')


class EventProxy(BaseProxy):
    _exposed_ = ('is_set', 'set', 'clear', 'wait')

    def is_set(self):
        return self._callmethod('is_set')

    def set(self):
        return self._callmethod('set')

    def clear(self):
        return self._callmethod('clear')

    def wait(self, timeout=None):
        return self._callmethod('wait', (timeout,))


class NamespaceProxy(BaseProxy):
    _exposed_ = ('__getattribute__', '__setattr__', '__delattr__')

    def __getattr__(self, key):
        if key[0] == '_':
            return object.__getattribute__(self, key)
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('__getattribute__', (key,))

    def __setattr__(self, key, value):
        if key[0] == '_':
            return object.__setattr__(self, key, value)
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('__setattr__', (key, value))

    def __delattr__(self, key):
        if key[0] == '_':
            return object.__delattr__(self, key)
        callmethod = object.__getattribute__(self, '_callmethod')
        return callmethod('__delattr__', (key,))


class ValueProxy(BaseProxy):
    _exposed_ = ('get', 'set')

    def get(self):
        return self._callmethod('get')

    def set(self, value):
        return self._callmethod('set', (value,))

    value = property(get, set)


BaseListProxy = MakeProxyType('BaseListProxy', ('__add__',
 '__contains__',
 '__delitem__',
 '__delslice__',
 '__getitem__',
 '__getslice__',
 '__len__',
 '__mul__',
 '__reversed__',
 '__rmul__',
 '__setitem__',
 '__setslice__',
 'append',
 'count',
 'extend',
 'index',
 'insert',
 'pop',
 'remove',
 'reverse',
 'sort',
 '__imul__'))

class ListProxy(BaseListProxy):

    def __iadd__(self, value):
        self._callmethod('extend', (value,))
        return self

    def __imul__(self, value):
        self._callmethod('__imul__', (value,))
        return self


DictProxy = MakeProxyType('DictProxy', ('__contains__',
 '__delitem__',
 '__getitem__',
 '__len__',
 '__setitem__',
 'clear',
 'copy',
 'get',
 'has_key',
 'items',
 'keys',
 'pop',
 'popitem',
 'setdefault',
 'update',
 'values'))
ArrayProxy = MakeProxyType('ArrayProxy', ('__len__',
 '__getitem__',
 '__setitem__',
 '__getslice__',
 '__setslice__'))
PoolProxy = MakeProxyType('PoolProxy', ('apply',
 'apply_async',
 'close',
 'imap',
 'imap_unordered',
 'join',
 'map',
 'map_async',
 'terminate'))
PoolProxy._method_to_typeid_ = {'apply_async': 'AsyncResult',
 'map_async': 'AsyncResult',
 'imap': 'Iterator',
 'imap_unordered': 'Iterator'}

class SyncManager(BaseManager):
    pass


SyncManager.register('Queue', Queue.Queue)
SyncManager.register('JoinableQueue', Queue.Queue)
SyncManager.register('Event', threading.Event, EventProxy)
SyncManager.register('Lock', threading.Lock, AcquirerProxy)
SyncManager.register('RLock', threading.RLock, AcquirerProxy)
SyncManager.register('Semaphore', threading.Semaphore, AcquirerProxy)
SyncManager.register('BoundedSemaphore', threading.BoundedSemaphore, AcquirerProxy)
SyncManager.register('Condition', threading.Condition, ConditionProxy)
SyncManager.register('Pool', Pool, PoolProxy)
SyncManager.register('list', list, ListProxy)
SyncManager.register('dict', dict, DictProxy)
SyncManager.register('Value', Value, ValueProxy)
SyncManager.register('Array', Array, ArrayProxy)
SyncManager.register('Namespace', Namespace, NamespaceProxy)
SyncManager.register('Iterator', proxytype=IteratorProxy, create_method=False)
SyncManager.register('AsyncResult', create_method=False)
