# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wot_plus/service_record_customization/cdn_cache.py
from __future__ import absolute_import
import logging
import os
import typing
from future.moves.urllib import parse as urlparse
from future.utils import viewitems
import ResMgr
from gui.game_control.wot_plus.service_record_customization import _updateConfig, getConfig, IResourceCacheManager
from helpers import dependency, getClientLanguage
from skeletons.gui.lobby_context import ILobbyContext
from web.cache.web_cache import BaseExternalCache, CachePrefetchResult, createManifestRecord, BaseExternalCacheManager
if typing.TYPE_CHECKING:
    from typing import Any, Optional, List, Dict, Tuple
    from gui.game_control.wot_plus.service_record_customization.models import ConfigModel, RibbonModel, BackgroundModel
_logger = logging.getLogger(__name__)

class ServiceRecordCustomizationCache(BaseExternalCache):
    _lobbyCtx = dependency.descriptor(ILobbyContext)
    _langCode = getClientLanguage()
    _CONFIGS_DIR_NAME = 'config'

    def __init__(self, cacheName, workersLimit):
        super(ServiceRecordCustomizationCache, self).__init__(cacheName, workersLimit)
        fileServer = self._lobbyCtx.getServerSettings().fileServer
        self._EXTERNAL_CONFIG_URL = fileServer.getServiceRecordCustomizationRootUrl()

    def _processFailedManifest(self):
        try:
            self._restoreManifestFromLocalConfig()
        except Exception as ex:
            _logger.exception('Failed to restore manifest, %s', exc_info=ex)
            self._prefetchEnd(CachePrefetchResult.FAIL)

    def _onManifestDownloadFailed(self):
        self._processFailedManifest()

    def _onManifestParsingFailed(self):
        self._processFailedManifest()

    def _getHostAndPathFromURL(self, url):
        parsedUrl = urlparse.urlparse(url)
        host = urlparse.urlunsplit((parsedUrl.scheme,
         parsedUrl.netloc,
         '',
         '',
         ''))
        return (host, parsedUrl.path)

    def _restoreManifestFromLocalConfig(self):
        _logger.info('SRC manifest download failed. Trying to recover local manifest')
        import json
        configFiles = self._storage.getApp(self._CONFIGS_DIR_NAME).getAll()
        if len(configFiles) != 1:
            _logger.warning('SRC local manifest is not loaded to the storage. Going to use static fallback')
            self._prefetchEnd(CachePrefetchResult.FAIL)
            return
        else:
            configPath = os.path.normpath(self.getLoaded().get(configFiles[0]))
            if configPath is None:
                _logger.warning('SRC local manifest is missed (probably removed from the disk). Going to use static fallback')
                self._prefetchEnd(CachePrefetchResult.FAIL)
                return
            section = ResMgr.openSection(configPath).asString
            rawConfig = json.loads(section)
            if rawConfig is None:
                _logger.warning('SRC local manifest cannot be read. Going to use static fallback')
                self._prefetchEnd(CachePrefetchResult.FAIL)
                return
            _updateConfig(rawConfig, self)
            _logger.info('SRC local manifest is recovered')
            self._prefetchEnd(CachePrefetchResult.SUCCESS)
            return

    def _createManifest(self, config=None):
        if config is None:
            _logger.info("The config is not set, manifest won't be updated")
            return
        else:
            parsedConfig = _updateConfig(config, self)
            toDownloadByHosts = {}
            localizationToDownloadByHosts = {}
            for background in parsedConfig.backgrounds:
                host, path = self._getHostAndPathFromURL(background.url)
                toDownloadByHosts.setdefault(host, []).append(path)
                host, path = self._getHostAndPathFromURL(background.localization)
                localizationToDownloadByHosts.setdefault(host, []).append(path)

            backgroundsManifest = [ createManifestRecord(appName='backgrounds', host=host, files=relativeUrls) for host, relativeUrls in viewitems(toDownloadByHosts) ]
            backgroundLozalisationManifest = [ createManifestRecord(appName='localization', host=host, files=relativeUrls) for host, relativeUrls in viewitems(localizationToDownloadByHosts) ]
            toDownloadByHosts.clear()
            for ribbonPath in parsedConfig.ribbonURLs:
                parsedUrl = urlparse.urlparse(ribbonPath)
                host = urlparse.urlunsplit((parsedUrl.scheme,
                 parsedUrl.netloc,
                 '',
                 '',
                 ''))
                toDownloadByHosts.setdefault(host, []).append(parsedUrl.path)

            ribbonsManifest = [ createManifestRecord(appName='ribbons', host=host, files=relativeUrls) for host, relativeUrls in viewitems(toDownloadByHosts) ]
            return backgroundsManifest + ribbonsManifest + backgroundLozalisationManifest


class CdnResourcesCacheManager(BaseExternalCacheManager, IResourceCacheManager):
    _REQUEST_TIMEOUT = 60
    _CDN_WORKERS = 2
    _CDN_CACHE_DIR = 'service_record_cache'

    def getRibbons(self):
        return getConfig().ribbons

    def getBackgrounds(self):
        return getConfig().backgrounds

    def getDownloadedBackgrounds(self):
        return [ background for background in self.getBackgrounds() if background.isDownloaded() ]

    def getDownloadedRibbons(self):
        return [ ribbon for ribbon in self.getRibbons() if ribbon.isDownloaded() ]

    def getDownloadedBackgroundIDs(self):
        return [ background.id for background in self.getBackgrounds() if background.isDownloaded() ]

    def getDownloadedRibbonIDs(self):
        return [ ribbon.id for ribbon in self.getRibbons() if ribbon.isDownloaded() ]

    def getConfigModel(self):
        config = getConfig()
        if config is None:
            raise Exception('The SRC cache config is not initialized yet.')
        return getConfig()

    def isCacheReady(self):
        config = getConfig()
        return config is not None and len(self.getDownloadedRibbons()) > 0 and len(self.getDownloadedBackgrounds()) > 0

    def getBackground(self, id_):
        background = self.getConfigModel().getBackground(id_)
        if background is None:
            _logger.warning('Could not find background %s in cache, returning first background instead', id_)
            background = self.getDownloadedBackgrounds()[0]
        return background

    def getRibbon(self, id_):
        ribbon = self.getConfigModel().getRibbon(id_)
        if ribbon is None:
            _logger.warning('Could not find ribbon %s in cache, returning first ribbon instead', id_)
            ribbon = self.getDownloadedRibbons()[0]
        return ribbon

    def registerCaller(self, caller, timeout):
        timeout = timeout or self._REQUEST_TIMEOUT
        self._registerCaller(caller, timeout)

    def _createCache(self):
        return ServiceRecordCustomizationCache(self._CDN_CACHE_DIR, self._CDN_WORKERS)
