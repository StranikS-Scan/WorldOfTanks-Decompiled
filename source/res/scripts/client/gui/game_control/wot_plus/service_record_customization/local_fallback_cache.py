# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus/service_record_customization/local_fallback_cache.py
from __future__ import absolute_import
import typing
from gui.game_control.wot_plus.service_record_customization import _updateConfig, getConfig, IResourceCacheManager
from gui.impl import backport
from gui.impl.gen import R
from web.cache.web_cache import CachePrefetchResult
if typing.TYPE_CHECKING:
    from typing import Optional, List
    from gui.game_control.wot_plus.service_record_customization.models import BackgroundModel, RibbonModel, ConfigModel
fallbackModel = {'ribbons': [{'id': 0,
              'name': 'red',
              'urls': {'base': backport.image(R.images.gui.maps.icons.achievements.summary.src_fallback.red()),
                       'icon': backport.image(R.images.gui.maps.icons.achievements.summary.src_fallback.red_icon()),
                       'small': backport.image(R.images.gui.maps.icons.achievements.summary.src_fallback.red_small()),
                       'large': backport.image(R.images.gui.maps.icons.achievements.summary.src_fallback.red_large())}}],
 'backgrounds': [{'id': 0,
                  'name': 'default',
                  'url': backport.image(R.images.gui.maps.icons.achievements.summary.src_fallback.default()),
                  'localization': ''}]}

class LocalResourceCacheManager(IResourceCacheManager):

    @property
    def isSyncing(self):
        return False

    def registerCaller(self, caller):
        caller(CachePrefetchResult.SUCCESS)

    def sync(self, callback=None, timeout=None):
        self._createCache()
        if callback is not None and callable(callback):
            callback(CachePrefetchResult.SUCCESS)
        return

    def getRibbons(self):
        return getConfig().ribbons

    def getBackgrounds(self):
        return getConfig().backgrounds

    def getDownloadedBackgrounds(self):
        return [ background for background in self.getBackgrounds() if background.isDownloaded() ]

    def getDownloadedRibbons(self):
        return [ ribbon for ribbon in self.getRibbons() if ribbon.isDownloaded() ]

    def getConfigModel(self):
        config = getConfig()
        if config is None:
            raise Exception('The SRC cache config is not initialized yet.')
        return getConfig()

    def isSynced(self):
        return True

    def isCacheReady(self):
        return True

    def getBackground(self, id_):
        return self.getBackgrounds()[0]

    def getRibbon(self, id_):
        return self.getRibbons()[0]

    def getDownloadedBackgroundIDs(self):
        return [ background.id for background in self.getBackgrounds() if background.isDownloaded() ]

    def getDownloadedRibbonIDs(self):
        return [ ribbon.id for ribbon in self.getRibbons() if ribbon.isDownloaded() ]

    def _createCache(self):
        _updateConfig(fallbackModel, None, True)
        return
