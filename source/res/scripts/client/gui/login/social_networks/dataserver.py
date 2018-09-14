# Embedded file name: scripts/client/gui/login/social_networks/DataServer.py
import os
import base64
import hashlib
from Event import Event
from Crypto.Cipher import AES
from Crypto.Util import Counter
from debug_utils import LOG_DEBUG
from RequestHandler import RequestHandler
from standalone.login import ThreadedHttpServer, HttpServer

class DataServer(HttpServer):

    def __init__(self, name):
        HttpServer.__init__(self, name, RequestHandler)
        self.dataReceived = Event()

    def keepData(self, token, spaID):
        self.dataReceived(token, spaID)

    def _logStatus(self):
        LOG_DEBUG(self._currentStatus)


class EncryptingDataServer(DataServer):

    def __init__(self, name):
        DataServer.__init__(self, name)
        self._tokenSecret = hashlib.sha1(os.urandom(128)).hexdigest()[:16]

    def keepData(self, token, spaID):
        cipher = AES.new(self._tokenSecret, AES.MODE_CTR, counter=Counter.new(128))
        token = cipher.decrypt(base64.urlsafe_b64decode(token))
        DataServer.keepData(self, token, spaID)

    @property
    def tokenSecret(self):
        return self._tokenSecret


class ThreadedDataServer(DataServer, ThreadedHttpServer):

    def __init__(self, name):
        DataServer.__init__(self, name)


class EncryptingThreadedDataServer(EncryptingDataServer, ThreadedHttpServer):

    def __init__(self, name):
        EncryptingDataServer.__init__(self, name)
