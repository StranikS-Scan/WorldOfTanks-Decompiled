# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus/service_record_customization/__init__.py
from __future__ import absolute_import
import logging
import typing
from gui.game_control.wot_plus.service_record_customization.models import createConfigModel, createLocalConfigModel
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, List, Callable, Union
    from gui.game_control.wot_plus.service_record_customization.models import ConfigModel, BackgroundModel, RibbonModel
    from gui.game_control.wot_plus.service_record_customization.cdn_cache import ServiceRecordCustomizationCache

class IResourceCacheManager(object):

    def getRibbons(self):
        raise NotImplementedError

    def getBackgrounds(self):
        raise NotImplementedError

    def getDownloadedBackgrounds(self):
        raise NotImplementedError

    def getDownloadedRibbons(self):
        raise NotImplementedError

    def getConfigModel(self):
        raise NotImplementedError

    def isCacheReady(self):
        raise NotImplementedError

    def getBackground(self, id_):
        raise NotImplementedError

    def getRibbon(self, id_):
        raise NotImplementedError

    def getDownloadedBackgroundIDs(self):
        raise NotImplementedError

    def getDownloadedRibbonIDs(self):
        raise NotImplementedError

    def registerCaller(self, caller, timeout):
        raise NotImplementedError


_g_config = None

def getConfig():
    global _g_config
    return _g_config


def _updateConfig(config, cache, local=False):
    global _g_config
    if _g_config is None and config is not None:
        if local:
            _g_config = createLocalConfigModel(config)
        else:
            _g_config = createConfigModel(config)
            if _g_config is None:
                raise Exception('Config model for service record customization cannot is not initialized')
            _g_config.setFileCache(cache)
    return _g_config
