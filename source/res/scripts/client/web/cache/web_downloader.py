# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/cache/web_downloader.py
import time
from functools import partial
from helpers import threads
from gui.shared.RemoteDataDownloader import _HttpOpenUrlJob
from helpers.web.downloader import IDownloader
from shared_utils import nextTick

class WebDownloader(IDownloader):

    def __init__(self, workersLimit, queueLimit=threads.INFINITE_QUEUE_SIZE):
        self.__worker = threads.ThreadPool(workersLimit, queueLimit)
        self.__worker.start()
        self.__paused = False

    @property
    def stopped(self):
        return self.__worker is None

    def close(self):
        if self.__worker:
            self.__worker.stop()
            self.__worker = None
        return

    def downloadLowPriority(self, url, callback):
        self.__worker.putLowPriorityJob(_HttpOpenUrlJob(url, None, partial(self.__onDownload, url, callback)))
        return

    def download(self, url, callback):
        self.__worker.putJob(_HttpOpenUrlJob(url, None, partial(self.__onDownload, url, callback)))
        return

    def setPause(self, value):
        self.__paused = value

    def __onDownload(self, url, callback, data, lastModified, expires):
        while self.__paused:
            time.sleep(1)

        nextTick(partial(callback, url, data))()
