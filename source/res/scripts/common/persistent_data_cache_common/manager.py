# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/persistent_data_cache_common/manager.py
from collections import OrderedDict
import typing
import wg_async
from persistent_data_cache_common.common import getLogger, MeasureExecutionTime, DEFAULT_SAVING_TIMEOUT
from persistent_data_cache_common.data_providers import PDProvider
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from persistent_data_cache_common.caches import BasePDCache
    from persistent_data_cache_common.types import TData, TDataFactory
    from persistent_data_cache_common.serializers import ISerializer

class DefaultPDCManager(object):
    __slots__ = ('_logger', '_cache', '_started', '_dataProviders', '_dataCreateTiming')

    def __init__(self, cache):
        self._logger = getLogger(self.__class__.__name__)
        self._cache = cache
        self._started = False
        self._dataProviders = OrderedDict()
        self._dataCreateTiming = MeasureExecutionTime('data.created')
        self._logger.info('Initialized.')

    def fini(self):
        self._started = False
        self._cache.destroy()
        self._cache = None
        for dataProvider in self._dataProviders.itervalues():
            dataProvider.destroy()

        self._dataProviders = None
        self._logger.info('Destroyed.')
        return

    def load(self, name, factory, serializer):
        if self._started:
            raise SoftException('Data <{}> cannot be load after manager started.'.format(name))
        dataProvider = self._register(name, factory, serializer)
        data = self._loadData(dataProvider)
        self._logger.info('Data has been %s for <%s>.', 'created' if dataProvider.isDataCreated else 'loaded', name)
        return data

    def start(self):
        if self._started:
            self._logger.warning('Already started.')
            return
        self._started = True
        self._start()
        self._dataCreateTiming.printTotalTime()
        self._logger.info('Started.')

    @wg_async.wg_async
    def save(self, timeout=DEFAULT_SAVING_TIMEOUT):
        if not self._started:
            self._logger.warning('Not started yet.')
            raise wg_async.AsyncReturn(False)
        providersToSave = [ provider for provider in self._dataProviders.itervalues() if provider.isDataCreated ]
        if not providersToSave:
            self._logger.debug('Nothing to save.')
            raise wg_async.AsyncReturn(True)
        if len(providersToSave) != len(self._dataProviders):
            self._logger.warning('There is a new cache added to code. But old cache file was not cleared.')
            providersToSave = []
        with MeasureExecutionTime('cache.saved').start():
            result = yield wg_async.wg_await(self._cache.save(providersToSave, timeout=timeout))
        self._logger.info('Data has%s been saved.', '' if result else ' not')
        raise wg_async.AsyncReturn(result)

    def _start(self):
        self._cache.unload()

    def _register(self, name, factory, serializer):
        if name in self._dataProviders:
            raise SoftException('DataProvider with name = {} already registered.'.format(name))
        factory = self._dataCreateTiming(factory, name)
        dataProvider = PDProvider(name, factory, serializer)
        self._dataProviders[name] = dataProvider
        self._logger.debug('Data provider <%s> registered.', name)
        return dataProvider

    def _loadData(self, dataProvider):
        data = self._cache.load(dataProvider)
        if data is None:
            data = dataProvider.create()
        return data


class ForceCreatingPDCManager(DefaultPDCManager):
    __slots__ = ()

    def _loadData(self, dataProvider):
        return dataProvider.create()
