# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus/service_record_customization/service_record_customization.py
from __future__ import absolute_import
import logging
from functools import partial
import typing
import BigWorld
from gui.game_control.wot_plus.service_record_customization.cdn_cache import CdnResourcesCacheManager
from gui.game_control.wot_plus.service_record_customization.local_fallback_cache import LocalResourceCacheManager
from gui.shared.gui_items.processors import Processor
from gui.shared.gui_items.processors.plugins import SyncValidator, makeSuccess, makeError
from gui.shared.utils.decorators import adisp_async
from helpers import dependency
from skeletons.gui.game_control import IWotPlusController
from web.cache.web_cache import CachePrefetchResult, CacheStates
from gui.shared.gui_items.processors.plugins import PluginResult
if typing.TYPE_CHECKING:
    from typing import Optional, Callable, List
    from gui.game_control.wot_plus.service_record_customization.models import BackgroundModel, RibbonModel
_logger = logging.getLogger(__name__)

class _HasWotPlusValidator(SyncValidator):
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)

    def _validate(self):
        return makeSuccess() if self._wotPlusCtrl.hasSubscription() else makeError('Player has no WotPlus subscription')


class _IsSRCustomizationEnabledValidator(SyncValidator):
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)

    def _validate(self):
        return makeSuccess() if self._wotPlusCtrl.getSettingsStorage().isServiceRecordCustomizationAvailable() else makeError('WotPlus service record customization is disabled')


class _AssetExistenceValidator(SyncValidator):

    def __init__(self, optionsList, option, isEnabled=True):
        super(_AssetExistenceValidator, self).__init__(isEnabled)
        self._optionsList = optionsList
        self._option = option

    def _validate(self):
        return makeError("Option '{}' is not found in options list".format(self._option)) if self._option not in self._optionsList else makeSuccess()


class ServiceRecordProcessor(Processor):
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)

    def __init__(self, backgroundID, ribbonID):
        _cache = self._wotPlusCtrl.getSRCAssetManager()
        self._ribbonID = ribbonID
        self._backgroundID = backgroundID
        plugins = [_HasWotPlusValidator(),
         _IsSRCustomizationEnabledValidator(),
         _AssetExistenceValidator(_cache.getDownloadedRibbonIDs(), ribbonID),
         _AssetExistenceValidator(_cache.getDownloadedBackgroundIDs(), backgroundID)]
        super(ServiceRecordProcessor, self).__init__(plugins)

    def _request(self, callback):
        BigWorld.player().setServiceRecordCustomizations(self._ribbonID, self._backgroundID, lambda code, errStr: self._response(code, callback, errStr=errStr))


class ServiceRecordAssetManager(object):

    def __init__(self):
        self._cdnCache = None
        self._localCache = None
        self._currentCache = None
        return

    def init(self, useCdnResourceCache=True, autoSync=True):
        self._cdnCache = CdnResourcesCacheManager()
        self._localCache = LocalResourceCacheManager()
        self._currentCache = self._cdnCache if useCdnResourceCache else self._localCache
        if autoSync:
            self.sync(lambda result: result)

    def clear(self):
        if self._cdnCache is not None:
            self._cdnCache.destroy()
        self._cdnCache = None
        self._localCache = None
        return

    def getBackground(self, id_):
        return self._currentCache.getBackground(id_)

    def getRibbon(self, id_):
        return self._currentCache.getRibbon(id_)

    def getDownloadedRibbons(self):
        return self._currentCache.getDownloadedRibbons()

    def getDownloadedBackgrounds(self):
        return self._currentCache.getDownloadedBackgrounds()

    def getDownloadedBackgroundIDs(self):
        return self._currentCache.getDownloadedBackgroundIDs()

    def getDownloadedRibbonIDs(self):
        return self._currentCache.getDownloadedRibbonIDs()

    def isSyncing(self):
        return self._currentCache.isSyncing

    def isUsingOfflineMode(self):
        return self._currentCache == self._localCache

    @adisp_async
    def sync(self, callback=None, timeout=None):
        if self._currentCache.isSyncing:
            self._currentCache.registerCaller(partial(self._onSyncFinished, callback), timeout)
            return
        elif self._currentCache.isSynced:
            if callback is not None and callable(callback):
                callback(CacheStates.SYNCED)
            return
        else:
            self._currentCache.sync(partial(self._onSyncFinished, callback), timeout)
            return

    def _onSyncFinished(self, callback, result):
        _logger.info('Service record sync finished with result %s', result)
        if result != CachePrefetchResult.SUCCESS:
            if not self._currentCache.isCacheReady():
                _logger.info('Service record res manager could not download or recreate manifest, it will switch to local fallback cache')
                self._localCache.sync(lambda x: x)
                self._currentCache = self._localCache
        if callback is not None and callable(callback):
            callback(result)
        return
