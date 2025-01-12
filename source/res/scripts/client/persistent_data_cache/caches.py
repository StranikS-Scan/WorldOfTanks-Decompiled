# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/persistent_data_cache/caches.py
from functools import partial
import typing
import BigWorld
import wg_async
from helpers.threads import ThreadPool, Job
from persistent_data_cache_common.caches import DefaultPDCache
from persistent_data_cache_common.common import getLogger, DEFAULT_SAVING_TIMEOUT
if typing.TYPE_CHECKING:
    from persistent_data_cache_common import cached_data
    from persistent_data_cache_common.configs import BasePDCConfig
    from persistent_data_cache_common.data_providers import PDProvider
    from persistent_data_cache_common.events import DefaultPDCEventsDispatcher
_logger = getLogger('Caches')

class _ThreadJob(Job):

    def __init__(self, func, callback):
        super(_ThreadJob, self).__init__()
        self._func = func
        self._callback = callback

    def doWork(self, worker):
        result = None
        try:
            try:
                result = self._func()
            except Exception:
                _logger.exception('Func <%s> execution failed.', self._func)

        finally:
            BigWorld.callback(0.0, partial(self._callback, result))

        return


class ThreadSavingPDCache(DefaultPDCache):
    __slots__ = ('_threadWorker',)

    def __init__(self, config, eventsDispatcher):
        super(ThreadSavingPDCache, self).__init__(config, eventsDispatcher)
        self._threadWorker = ThreadPool(workersLimit=1)

    def destroy(self):
        if self._threadWorker.isRunning:
            self._threadWorker.stop()
        self._threadWorker = None
        super(ThreadSavingPDCache, self).destroy()
        return

    @wg_async.wg_async
    def save(self, dataProviders, timeout=DEFAULT_SAVING_TIMEOUT):
        if not self._threadWorker or self._threadWorker.isRunning:
            self._logger.warning('Saving in progress or canceled.')
            raise wg_async.AsyncReturn(False)
        self._logger.debug('Background saving started.')
        self._threadWorker.start()
        result = yield wg_async.wg_await(super(ThreadSavingPDCache, self).save(dataProviders, timeout))
        if self._threadWorker and self._threadWorker.isRunning:
            self._threadWorker.stop()
        self._logger.debug('Background saving complete.')
        raise wg_async.AsyncReturn(result)

    @wg_async.wg_async
    def _tryToDeleteCacheFile(self, filePath):
        func = partial(super(ThreadSavingPDCache, self)._tryToDeleteCacheFile, filePath)
        result = yield wg_async.await_callback(self._startJob)(func, errorResult=False)
        raise wg_async.AsyncReturn(result)

    @wg_async.wg_async
    def _tryToSerializeData(self, dataProvider):
        func = partial(super(ThreadSavingPDCache, self)._tryToSerializeData, dataProvider)
        result = yield wg_async.await_callback(self._startJob)(func, errorResult=None)
        raise wg_async.AsyncReturn(result)
        return

    @wg_async.wg_async
    def _tryToSaveCachedData(self, filePath, cachedData):
        func = partial(super(ThreadSavingPDCache, self)._tryToSaveCachedData, filePath, cachedData)
        result = yield wg_async.await_callback(self._startJob)(func, errorResult=False)
        raise wg_async.AsyncReturn(result)

    def _startJob(self, func, callback, errorResult=None):
        if not self._threadWorker or not self._threadWorker.isRunning:
            self._logger.error('Starting job <%s> when worker is stopped. Sending result <%s>.', func, errorResult)
            callback(errorResult)
            return
        job = _ThreadJob(func=func, callback=callback)
        self._threadWorker.putJob(job)
