# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/persistent_data_cache/__init__.py
import os
import sys
import typing
import BigWorld
import constants
from helpers import ExitCode
from persistent_data_cache import configs
from persistent_data_cache import fault_tolerance
from persistent_data_cache.caches import ThreadSavingPDCache
from persistent_data_cache.manager import ClientForceCreatingPDCManager
from persistent_data_cache.version import getClientPDCVersion
from persistent_data_cache_common import load, start, save, fini as commonFini, init as commonInit
from persistent_data_cache_common.caches import DefaultPDCache
from persistent_data_cache_common.manager import DefaultPDCManager
from persistent_data_cache_common.common import getLogger
from persistent_data_cache_common.configs import BasePDCConfig
from persistent_data_cache_common.events import DefaultPDCEventsDispatcher
if typing.TYPE_CHECKING:
    from ResMgr import DataSection
    from gui.game_loading import loading as gameLoading
_logger = getLogger('Manager')
PDC_CREATE_ARG = 'pdcCreate'
PDC_OFF_ARG = 'pdcOff'
PDC_CACHE_FILE_PATH = './data.wgpdc'
_eventDispatcher = None

def getEventsDispatcher():
    global _eventDispatcher
    return _eventDispatcher


def getForceCreatingParam():
    return PDC_CREATE_ARG in sys.argv


def hasPDCOffParam():
    return PDC_OFF_ARG in sys.argv


def init(scriptsConfig, engineConfig, userPreferences, gameLoadingStep):
    global _eventDispatcher
    forceCreating = getForceCreatingParam()
    clientVersion = getClientPDCVersion()
    if not clientVersion:
        _logger.error('Disabled. Broken client version.')
        if forceCreating:
            BigWorld.quitWithExitCode(ExitCode.FAILED)
        return
    settings = configs.createPDCSettings(scriptsConfig, engineConfig)
    if not forceCreating:
        if not settings.enabled or constants.IS_DEVELOPMENT and not settings.devEnabled:
            _logger.info('Disabled in config.')
            return
        if hasPDCOffParam():
            _logger.info('Disabled by the script argument.')
            return
    elif hasPDCOffParam():
        _logger.error("Can't use 'pdcCreate' and 'pdcOff' arguments simultaneously!")
        BigWorld.quitWithExitCode(ExitCode.FAILED)
        return
    _logger.debug('Settings: %s', settings)
    _eventDispatcher = DefaultPDCEventsDispatcher()
    if not forceCreating:
        faultTolerance = fault_tolerance.init(clientVersion, userPreferences)
        if faultTolerance.isLimitsReached():
            _logger.error('Disabled. Fault tolerance limits reached.')
            return
        _eventDispatcher.onFailedToLoadCachedData += faultTolerance.increaseFailedToLoadCount
        _eventDispatcher.onCachedDataLoaded += faultTolerance.resetFailedToLoadCount
        _eventDispatcher.onFailedToSaveCachedData += faultTolerance.increaseFailedToSaveCount
        _eventDispatcher.onCachedDataSaved += faultTolerance.resetFailedToSaveCount
    _eventDispatcher.onDataDeserialized += lambda name: gameLoadingStep()
    defaultCacheConfig = BasePDCConfig(version=clientVersion, cacheFilePath=PDC_CACHE_FILE_PATH)
    if forceCreating:
        cache = DefaultPDCache(defaultCacheConfig, _eventDispatcher)
        mrg = ClientForceCreatingPDCManager(cache)
    elif settings.useThread:
        cache = ThreadSavingPDCache(defaultCacheConfig, _eventDispatcher)
        mrg = DefaultPDCManager(cache)
    else:
        cache = DefaultPDCache(defaultCacheConfig, _eventDispatcher)
        mrg = DefaultPDCManager(cache)
    commonInit(mrg)


def fini():
    global _eventDispatcher
    fault_tolerance.fini()
    commonFini()
    if _eventDispatcher is not None:
        _eventDispatcher.fini()
        _eventDispatcher = None
    return


__all__ = ['init',
 'load',
 'start',
 'save',
 'fini',
 'getEventsDispatcher']
