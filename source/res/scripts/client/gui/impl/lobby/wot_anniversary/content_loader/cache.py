# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/content_loader/cache.py
import logging
import time
import typing
import ResMgr
from BWUtil import AsyncReturn
from gui.impl.lobby.wot_anniversary.content_loader.config import makeContentConfig
from gui.impl.lobby.wot_anniversary.content_loader.models import BackgroundContent, DayContent, VIDEOS_CONTENT_NAME, VideosContent
from gui.impl.lobby.wot_anniversary.content_loader.url_utils import makeUrlFromParts
from gui.impl.utils.path import normalizeGfImagePath, normalizeGfVideoPath
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.wot_anniversary import IWotAnniversaryController
from web.cache.web_cache import BaseExternalCache, BaseExternalCacheManager, createManifestRecord, CachePrefetchResult
from wg_async import AsyncEvent, wg_async, wg_await
if typing.TYPE_CHECKING:
    from typing import Any, Dict, List, Optional, Union
    from gui.impl.lobby.wot_anniversary.content_loader.config import ContentConfig, DayConfig, BackgroundConfig
_logger = logging.getLogger(__name__)

class WotAnniversaryCdnCache(BaseExternalCache):
    __wotAnniversaryController = dependency.descriptor(IWotAnniversaryController)
    __CDN_CACHE_DIR = 'wot_anniversary_cache'
    __CDN_WORKERS = 16
    __CONTENT_PATH_TEMPLATE = 'wot_anniversary_content_config.json?{}'

    def __init__(self, externalConfigHost):
        self._EXTERNAL_CONFIG_URL = makeUrlFromParts(externalConfigHost, self.__CONTENT_PATH_TEMPLATE.format(time.time()))
        self.__host = externalConfigHost
        self.__config = None
        self.__content = None
        super(WotAnniversaryCdnCache, self).__init__(self.__CDN_CACHE_DIR, self.__CDN_WORKERS)
        return

    @property
    def config(self):
        return self.__config

    def isContentLoaded(self, validate=True):
        if self.config is None:
            _logger.error('Content Config is not initialized.')
            return False
        else:
            if validate:
                self.__content = self.__validateContent()
            return self.__content is not None

    def getContentByDayID(self, dayID):
        if self.config is None:
            _logger.error('Content Config is not initialized.')
            return
        else:
            dayConfig = findFirst(lambda dc: int(dc.id) == dayID, self.config.days)
            if dayConfig is None:
                _logger.error('Can not find the DayConfig by dayId = %s', dayID)
                return
            return self.__createDayContent(dayConfig)

    def getAlbumContent(self):
        return None if not self.isContentLoaded() else self.__content

    def _prepareToUpdate(self, config=None, manifest=None):
        self.__config = makeContentConfig(config)
        super(WotAnniversaryCdnCache, self)._prepareToUpdate(config=self.__config, manifest=manifest)

    def _createManifest(self, config=None):
        _logger.debug('Creating manifest to download from config.')
        toDownloadDayCount = self.__wotAnniversaryController.getReleasedEnvelopCount()
        contentToDownloadUrls = []
        videoToDownloadUrls = [ v for v in config.videos ] if config.videos is not None else []
        for day in config.days:
            if int(day.id) <= toDownloadDayCount:
                contentToDownloadUrls.extend([day.image, day.imageLarge, day.localizations])
                videoToDownloadUrls.append(day.video)

        for bg in config.backgrounds:
            contentToDownloadUrls.extend([bg.small,
             bg.medium,
             bg.large,
             bg.extraLarge])

        return [createManifestRecord(appName='content', host=self.__host, files=contentToDownloadUrls), createManifestRecord(appName='webmvideo', host=self.__host, files=videoToDownloadUrls)]

    def __validateContent(self):
        toDownloadDayCount = self.__wotAnniversaryController.getReleasedEnvelopCount()
        if len(self.config.days) < toDownloadDayCount:
            _logger.error('Content Config does not have all needed files. config=%s, toDownloadDayCount=%s', self.config, toDownloadDayCount)
            return
        content = {bg.id:BackgroundContent(*[ self.__getGFImagePath(f) for f in (bg.small,
         bg.medium,
         bg.large,
         bg.extraLarge) ]) for bg in self.config.backgrounds}
        content.update({d.id:self.__createDayContent(d) for d in self.config.days if int(d.id) <= toDownloadDayCount})
        if self.config.videos is not None:
            content[VIDEOS_CONTENT_NAME] = VideosContent(*[ self.__getGFVideoPath(f) for f in (self.config.videos.conversionOneEnv,
             self.config.videos.conversionTwoEnvs,
             self.config.videos.conversionThreeEnvs,
             self.config.videos.turnPage) ])
        if not all([ c.isContentLoaded() for c in content.values() ]):
            _logger.info('Content is not downloaded for all needed days.')
            return
        else:
            return content

    def __getGFImagePath(self, url):
        return normalizeGfImagePath(self.getRelativePath(makeUrlFromParts(self.__host, url)))

    def __getGFVideoPath(self, url):
        return normalizeGfVideoPath(self.get(makeUrlFromParts(self.__host, url), appName='webmvideo'))

    def __createDayContent(self, dayConfig):
        localizationPath = self.get(makeUrlFromParts(self.__host, dayConfig.localizations))
        return DayContent(self.__getGFImagePath(dayConfig.image), self.__getGFImagePath(dayConfig.imageLarge), ResMgr.openSection(localizationPath) if localizationPath is not None else None, self.__getGFVideoPath(dayConfig.video))


class WotAnniversaryCdnCacheMgr(BaseExternalCacheManager):
    __wotAnniversaryController = dependency.descriptor(IWotAnniversaryController)
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    _REQUEST_TIMEOUT = 1200.0
    _DEFAULT_SYNC_TIMEOUT = 1260.0
    _MAX_RETRY_COUNT = 3

    def __init__(self):
        super(WotAnniversaryCdnCacheMgr, self).__init__()
        self._cache = None
        self.__downloadResult = None
        self.__downloadEvent = None
        return

    def startSync(self):
        if self.__downloadEvent is None:
            self.__downloadEvent = AsyncEvent()
        self.__tryToDownload()
        return

    def reload(self):
        if self._cache is None:
            return
        else:
            self.__tryToDownload()
            return

    def stopSync(self):
        self.__downloadEvent = None
        self.__downloadResult = None
        self._destroyCache()
        return

    def isSynced(self):
        return self.__downloadEvent is not None and self.__downloadEvent.is_set() and self.__downloadResult == CachePrefetchResult.SUCCESS and self._cache is not None and self._cache.isContentLoaded()

    @wg_async
    def waitSync(self):
        if not self.isSynced():
            self.__tryToDownload()
        result = yield wg_await(self.__downloadEvent.wait())
        raise AsyncReturn(result)

    def getContentByDayID(self, dayID):
        return self._cache.getContentByDayID(dayID)

    def getAlbumContent(self):
        return self._cache.getAlbumContent()

    def _createCache(self):
        return WotAnniversaryCdnCache(self.__wotAnniversaryController.config.contentConfigUrl)

    def __tryToDownload(self):
        if self.isSyncing:
            return
        self.__downloadEvent.clear()
        _logger.debug('[WorAnniversary] Trying to download content.')
        self.sync(self.__onSynced)

    def __onSynced(self, result):
        self.__downloadResult = result
        if self.__downloadEvent is not None:
            _logger.debug('[WorAnniversary] Sync of cache is completed. Result=%s', result)
            self.__downloadEvent.set()
        return
