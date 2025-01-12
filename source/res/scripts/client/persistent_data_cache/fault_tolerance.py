# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/persistent_data_cache/fault_tolerance.py
import typing
from persistent_data_cache_common.common import getLogger
from helpers import base64_utils
from PlayerEvents import g_playerEvents as playerEvents
from uilogging.persistent_data_cache.loggers import PDCFaultToleranceLogger
if typing.TYPE_CHECKING:
    from ResMgr import DataSection
    from persistent_data_cache_common.types import TPDCVersion
_logger = getLogger('FaultTolerance')
_PREFS_NAME = 'pdcFaultTolerance'
_VERSION_KEY = 'version'
_FAILED_TO_LOAD_COUNT_KEY = 'failedToLoadCount'
_FAILED_TO_SAVE_COUNT_KEY = 'failedToSaveCount'
_FAILED_TO_LOAD_COUNT_LIMIT = 5
_FAILED_TO_SAVE_COUNT_LIMIT = 5

def _loadData(version, userPrefs):
    data, modified = {}, False
    if userPrefs.has_key(_PREFS_NAME):
        unpacked = base64_utils.unpack(userPrefs[_PREFS_NAME].asString, default=None)
        if isinstance(unpacked, dict):
            _logger.debug('Data has been loaded from preferences.')
            prefVersion = unpacked.pop(_VERSION_KEY, None)
            if prefVersion is None or prefVersion != version:
                modified, unpacked = True, {}
                _logger.debug('Version of preferences changed. <%s> != <%s>.', prefVersion, version)
            data = unpacked
        else:
            _logger.warning('Failed to load data from preferences.')
            modified = True
    return (data, modified)


class FaultTolerance(object):
    __slots__ = ('_lastErrors', '_userPrefs', '_data', '_version', '_modified')

    def __init__(self, version, userPrefs):
        self._version = version
        self._userPrefs = userPrefs
        self._data, self._modified = _loadData(self._version, self._userPrefs)
        self._lastErrors = {}
        playerEvents.onUILoggingStarted += self._sendLastErrors
        _logger.debug('Initialized. <version==%s, modified=%s, data=%s>.', self._version, self._modified, self._data)

    def isLimitsReached(self):
        failedToLoadCount = self._data.get(_FAILED_TO_LOAD_COUNT_KEY, 0)
        failedToSaveCount = self._data.get(_FAILED_TO_SAVE_COUNT_KEY, 0)
        return failedToLoadCount >= _FAILED_TO_LOAD_COUNT_LIMIT or failedToSaveCount >= _FAILED_TO_SAVE_COUNT_LIMIT

    def increaseFailedToLoadCount(self, error):
        self._increaseCount(_FAILED_TO_LOAD_COUNT_KEY)
        self._lastErrors[_FAILED_TO_LOAD_COUNT_KEY] = error

    def resetFailedToLoadCount(self):
        self._resetCount(_FAILED_TO_LOAD_COUNT_KEY)

    def increaseFailedToSaveCount(self, error):
        self._increaseCount(_FAILED_TO_SAVE_COUNT_KEY)
        self._lastErrors[_FAILED_TO_SAVE_COUNT_KEY] = error

    def resetFailedToSaveCount(self):
        self._resetCount(_FAILED_TO_SAVE_COUNT_KEY)

    def fini(self):
        if self._modified and self._userPrefs is not None:
            if self._data:
                data = {_VERSION_KEY: self._version}
                data.update(self._data)
                packed = base64_utils.pack(data)
                if packed is not None:
                    self._userPrefs.write(_PREFS_NAME, packed)
                    _logger.debug('Data has been saved. <%s>.', data)
                else:
                    _logger.error('Data has not been saved.')
            else:
                _logger.debug('Nothing to save.')
                if self._userPrefs.has_key(_PREFS_NAME):
                    self._userPrefs.deleteSection(_PREFS_NAME)
        self._userPrefs = None
        self._modified = False
        playerEvents.onUILoggingStarted -= self._sendLastErrors
        self._lastErrors.clear()
        _logger.debug('Finalized.')
        return

    def _resetCount(self, key):
        if key in self._data:
            self._data.pop(key, None)
            self._modified = True
            _logger.debug('Count <%s> value has been deleted.', key)
        return

    def _increaseCount(self, key):
        count = self._data.get(key, 0) + 1
        self._data[key] = count
        self._modified = True
        _logger.debug('Count <%s> value changed to <%s>.', key, count)

    def _sendLastErrors(self):
        if self._lastErrors:
            errors = {eType:(self._data.get(eType, 0), error) for eType, error in self._lastErrors.iteritems()}
            self._lastErrors.clear()
            _logger.debug('Sending last errors to logging service. <%s>.', errors)
            PDCFaultToleranceLogger().logErrors(errors)


_g_faultTolerance = None

def init(version, userPrefs):
    global _g_faultTolerance
    if _g_faultTolerance is not None:
        _logger.error('Already initialized.')
        return _g_faultTolerance
    else:
        _g_faultTolerance = FaultTolerance(version, userPrefs)
        return _g_faultTolerance


def fini():
    global _g_faultTolerance
    if _g_faultTolerance is None:
        _logger.debug('Not initialized.')
        return
    else:
        _g_faultTolerance.fini()
        _g_faultTolerance = None
        return
