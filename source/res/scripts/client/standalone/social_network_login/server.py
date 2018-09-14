# Embedded file name: scripts/client/standalone/social_network_login/Server.py
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn
from threading import Thread
import sys

class Server(ThreadingMixIn, HTTPServer):

    def __init__(self, name, requestHandlerClass):
        BIND_ADDRESS = '127.0.0.1'
        self.__name = name
        HTTPServer.__init__(self, (BIND_ADDRESS, 0), requestHandlerClass)
        self.__setStatus('NOT RUNNING')
        self.__serverThread = None
        return

    def start(self):
        if self.__serverThread is not None:
            self._logStatus()
            return
        else:
            self.__serverThread = Thread(target=HTTPServer.serve_forever, args=(self,))
            self.__serverThread.start()
            self.__setStatus('RUNNING')
            self._logStatus()
            return

    def stop(self):
        if self.__serverThread is None:
            self._logStatus()
            return
        else:
            HTTPServer.shutdown(self)
            self.__serverThread = None
            self.__setStatus('NOT RUNNING')
            self._logStatus()
            return

    def __setStatus(self, status):
        self._currentStatus = '{0} (http://localhost:{1}): {2}.'.format(self.__name, self.server_port, status)

    def _logStatus(self):
        sys.stdout.write(self._currentStatus + '\n')
