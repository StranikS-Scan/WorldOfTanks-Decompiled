# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/SocketServer.py
# Compiled at: 2010-05-25 20:46:16
"""Generic socket server classes.

This module tries to capture the various aspects of defining a server:

For socket-based servers:

- address family:
        - AF_INET{,6}: IP (Internet Protocol) sockets (default)
        - AF_UNIX: Unix domain sockets
        - others, e.g. AF_DECNET are conceivable (see <socket.h>
- socket type:
        - SOCK_STREAM (reliable stream, e.g. TCP)
        - SOCK_DGRAM (datagrams, e.g. UDP)

For request-based servers (including socket-based):

- client address verification before further looking at the request
        (This is actually a hook for any processing that needs to look
         at the request before anything else, e.g. logging)
- how to handle multiple requests:
        - synchronous (one request is handled at a time)
        - forking (each request is handled by a new process)
        - threading (each request is handled by a new thread)

The classes in this module favor the server type that is simplest to
write: a synchronous TCP/IP server.  This is bad class design, but
save some typing.  (There's also the issue that a deep class hierarchy
slows down method lookups.)

There are five classes in an inheritance diagram, four of which represent
synchronous servers of four types:

        +------------+
        | BaseServer |
        +------------+
              |
              v
        +-----------+        +------------------+
        | TCPServer |------->| UnixStreamServer |
        +-----------+        +------------------+
              |
              v
        +-----------+        +--------------------+
        | UDPServer |------->| UnixDatagramServer |
        +-----------+        +--------------------+

Note that UnixDatagramServer derives from UDPServer, not from
UnixStreamServer -- the only difference between an IP and a Unix
stream server is the address family, which is simply repeated in both
unix server classes.

Forking and threading versions of each type of server can be created
using the ForkingMixIn and ThreadingMixIn mix-in classes.  For
instance, a threading UDP server class is created as follows:

        class ThreadingUDPServer(ThreadingMixIn, UDPServer): pass

The Mix-in class must come first, since it overrides a method defined
in UDPServer! Setting the various member variables also changes
the behavior of the underlying server mechanism.

To implement a service, you must derive a class from
BaseRequestHandler and redefine its handle() method.  You can then run
various versions of the service by combining one of the server classes
with your request handler class.

The request handler class must be different for datagram or stream
services.  This can be hidden by using the request handler
subclasses StreamRequestHandler or DatagramRequestHandler.

Of course, you still have to use your head!

For instance, it makes no sense to use a forking server if the service
contains state in memory that can be modified by requests (since the
modifications in the child process would never reach the initial state
kept in the parent process and passed to each child).  In this case,
you can use a threading server, but you will probably have to use
locks to avoid two requests that come in nearly simultaneous to apply
conflicting changes to the server state.

On the other hand, if you are building e.g. an HTTP server, where all
data is stored externally (e.g. in the file system), a synchronous
class will essentially render the service "deaf" while one request is
being handled -- which may be for a very long time if a client is slow
to reqd all the data it has requested.  Here a threading or forking
server is appropriate.

In some cases, it may be appropriate to process part of a request
synchronously, but to finish processing in a forked child depending on
the request data.  This can be implemented by using a synchronous
server and doing an explicit fork in the request handler class
handle() method.

Another approach to handling multiple simultaneous requests in an
environment that supports neither threads nor fork (or where these are
too expensive or inappropriate for the service) is to maintain an
explicit table of partially finished requests and to use select() to
decide which request to work on next (or whether to handle a new
incoming request).  This is particularly important for stream services
where each client can potentially be connected for a long time (if
threads or subprocesses cannot be used).

Future work:
- Standard classes for Sun RPC (which uses either UDP or TCP)
- Standard mix-in classes to implement various authentication
  and encryption schemes
- Standard framework for select-based multiplexing

XXX Open problems:
- What to do with out-of-band data?

BaseServer:
- split generic "request" functionality out into BaseServer class.
  Copyright (C) 2000  Luke Kenneth Casson Leighton <lkcl@samba.org>

  example: read entries from a SQL database (requires overriding
  get_request() to return a table entry from the database).
  entry is processed by a RequestHandlerClass.

"""
__version__ = '0.4'
import socket
import select
import sys
import os
try:
    import threading
except ImportError:
    import dummy_threading as threading

__all__ = ['TCPServer',
 'UDPServer',
 'ForkingUDPServer',
 'ForkingTCPServer',
 'ThreadingUDPServer',
 'ThreadingTCPServer',
 'BaseRequestHandler',
 'StreamRequestHandler',
 'DatagramRequestHandler',
 'ThreadingMixIn',
 'ForkingMixIn']
if hasattr(socket, 'AF_UNIX'):
    __all__.extend(['UnixStreamServer',
     'UnixDatagramServer',
     'ThreadingUnixStreamServer',
     'ThreadingUnixDatagramServer'])

class BaseServer:
    """Base class for server classes.
    
    Methods for the caller:
    
    - __init__(server_address, RequestHandlerClass)
    - serve_forever(poll_interval=0.5)
    - shutdown()
    - handle_request()  # if you do not use serve_forever()
    - fileno() -> int   # for select()
    
    Methods that may be overridden:
    
    - server_bind()
    - server_activate()
    - get_request() -> request, client_address
    - handle_timeout()
    - verify_request(request, client_address)
    - server_close()
    - process_request(request, client_address)
    - close_request(request)
    - handle_error()
    
    Methods for derived classes:
    
    - finish_request(request, client_address)
    
    Class variables that may be overridden by derived classes or
    instances:
    
    - timeout
    - address_family
    - socket_type
    - allow_reuse_address
    
    Instance variables:
    
    - RequestHandlerClass
    - socket
    
    """
    timeout = None

    def __init__(self, server_address, RequestHandlerClass):
        """Constructor.  May be extended, do not override."""
        self.server_address = server_address
        self.RequestHandlerClass = RequestHandlerClass
        self.__is_shut_down = threading.Event()
        self.__serving = False

    def server_activate(self):
        """Called by constructor to activate the server.
        
        May be overridden.
        
        """
        pass

    def serve_forever(self, poll_interval=0.5):
        """Handle one request at a time until shutdown.
        
        Polls for shutdown every poll_interval seconds. Ignores
        self.timeout. If you need to do periodic tasks, do them in
        another thread.
        """
        self.__serving = True
        self.__is_shut_down.clear()
        while 1:
            if self.__serving:
                r, w, e = select.select([self], [], [], poll_interval)
                r and self._handle_request_noblock()

        self.__is_shut_down.set()

    def shutdown(self):
        """Stops the serve_forever loop.
        
        Blocks until the loop has finished. This must be called while
        serve_forever() is running in another thread, or it will
        deadlock.
        """
        self.__serving = False
        self.__is_shut_down.wait()

    def handle_request(self):
        """Handle one request, possibly blocking.
        
        Respects self.timeout.
        """
        timeout = self.socket.gettimeout()
        if timeout is None:
            timeout = self.timeout
        elif self.timeout is not None:
            timeout = min(timeout, self.timeout)
        fd_sets = select.select([self], [], [], timeout)
        if not fd_sets[0]:
            self.handle_timeout()
            return
        else:
            self._handle_request_noblock()
            return

    def _handle_request_noblock(self):
        """Handle one request, without blocking.
        
        I assume that select.select has returned that the socket is
        readable before this function was called, so there should be
        no risk of blocking in get_request().
        """
        try:
            request, client_address = self.get_request()
        except socket.error:
            return

        if self.verify_request(request, client_address):
            try:
                self.process_request(request, client_address)
            except:
                self.handle_error(request, client_address)
                self.close_request(request)

    def handle_timeout(self):
        """Called if no new request arrives within self.timeout.
        
        Overridden by ForkingMixIn.
        """
        pass

    def verify_request(self, request, client_address):
        """Verify the request.  May be overridden.
        
        Return True if we should proceed with this request.
        
        """
        return True

    def process_request(self, request, client_address):
        """Call finish_request.
        
        Overridden by ForkingMixIn and ThreadingMixIn.
        
        """
        self.finish_request(request, client_address)
        self.close_request(request)

    def server_close(self):
        """Called to clean-up the server.
        
        May be overridden.
        
        """
        pass

    def finish_request(self, request, client_address):
        """Finish one request by instantiating RequestHandlerClass."""
        self.RequestHandlerClass(request, client_address, self)

    def close_request(self, request):
        """Called to clean up an individual request."""
        pass

    def handle_error(self, request, client_address):
        """Handle an error gracefully.  May be overridden.
        
        The default is to print a traceback and continue.
        
        """
        print '-' * 40
        print 'Exception happened during processing of request from',
        print client_address
        import traceback
        traceback.print_exc()
        print '-' * 40


class TCPServer(BaseServer):
    """Base class for various socket-based server classes.
    
    Defaults to synchronous IP stream (i.e., TCP).
    
    Methods for the caller:
    
    - __init__(server_address, RequestHandlerClass, bind_and_activate=True)
    - serve_forever(poll_interval=0.5)
    - shutdown()
    - handle_request()  # if you don't use serve_forever()
    - fileno() -> int   # for select()
    
    Methods that may be overridden:
    
    - server_bind()
    - server_activate()
    - get_request() -> request, client_address
    - handle_timeout()
    - verify_request(request, client_address)
    - process_request(request, client_address)
    - close_request(request)
    - handle_error()
    
    Methods for derived classes:
    
    - finish_request(request, client_address)
    
    Class variables that may be overridden by derived classes or
    instances:
    
    - timeout
    - address_family
    - socket_type
    - request_queue_size (only for stream sockets)
    - allow_reuse_address
    
    Instance variables:
    
    - server_address
    - RequestHandlerClass
    - socket
    
    """
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5
    allow_reuse_address = False

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        """Constructor.  May be extended, do not override."""
        BaseServer.__init__(self, server_address, RequestHandlerClass)
        self.socket = socket.socket(self.address_family, self.socket_type)
        if bind_and_activate:
            self.server_bind()
            self.server_activate()

    def server_bind(self):
        """Called by constructor to bind the socket.
        
        May be overridden.
        
        """
        if self.allow_reuse_address:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()

    def server_activate(self):
        """Called by constructor to activate the server.
        
        May be overridden.
        
        """
        self.socket.listen(self.request_queue_size)

    def server_close(self):
        """Called to clean-up the server.
        
        May be overridden.
        
        """
        self.socket.close()

    def fileno(self):
        """Return socket file number.
        
        Interface required by select().
        
        """
        return self.socket.fileno()

    def get_request(self):
        """Get the request and client address from the socket.
        
        May be overridden.
        
        """
        return self.socket.accept()

    def close_request(self, request):
        """Called to clean up an individual request."""
        request.close()


class UDPServer(TCPServer):
    """UDP server class."""
    allow_reuse_address = False
    socket_type = socket.SOCK_DGRAM
    max_packet_size = 8192

    def get_request(self):
        data, client_addr = self.socket.recvfrom(self.max_packet_size)
        return ((data, self.socket), client_addr)

    def server_activate(self):
        pass

    def close_request(self, request):
        pass


class ForkingMixIn:
    """Mix-in class to handle each request in a new process."""
    timeout = 300
    active_children = None
    max_children = 40

    def collect_children--- This code section failed: ---

 483       0	LOAD_FAST         'self'
           3	LOAD_ATTR         'active_children'
           6	LOAD_CONST        ''
           9	COMPARE_OP        'is'
          12	JUMP_IF_FALSE     '19'
          15	LOAD_CONST        ''
          18	RETURN_END_IF     ''

 484      19	SETUP_LOOP        '144'
          22	LOAD_GLOBAL       'len'
          25	LOAD_FAST         'self'
          28	LOAD_ATTR         'active_children'
          31	CALL_FUNCTION_1   ''
          34	LOAD_FAST         'self'
          37	LOAD_ATTR         'max_children'
          40	COMPARE_OP        '>='
          43	JUMP_IF_FALSE     '143'

 489      46	SETUP_EXCEPT      '77'

 490      49	LOAD_GLOBAL       'os'
          52	LOAD_ATTR         'waitpid'
          55	LOAD_CONST        0
          58	LOAD_CONST        0
          61	CALL_FUNCTION_2   ''
          64	UNPACK_SEQUENCE_2 ''
          67	STORE_FAST        'pid'
          70	STORE_FAST        'status'
          73	POP_BLOCK         ''
          74	JUMP_FORWARD      '103'
        77_0	COME_FROM         '46'

 491      77	DUP_TOP           ''
          78	LOAD_GLOBAL       'os'
          81	LOAD_ATTR         'error'
          84	COMPARE_OP        'exception match'
          87	JUMP_IF_FALSE     '102'
          90	POP_TOP           ''
          91	POP_TOP           ''
          92	POP_TOP           ''

 492      93	LOAD_CONST        ''
          96	STORE_FAST        'pid'
          99	JUMP_FORWARD      '103'
         102	END_FINALLY       ''
       103_0	COME_FROM         '74'
       103_1	COME_FROM         '102'

 493     103	LOAD_FAST         'pid'
         106	LOAD_FAST         'self'
         109	LOAD_ATTR         'active_children'
         112	COMPARE_OP        'not in'
         115	JUMP_IF_FALSE     '124'
         118	CONTINUE          '22'
         121	JUMP_FORWARD      '124'
       124_0	COME_FROM         '121'

 494     124	LOAD_FAST         'self'
         127	LOAD_ATTR         'active_children'
         130	LOAD_ATTR         'remove'
         133	LOAD_FAST         'pid'
         136	CALL_FUNCTION_1   ''
         139	POP_TOP           ''
         140	JUMP_BACK         '22'
         143	POP_BLOCK         ''
       144_0	COME_FROM         '19'

 501     144	SETUP_LOOP        '309'
         147	LOAD_FAST         'self'
         150	LOAD_ATTR         'active_children'
         153	GET_ITER          ''
         154	FOR_ITER          '308'
         157	STORE_FAST        'child'

 502     160	SETUP_EXCEPT      '194'

 503     163	LOAD_GLOBAL       'os'
         166	LOAD_ATTR         'waitpid'
         169	LOAD_FAST         'child'
         172	LOAD_GLOBAL       'os'
         175	LOAD_ATTR         'WNOHANG'
         178	CALL_FUNCTION_2   ''
         181	UNPACK_SEQUENCE_2 ''
         184	STORE_FAST        'pid'
         187	STORE_FAST        'status'
         190	POP_BLOCK         ''
         191	JUMP_FORWARD      '220'
       194_0	COME_FROM         '160'

 504     194	DUP_TOP           ''
         195	LOAD_GLOBAL       'os'
         198	LOAD_ATTR         'error'
         201	COMPARE_OP        'exception match'
         204	JUMP_IF_FALSE     '219'
         207	POP_TOP           ''
         208	POP_TOP           ''
         209	POP_TOP           ''

 505     210	LOAD_CONST        ''
         213	STORE_FAST        'pid'
         216	JUMP_FORWARD      '220'
         219	END_FINALLY       ''
       220_0	COME_FROM         '191'
       220_1	COME_FROM         '219'

 506     220	LOAD_FAST         'pid'
         223	JUMP_IF_TRUE      '232'
         226	CONTINUE          '154'
         229	JUMP_FORWARD      '232'
       232_0	COME_FROM         '229'

 507     232	SETUP_EXCEPT      '255'

 508     235	LOAD_FAST         'self'
         238	LOAD_ATTR         'active_children'
         241	LOAD_ATTR         'remove'
         244	LOAD_FAST         'pid'
         247	CALL_FUNCTION_1   ''
         250	POP_TOP           ''
         251	POP_BLOCK         ''
         252	JUMP_BACK         '154'
       255_0	COME_FROM         '232'

 509     255	DUP_TOP           ''
         256	LOAD_GLOBAL       'ValueError'
         259	COMPARE_OP        'exception match'
         262	JUMP_IF_FALSE     '304'
         265	POP_TOP           ''
         266	STORE_FAST        'e'
         269	POP_TOP           ''

 510     270	LOAD_GLOBAL       'ValueError'
         273	LOAD_CONST        '%s. x=%d and list=%r'
         276	LOAD_FAST         'e'
         279	LOAD_ATTR         'message'
         282	LOAD_FAST         'pid'

 511     285	LOAD_FAST         'self'
         288	LOAD_ATTR         'active_children'
         291	BUILD_TUPLE_3     ''
         294	BINARY_MODULO     ''
         295	CALL_FUNCTION_1   ''
         298	RAISE_VARARGS_1   ''
         301	JUMP_BACK         '154'
         304	END_FINALLY       ''
       305_0	COME_FROM         '304'
         305	JUMP_BACK         '154'
         308	POP_BLOCK         ''
       309_0	COME_FROM         '144'
         309	LOAD_CONST        ''
         312	RETURN_VALUE      ''

Syntax error at or near 'POP_BLOCK' token at offset 143

    def handle_timeout(self):
        """Wait for zombies after self.timeout seconds of inactivity.
        
        May be extended, do not override.
        """
        self.collect_children()

    def process_request(self, request, client_address):
        """Fork a new subprocess to process the request."""
        self.collect_children()
        pid = os.fork()
        if pid:
            if self.active_children is None:
                self.active_children = []
            self.active_children.append(pid)
            self.close_request(request)
            return
        else:
            try:
                self.finish_request(request, client_address)
                os._exit(0)
            except:
                try:
                    self.handle_error(request, client_address)
                finally:
                    os._exit(1)

            return


class ThreadingMixIn:
    """Mix-in class to handle each request in a new thread."""
    daemon_threads = False

    def process_request_thread(self, request, client_address):
        """Same as in BaseServer but as a thread.
        
        In addition, exception handling is done here.
        
        """
        try:
            self.finish_request(request, client_address)
            self.close_request(request)
        except:
            self.handle_error(request, client_address)
            self.close_request(request)

    def process_request(self, request, client_address):
        """Start a new thread to process the request."""
        t = threading.Thread(target=self.process_request_thread, args=(request, client_address))
        if self.daemon_threads:
            t.setDaemon(1)
        t.start()


class ForkingUDPServer(ForkingMixIn, UDPServer):
    pass


class ForkingTCPServer(ForkingMixIn, TCPServer):
    pass


class ThreadingUDPServer(ThreadingMixIn, UDPServer):
    pass


class ThreadingTCPServer(ThreadingMixIn, TCPServer):
    pass


if hasattr(socket, 'AF_UNIX'):

    class UnixStreamServer(TCPServer):
        address_family = socket.AF_UNIX


    class UnixDatagramServer(UDPServer):
        address_family = socket.AF_UNIX


    class ThreadingUnixStreamServer(ThreadingMixIn, UnixStreamServer):
        pass


    class ThreadingUnixDatagramServer(ThreadingMixIn, UnixDatagramServer):
        pass


class BaseRequestHandler:
    """Base class for request handler classes.
    
    This class is instantiated for each request to be handled.  The
    constructor sets the instance variables request, client_address
    and server, and then calls the handle() method.  To implement a
    specific service, all you need to do is to derive a class which
    defines a handle() method.
    
    The handle() method can find the request as self.request, the
    client address as self.client_address, and the server (in case it
    needs access to per-server information) as self.server.  Since a
    separate instance is created for each request, the handle() method
    can define arbitrary other instance variariables.
    
    """

    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        try:
            self.setup()
            self.handle()
            self.finish()
        finally:
            sys.exc_traceback = None

        return

    def setup(self):
        pass

    def handle(self):
        pass

    def finish(self):
        pass


class StreamRequestHandler(BaseRequestHandler):
    """Define self.rfile and self.wfile for stream sockets."""
    rbufsize = -1
    wbufsize = 0

    def setup(self):
        self.connection = self.request
        self.rfile = self.connection.makefile('rb', self.rbufsize)
        self.wfile = self.connection.makefile('wb', self.wbufsize)

    def finish(self):
        if not self.wfile.closed:
            self.wfile.flush()
        self.wfile.close()
        self.rfile.close()


class DatagramRequestHandler(BaseRequestHandler):
    """Define self.rfile and self.wfile for datagram sockets."""

    def setup(self):
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO

        self.packet, self.socket = self.request
        self.rfile = StringIO(self.packet)
        self.wfile = StringIO()

    def finish(self):
        self.socket.sendto(self.wfile.getvalue(), self.client_address)