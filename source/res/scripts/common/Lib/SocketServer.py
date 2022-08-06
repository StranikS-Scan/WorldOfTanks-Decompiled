# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/SocketServer.py
__version__ = '0.4'
import socket
import select
import sys
import os
import errno
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

def _eintr_retry(func, *args):
    while True:
        try:
            return func(*args)
        except (OSError, select.error) as e:
            if e.args[0] != errno.EINTR:
                raise


class BaseServer:
    timeout = None

    def __init__(self, server_address, RequestHandlerClass):
        self.server_address = server_address
        self.RequestHandlerClass = RequestHandlerClass
        self.__is_shut_down = threading.Event()
        self.__shutdown_request = False

    def server_activate(self):
        pass

    def serve_forever(self, poll_interval=0.5):
        self.__is_shut_down.clear()
        try:
            while not self.__shutdown_request:
                r, w, e = _eintr_retry(select.select, [self], [], [], poll_interval)
                if self.__shutdown_request:
                    break
                if self in r:
                    self._handle_request_noblock()

        finally:
            self.__shutdown_request = False
            self.__is_shut_down.set()

    def shutdown(self):
        self.__shutdown_request = True
        self.__is_shut_down.wait()

    def handle_request(self):
        timeout = self.socket.gettimeout()
        if timeout is None:
            timeout = self.timeout
        elif self.timeout is not None:
            timeout = min(timeout, self.timeout)
        fd_sets = _eintr_retry(select.select, [self], [], [], timeout)
        if not fd_sets[0]:
            self.handle_timeout()
            return
        else:
            self._handle_request_noblock()
            return

    def _handle_request_noblock(self):
        try:
            request, client_address = self.get_request()
        except socket.error:
            return

        if self.verify_request(request, client_address):
            try:
                self.process_request(request, client_address)
            except:
                self.handle_error(request, client_address)
                self.shutdown_request(request)

        else:
            self.shutdown_request(request)

    def handle_timeout(self):
        pass

    def verify_request(self, request, client_address):
        return True

    def process_request(self, request, client_address):
        self.finish_request(request, client_address)
        self.shutdown_request(request)

    def server_close(self):
        pass

    def finish_request(self, request, client_address):
        self.RequestHandlerClass(request, client_address, self)

    def shutdown_request(self, request):
        self.close_request(request)

    def close_request(self, request):
        pass

    def handle_error(self, request, client_address):
        print '-' * 40
        print 'Exception happened during processing of request from',
        print client_address
        import traceback
        traceback.print_exc()
        print '-' * 40


class TCPServer(BaseServer):
    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 5
    allow_reuse_address = False

    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        BaseServer.__init__(self, server_address, RequestHandlerClass)
        self.socket = socket.socket(self.address_family, self.socket_type)
        if bind_and_activate:
            try:
                self.server_bind()
                self.server_activate()
            except:
                self.server_close()
                raise

    def server_bind(self):
        if self.allow_reuse_address:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()

    def server_activate(self):
        self.socket.listen(self.request_queue_size)

    def server_close(self):
        self.socket.close()

    def fileno(self):
        return self.socket.fileno()

    def get_request(self):
        return self.socket.accept()

    def shutdown_request(self, request):
        try:
            request.shutdown(socket.SHUT_WR)
        except socket.error:
            pass

        self.close_request(request)

    def close_request(self, request):
        request.close()


class UDPServer(TCPServer):
    allow_reuse_address = False
    socket_type = socket.SOCK_DGRAM
    max_packet_size = 8192

    def get_request(self):
        data, client_addr = self.socket.recvfrom(self.max_packet_size)
        return ((data, self.socket), client_addr)

    def server_activate(self):
        pass

    def shutdown_request(self, request):
        self.close_request(request)

    def close_request(self, request):
        pass


class ForkingMixIn:
    timeout = 300
    active_children = None
    max_children = 40

    def collect_children(self):
        if self.active_children is None:
            return
        else:
            while len(self.active_children) >= self.max_children:
                try:
                    pid, _ = os.waitpid(-1, 0)
                    self.active_children.discard(pid)
                except OSError as e:
                    if e.errno == errno.ECHILD:
                        self.active_children.clear()
                    elif e.errno != errno.EINTR:
                        break

            for pid in self.active_children.copy():
                try:
                    pid, _ = os.waitpid(pid, os.WNOHANG)
                    self.active_children.discard(pid)
                except OSError as e:
                    if e.errno == errno.ECHILD:
                        self.active_children.discard(pid)

            return

    def handle_timeout(self):
        self.collect_children()

    def process_request(self, request, client_address):
        self.collect_children()
        pid = os.fork()
        if pid:
            if self.active_children is None:
                self.active_children = set()
            self.active_children.add(pid)
            self.close_request(request)
            return
        else:
            try:
                self.finish_request(request, client_address)
                self.shutdown_request(request)
                os._exit(0)
            except:
                try:
                    self.handle_error(request, client_address)
                    self.shutdown_request(request)
                finally:
                    os._exit(1)

            return


class ThreadingMixIn:
    daemon_threads = False

    def process_request_thread(self, request, client_address):
        try:
            self.finish_request(request, client_address)
            self.shutdown_request(request)
        except:
            self.handle_error(request, client_address)
            self.shutdown_request(request)

    def process_request(self, request, client_address):
        t = threading.Thread(target=self.process_request_thread, args=(request, client_address))
        t.daemon = self.daemon_threads
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

    def __init__(self, request, client_address, server):
        self.request = request
        self.client_address = client_address
        self.server = server
        self.setup()
        try:
            self.handle()
        finally:
            self.finish()

    def setup(self):
        pass

    def handle(self):
        pass

    def finish(self):
        pass


class StreamRequestHandler(BaseRequestHandler):
    rbufsize = -1
    wbufsize = 0
    timeout = None
    disable_nagle_algorithm = False

    def setup(self):
        self.connection = self.request
        if self.timeout is not None:
            self.connection.settimeout(self.timeout)
        if self.disable_nagle_algorithm:
            self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
        self.rfile = self.connection.makefile('rb', self.rbufsize)
        self.wfile = self.connection.makefile('wb', self.wbufsize)
        return

    def finish(self):
        if not self.wfile.closed:
            try:
                self.wfile.flush()
            except socket.error:
                pass

        self.wfile.close()
        self.rfile.close()


class DatagramRequestHandler(BaseRequestHandler):

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
