# Embedded file name: scripts/client/standalone/login/HttpServer.py
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn
from socket import error as SocketError
from threading import Thread
import sys

class HttpServer(HTTPServer):
    allow_reuse_address = False
    __BIND_ADDRESS = '127.0.0.1'
    __PORTS_POOL = (50010, 50011, 50012, 50013, 50014)

    def __init__(self, name, requestHandlerClass):
        socketBindSuccess = False
        for port_number in self.__PORTS_POOL:
            try:
                if not socketBindSuccess:
                    HTTPServer.__init__(self, (self.__BIND_ADDRESS, port_number), requestHandlerClass)
                    socketBindSuccess = True
            except SocketError as e:
                self._currentStatus = 'Failed to bind socket to {0}:{1}'.format(self.__BIND_ADDRESS, port_number)
                self._logStatus()
                if port_number == self.__PORTS_POOL[4]:
                    self._currentStatus = 'Giving up.'
                    self._logStatus()
                    raise e
                else:
                    continue

        self.__name = name
        self.__setStatus('NOT RUNNING')
        self.__serverThread = None
        return

    def start_listening(self):
        if self.__serverThread is not None:
            self._logStatus()
            return
        else:
            self.__serverThread = Thread(target=self.serve_forever)
            self.__serverThread.start()
            self.__setStatus('RUNNING')
            self._logStatus()
            return

    def stop_listening(self):
        if self.__serverThread is None:
            self._logStatus()
            return
        else:
            self.shutdown()
            self.__serverThread = None
            self.__setStatus('NOT RUNNING')
            self._logStatus()
            return

    def __setStatus(self, status):
        self._currentStatus = '{0} (http://localhost:{1}): {2}.'.format(self.__name, self.server_port, status)

    def _logStatus(self):
        sys.stdout.write(self._currentStatus + '\n')

    @property
    def name(self):
        return self.__name


class ThreadedHttpServer(HttpServer, ThreadingMixIn):
    pass
