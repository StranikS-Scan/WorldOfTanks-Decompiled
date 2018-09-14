# Embedded file name: scripts/client/helpers/RSSDownloader.py
import threading
import helpers
import BigWorld
import feedparser
from debug_utils import *
_CLIENT_VERSION = helpers.getFullClientVersion()
feedparser.PARSE_MICROFORMATS = 0
feedparser.SANITIZE_HTML = 0

class RSSDownloader:
    UPDATE_INTERVAL = 0.1
    lastRSS = property(lambda self: self.__lastRSS)
    isBusy = property(lambda self: self.__thread is not None)

    def __init__(self):
        self.__thread = None
        self.__lastDownloadTime = None
        self.__cbID = BigWorld.callback(self.UPDATE_INTERVAL, self.__update)
        self.__lastRSS = {}
        self.__onCompleteCallbacks = set()
        return

    def destroy(self):
        self.__thread = None
        self.__onCompleteCallbacks = None
        self.__lastDownloadTime = None
        if self.__cbID is not None:
            BigWorld.cancelCallback(self.__cbID)
            self.__cbID = None
        return

    def download(self, callback, url):
        if not callback is not None:
            raise AssertionError
            self.__thread is not None and LOG_WARNING('Rss downloading in progress, skipping')
            return
        else:
            if self.__thread is not None:
                self.__onCompleteCallbacks.add(callback)
            else:
                self.__lastDownloadTime = BigWorld.time()
                self.__thread = _WorkerThread(url)
                self.__onCompleteCallbacks.add(callback)
            return

    def __update(self):
        self.__cbID = BigWorld.callback(self.UPDATE_INTERVAL, self.__update)
        if self.__thread is None or self.__thread.isAlive():
            return
        else:
            if self.__thread.result is not None:
                self.__lastRSS = self.__thread.result
            for callback in self.__onCompleteCallbacks:
                try:
                    callback(self.__lastRSS)
                except:
                    LOG_CURRENT_EXCEPTION()

            self.__onCompleteCallbacks = set()
            self.__thread = None
            return


class _WorkerThread(threading.Thread):

    def __init__(self, url):
        super(_WorkerThread, self).__init__()
        self.url = url
        self.result = None
        self.name = 'RSS Downloader thread'
        self.start()
        return

    def run(self):
        try:
            self.result = feedparser.parse(self.url, None, None, _CLIENT_VERSION)
        except:
            LOG_CURRENT_EXCEPTION()

        return


g_downloader = None

def init():
    global g_downloader
    g_downloader = RSSDownloader()
