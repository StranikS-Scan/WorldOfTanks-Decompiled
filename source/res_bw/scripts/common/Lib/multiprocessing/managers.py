# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/multiprocessing/managers.py
# Compiled at: 2010-08-25 17:58:21
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
    """
    Type to uniquely indentify a shared object
    """
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
    """
    Send a message to manager using connection `c` and return response
    """
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
        assert type(result) is str
        return RemoteError(result)
    elif kind == '#UNSERIALIZABLE':
        assert type(result) is str
        return RemoteError('Unserializable message: %s\n' % result)
    else:
        return ValueError('Unrecognized message type')


class RemoteError(Exception):

    def __str__(self):
        return '\n' + '-' * 75 + '\n' + str(self.args[0]) + '-' * 75


def all_methods(obj):
    """
    Return a list of names of methods of `obj`
    """
    temp = []
    for name in dir(obj):
        func = getattr(obj, name)
        if hasattr(func, '__call__'):
            temp.append(name)

    return temp


def public_methods(obj):
    """
    Return a list of names of methods of `obj` which do not start with '_'
    """
    return [ name for name in all_methods(obj) if name[0] != '_' ]


class Server(object):
    """
    Server class which runs in a process controlled by a manager object
    """
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
        assert isinstance(authkey, bytes)
        self.registry = registry
        self.authkey = AuthenticationString(authkey)
        Listener, Client = listener_client[serializer]
        self.listener = Listener(address=address, backlog=5)
        self.address = self.listener.address
        self.id_to_obj = {0: (None, ())}
        self.id_to_refcount = {}
        self.mutex = threading.RLock()
        self.stop = 0
        return

    def serve_forever(self):
        """
        Run the server forever
        """
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
        """
        Handle a new connection
        """
        funcname = result = request = None
        try:
            connection.deliver_challenge(c, self.authkey)
            connection.answer_challenge(c, self.authkey)
            request = c.recv()
            ignore, funcname, args, kwds = request
            assert funcname in self.public, '%r unrecognized' % funcname
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

    def serve_client--- This code section failed: ---

 203       0	LOAD_GLOBAL       'util'
           3	LOAD_ATTR         'debug'
           6	LOAD_CONST        'starting server thread to service %r'

 204       9	LOAD_GLOBAL       'threading'
          12	LOAD_ATTR         'current_thread'
          15	CALL_FUNCTION_0   ''
          18	LOAD_ATTR         'name'
          21	CALL_FUNCTION_2   ''
          24	POP_TOP           ''

 206      25	LOAD_FAST         'conn'
          28	LOAD_ATTR         'recv'
          31	STORE_FAST        'recv'

 207      34	LOAD_FAST         'conn'
          37	LOAD_ATTR         'send'
          40	STORE_FAST        'send'

 208      43	LOAD_FAST         'self'
          46	LOAD_ATTR         'id_to_obj'
          49	STORE_FAST        'id_to_obj'

 210      52	SETUP_LOOP        '743'
          55	LOAD_FAST         'self'
          58	LOAD_ATTR         'stop'
          61	JUMP_IF_TRUE      '742'

 212      64	SETUP_EXCEPT      '352'

 213      67	LOAD_CONST        ''
          70	DUP_TOP           ''
          71	STORE_FAST        'methodname'
          74	STORE_FAST        'obj'

 214      77	LOAD_FAST         'recv'
          80	CALL_FUNCTION_0   ''
          83	STORE_FAST        'request'

 215      86	LOAD_FAST         'request'
          89	UNPACK_SEQUENCE_4 ''
          92	STORE_FAST        'ident'
          95	STORE_FAST        'methodname'
          98	STORE_FAST        'args'
         101	STORE_FAST        'kwds'

 216     104	LOAD_FAST         'id_to_obj'
         107	LOAD_FAST         'ident'
         110	BINARY_SUBSCR     ''
         111	UNPACK_SEQUENCE_3 ''
         114	STORE_FAST        'obj'
         117	STORE_FAST        'exposed'
         120	STORE_FAST        'gettypeid'

 218     123	LOAD_FAST         'methodname'
         126	LOAD_FAST         'exposed'
         129	COMPARE_OP        'not in'
         132	JUMP_IF_FALSE     '169'

 219     135	LOAD_GLOBAL       'AttributeError'

 220     138	LOAD_CONST        'method %r of %r object is not in exposed=%r'

 221     141	LOAD_FAST         'methodname'
         144	LOAD_GLOBAL       'type'
         147	LOAD_FAST         'obj'
         150	CALL_FUNCTION_1   ''
         153	LOAD_FAST         'exposed'
         156	BUILD_TUPLE_3     ''
         159	BINARY_MODULO     ''
         160	CALL_FUNCTION_1   ''
         163	RAISE_VARARGS_1   ''
         166	JUMP_FORWARD      '169'
       169_0	COME_FROM         '166'

 224     169	LOAD_GLOBAL       'getattr'
         172	LOAD_FAST         'obj'
         175	LOAD_FAST         'methodname'
         178	CALL_FUNCTION_2   ''
         181	STORE_FAST        'function'

 226     184	SETUP_EXCEPT      '206'

 227     187	LOAD_FAST         'function'
         190	LOAD_FAST         'args'
         193	LOAD_FAST         'kwds'
         196	CALL_FUNCTION_VAR_KW_0 ''
         199	STORE_FAST        'res'
         202	POP_BLOCK         ''
         203	JUMP_FORWARD      '237'
       206_0	COME_FROM         '184'

 228     206	DUP_TOP           ''
         207	LOAD_GLOBAL       'Exception'
         210	COMPARE_OP        'exception match'
         213	JUMP_IF_FALSE     '236'
         216	POP_TOP           ''
         217	STORE_FAST        'e'
         220	POP_TOP           ''

 229     221	LOAD_CONST        '#ERROR'
         224	LOAD_FAST         'e'
         227	BUILD_TUPLE_2     ''
         230	STORE_FAST        'msg'
         233	JUMP_FORWARD      '348'
         236	END_FINALLY       ''
       237_0	COME_FROM         '203'

 231     237	LOAD_FAST         'gettypeid'
         240	JUMP_IF_FALSE     '258'
         243	LOAD_FAST         'gettypeid'
         246	LOAD_ATTR         'get'
         249	LOAD_FAST         'methodname'
         252	LOAD_CONST        ''
         255	CALL_FUNCTION_2   ''
         258	STORE_FAST        'typeid'

 232     261	LOAD_FAST         'typeid'
         264	JUMP_IF_FALSE     '336'

 233     267	LOAD_FAST         'self'
         270	LOAD_ATTR         'create'
         273	LOAD_FAST         'conn'
         276	LOAD_FAST         'typeid'
         279	LOAD_FAST         'res'
         282	CALL_FUNCTION_3   ''
         285	UNPACK_SEQUENCE_2 ''
         288	STORE_FAST        'rident'
         291	STORE_FAST        'rexposed'

 234     294	LOAD_GLOBAL       'Token'
         297	LOAD_FAST         'typeid'
         300	LOAD_FAST         'self'
         303	LOAD_ATTR         'address'
         306	LOAD_FAST         'rident'
         309	CALL_FUNCTION_3   ''
         312	STORE_FAST        'token'

 235     315	LOAD_CONST        '#PROXY'
         318	LOAD_FAST         'rexposed'
         321	LOAD_FAST         'token'
         324	BUILD_TUPLE_2     ''
         327	BUILD_TUPLE_2     ''
         330	STORE_FAST        'msg'
         333	JUMP_FORWARD      '348'

 237     336	LOAD_CONST        '#RETURN'
         339	LOAD_FAST         'res'
         342	BUILD_TUPLE_2     ''
         345	STORE_FAST        'msg'
       348_0	COME_FROM         '236'
       348_1	COME_FROM         '333'
         348	POP_BLOCK         ''
         349	JUMP_FORWARD      '575'
       352_0	COME_FROM         '64'

 239     352	DUP_TOP           ''
         353	LOAD_GLOBAL       'AttributeError'
         356	COMPARE_OP        'exception match'
         359	JUMP_IF_FALSE     '489'
         362	POP_TOP           ''
         363	POP_TOP           ''
         364	POP_TOP           ''

 240     365	LOAD_FAST         'methodname'
         368	LOAD_CONST        ''
         371	COMPARE_OP        'is'
         374	JUMP_IF_FALSE     '395'

 241     377	LOAD_CONST        '#TRACEBACK'
         380	LOAD_GLOBAL       'format_exc'
         383	CALL_FUNCTION_0   ''
         386	BUILD_TUPLE_2     ''
         389	STORE_FAST        'msg'
         392	JUMP_ABSOLUTE     '575'

 243     395	SETUP_EXCEPT      '454'

 244     398	LOAD_FAST         'self'
         401	LOAD_ATTR         'fallback_mapping'
         404	LOAD_FAST         'methodname'
         407	BINARY_SUBSCR     ''
         408	STORE_FAST        'fallback_func'

 245     411	LOAD_FAST         'fallback_func'

 246     414	LOAD_FAST         'self'
         417	LOAD_FAST         'conn'
         420	LOAD_FAST         'ident'
         423	LOAD_FAST         'obj'
         426	LOAD_FAST         'args'
         429	LOAD_FAST         'kwds'
         432	CALL_FUNCTION_VAR_KW_4 ''
         435	STORE_FAST        'result'

 248     438	LOAD_CONST        '#RETURN'
         441	LOAD_FAST         'result'
         444	BUILD_TUPLE_2     ''
         447	STORE_FAST        'msg'
         450	POP_BLOCK         ''
         451	JUMP_ABSOLUTE     '575'
       454_0	COME_FROM         '395'

 249     454	DUP_TOP           ''
         455	LOAD_GLOBAL       'Exception'
         458	COMPARE_OP        'exception match'
         461	JUMP_IF_FALSE     '485'
         464	POP_TOP           ''
         465	POP_TOP           ''
         466	POP_TOP           ''

 250     467	LOAD_CONST        '#TRACEBACK'
         470	LOAD_GLOBAL       'format_exc'
         473	CALL_FUNCTION_0   ''
         476	BUILD_TUPLE_2     ''
         479	STORE_FAST        'msg'
         482	JUMP_ABSOLUTE     '575'
         485	END_FINALLY       ''
       486_0	COME_FROM         '485'
         486	JUMP_FORWARD      '575'

 252     489	DUP_TOP           ''
         490	LOAD_GLOBAL       'EOFError'
         493	COMPARE_OP        'exception match'
         496	JUMP_IF_FALSE     '543'
         499	POP_TOP           ''
         500	POP_TOP           ''
         501	POP_TOP           ''

 253     502	LOAD_GLOBAL       'util'
         505	LOAD_ATTR         'debug'
         508	LOAD_CONST        'got EOF -- exiting thread serving %r'

 254     511	LOAD_GLOBAL       'threading'
         514	LOAD_ATTR         'current_thread'
         517	CALL_FUNCTION_0   ''
         520	LOAD_ATTR         'name'
         523	CALL_FUNCTION_2   ''
         526	POP_TOP           ''

 255     527	LOAD_GLOBAL       'sys'
         530	LOAD_ATTR         'exit'
         533	LOAD_CONST        0
         536	CALL_FUNCTION_1   ''
         539	POP_TOP           ''
         540	JUMP_FORWARD      '575'

 257     543	DUP_TOP           ''
         544	LOAD_GLOBAL       'Exception'
         547	COMPARE_OP        'exception match'
         550	JUMP_IF_FALSE     '574'
         553	POP_TOP           ''
         554	POP_TOP           ''
         555	POP_TOP           ''

 258     556	LOAD_CONST        '#TRACEBACK'
         559	LOAD_GLOBAL       'format_exc'
         562	CALL_FUNCTION_0   ''
         565	BUILD_TUPLE_2     ''
         568	STORE_FAST        'msg'
         571	JUMP_FORWARD      '575'
         574	END_FINALLY       ''
       575_0	COME_FROM         '349'
       575_1	COME_FROM         '574'

 260     575	SETUP_EXCEPT      '640'

 261     578	SETUP_EXCEPT      '595'

 262     581	LOAD_FAST         'send'
         584	LOAD_FAST         'msg'
         587	CALL_FUNCTION_1   ''
         590	POP_TOP           ''
         591	POP_BLOCK         ''
         592	JUMP_FORWARD      '636'
       595_0	COME_FROM         '578'

 263     595	DUP_TOP           ''
         596	LOAD_GLOBAL       'Exception'
         599	COMPARE_OP        'exception match'
         602	JUMP_IF_FALSE     '635'
         605	POP_TOP           ''
         606	STORE_FAST        'e'
         609	POP_TOP           ''

 264     610	LOAD_FAST         'send'
         613	LOAD_CONST        '#UNSERIALIZABLE'
         616	LOAD_GLOBAL       'repr'
         619	LOAD_FAST         'msg'
         622	CALL_FUNCTION_1   ''
         625	BUILD_TUPLE_2     ''
         628	CALL_FUNCTION_1   ''
         631	POP_TOP           ''
         632	JUMP_FORWARD      '636'
         635	END_FINALLY       ''
       636_0	COME_FROM         '592'
       636_1	COME_FROM         '635'
         636	POP_BLOCK         ''
         637	JUMP_BACK         '55'
       640_0	COME_FROM         '575'

 265     640	DUP_TOP           ''
         641	LOAD_GLOBAL       'Exception'
         644	COMPARE_OP        'exception match'
         647	JUMP_IF_FALSE     '738'
         650	POP_TOP           ''
         651	STORE_FAST        'e'
         654	POP_TOP           ''

 266     655	LOAD_GLOBAL       'util'
         658	LOAD_ATTR         'info'
         661	LOAD_CONST        'exception in thread serving %r'

 267     664	LOAD_GLOBAL       'threading'
         667	LOAD_ATTR         'current_thread'
         670	CALL_FUNCTION_0   ''
         673	LOAD_ATTR         'name'
         676	CALL_FUNCTION_2   ''
         679	POP_TOP           ''

 268     680	LOAD_GLOBAL       'util'
         683	LOAD_ATTR         'info'
         686	LOAD_CONST        ' ... message was %r'
         689	LOAD_FAST         'msg'
         692	CALL_FUNCTION_2   ''
         695	POP_TOP           ''

 269     696	LOAD_GLOBAL       'util'
         699	LOAD_ATTR         'info'
         702	LOAD_CONST        ' ... exception was %r'
         705	LOAD_FAST         'e'
         708	CALL_FUNCTION_2   ''
         711	POP_TOP           ''

 270     712	LOAD_FAST         'conn'
         715	LOAD_ATTR         'close'
         718	CALL_FUNCTION_0   ''
         721	POP_TOP           ''

 271     722	LOAD_GLOBAL       'sys'
         725	LOAD_ATTR         'exit'
         728	LOAD_CONST        1
         731	CALL_FUNCTION_1   ''
         734	POP_TOP           ''
         735	JUMP_BACK         '55'
         738	END_FINALLY       ''
       739_0	COME_FROM         '738'
         739	JUMP_BACK         '55'
         742	POP_BLOCK         ''
       743_0	COME_FROM         '52'
         743	LOAD_CONST        ''
         746	RETURN_VALUE      ''

Syntax error at or near 'POP_BLOCK' token at offset 742

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
        """
        Return some info --- useful to spot problems with refcounting
        """
        self.mutex.acquire()
        try:
            result = []
            keys = self.id_to_obj.keys()
            keys.sort()
            for ident in keys:
                if ident != 0:
                    result.append('  %s:       refcount=%s\n    %s' % (ident, self.id_to_refcount[ident], str(self.id_to_obj[ident][0])[:75]))

            return '\n'.join(result)
        finally:
            self.mutex.release()

    def number_of_objects(self, c):
        """
        Number of shared objects
        """
        return len(self.id_to_obj) - 1

    def shutdown(self, c):
        """
        Shutdown this process
        """
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
        """
        Create a new shared object and return its id
        """
        self.mutex.acquire()
        try:
            callable, exposed, method_to_typeid, proxytype = self.registry[typeid]
            if callable is None:
                assert len(args) == 1 and not kwds
                obj = args[0]
            else:
                obj = callable(*args, **kwds)
            if exposed is None:
                exposed = public_methods(obj)
            if method_to_typeid is not None:
                assert type(method_to_typeid) is dict
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
        """
        Return the methods of the shared object indicated by token
        """
        return tuple(self.id_to_obj[token.id][1])

    def accept_connection(self, c, name):
        """
        Spawn a new thread to serve this connection
        """
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
            assert self.id_to_refcount[ident] >= 1
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
    """
    Base class for managers
    """
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
        """
        Return server object with serve_forever() method and address attribute
        """
        assert self._state.value == State.INITIAL
        return Server(self._registry, self._address, self._authkey, self._serializer)

    def connect(self):
        """
        Connect manager object to the server process
        """
        Listener, Client = listener_client[self._serializer]
        conn = Client(self._address, authkey=self._authkey)
        dispatch(conn, None, 'dummy')
        self._state.value = State.STARTED
        return

    def start(self):
        """
        Spawn a server process for this manager object
        """
        assert self._state.value == State.INITIAL
        reader, writer = connection.Pipe(duplex=False)
        self._process = Process(target=type(self)._run_server, args=(self._registry,
         self._address,
         self._authkey,
         self._serializer,
         writer))
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

    @classmethod
    def _run_server(cls, registry, address, authkey, serializer, writer):
        """
        Create a server, report its address and run it
        """
        server = cls._Server(registry, address, authkey, serializer)
        writer.send(server.address)
        writer.close()
        util.info('manager serving at %r', server.address)
        server.serve_forever()

    def _create(self, typeid, *args, **kwds):
        """
        Create a new shared object; return the token and exposed tuple
        """
        assert self._state.value == State.STARTED, 'server not yet started'
        conn = self._Client(self._address, authkey=self._authkey)
        try:
            id, exposed = dispatch(conn, None, 'create', (typeid,) + args, kwds)
        finally:
            conn.close()

        return (Token(typeid, self._address, id), exposed)

    def join(self, timeout=None):
        """
        Join the manager process (if it has been spawned)
        """
        self._process.join(timeout)

    def _debug_info(self):
        """
        Return some info about the servers shared objects and connections
        """
        conn = self._Client(self._address, authkey=self._authkey)
        try:
            return dispatch(conn, None, 'debug_info')
        finally:
            conn.close()

        return

    def _number_of_objects(self):
        """
        Return the number of shared objects
        """
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
        """
        Shutdown the manager process; will be registered as a finalizer
        """
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
        """
        Register a typeid with the manager type
        """
        if '_registry' not in cls.__dict__:
            cls._registry = cls._registry.copy()
        if proxytype is None:
            proxytype = AutoProxy
        exposed = exposed or getattr(proxytype, '_exposed_', None)
        method_to_typeid = method_to_typeid or getattr(proxytype, '_method_to_typeid_', None)
        if method_to_typeid:
            for key, value in method_to_typeid.items():
                assert type(key) is str, '%r is not a string' % key
                assert type(value) is str, '%r is not a string' % value

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
    """
    A base for proxies of shared objects
    """
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
        """
        Try to call a method of the referrent and return a copy of the result
        """
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
            proxy = proxytype(token, self._serializer, manager=self._manager, authkey=self._authkey, exposed=exposed)
            conn = self._Client(token.address, authkey=self._authkey)
            dispatch(conn, None, 'decref', (token.id,))
            return proxy
        else:
            raise convert_to_error(kind, result)
            return

    def _getvalue(self):
        """
        Get a copy of the value of the referent
        """
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
        """
        Return representation of the referent (or a fall-back if that fails)
        """
        try:
            return self._callmethod('__repr__')
        except Exception:
            return repr(self)[:-1] + "; '__str__()' failed>"


def RebuildProxy(func, token, serializer, kwds):
    """
    Function used for unpickling proxy objects.
    
    If possible the shared object is returned, or otherwise a proxy for it.
    """
    server = getattr(current_process(), '_manager_server', None)
    if server and server.address == token.address:
        return server.id_to_obj[token.id][0]
    else:
        incref = kwds.pop('incref', True) and not getattr(current_process(), '_inheriting', False)
        return func(token, serializer, incref=incref, **kwds)
        return


def MakeProxyType(name, exposed, _cache={}):
    """
    Return an proxy type whose methods are given by `exposed`
    """
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
    """
    Return an auto-proxy for `token`
    """
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
    """
    Subclass of `BaseManager` which supports a number of shared object types.
    
    The types registered are those intended for the synchronization
    of threads, plus `dict`, `list` and `Namespace`.
    
    The `multiprocessing.Manager()` function creates started instances of
    this class.
    """
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