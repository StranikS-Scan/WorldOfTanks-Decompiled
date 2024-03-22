# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/resources/cdn/cache.py
import os
import random
import itertools
import typing
import urlparse
from helpers import dependency, isPlayerAccount
from gui.game_loading import loggers
from gui.game_loading.resources.cdn import history
from gui.game_loading.resources.cdn.consts import CDN_CACHE_SYNC_TIMEOUT, DOWNLOAD_SLIDES_MULTIPLAYER, NEWBIES_BATTLES_LIMIT, SequenceOrders, SequenceCohorts
from gui.game_loading.resources.cdn.models import LocalSlideModel, CdnCacheParamsModel
from gui.game_loading.resources.cdn.config import createConfigModel
from PlayerEvents import g_playerEvents as playerEvents
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from web.cache.web_cache import BaseExternalCache, BaseExternalCacheManager, createManifestRecord, CachePrefetchResult
if typing.TYPE_CHECKING:
    from gui.game_loading.resources.cdn.types import SequenceType
    from gui.game_loading.resources.cdn.models import CdnCacheDefaultsModel, ConfigSlideModel, ConfigSequenceModel
_logger = loggers.getCdnCacheLogger()

class GameLoadingCdnCache(BaseExternalCache):
    _CACHE_DIR_NAME = 'game_loading_cache'
    _RESOURCES_SUB_DIR_NAME = 'cdn'
    _WORKERS_LIMIT = 2
    _CONFIGS_DIR_NAME = None

    def __init__(self, defaults, externalConfigUrl=None, cohort=None):
        super(GameLoadingCdnCache, self).__init__(os.path.join(self._CACHE_DIR_NAME, self._RESOURCES_SUB_DIR_NAME), self._WORKERS_LIMIT)
        self.defaults = defaults
        self._EXTERNAL_CONFIG_URL = externalConfigUrl
        self._historyDirPath = os.path.normpath(os.path.join(self.rootDirPath, self._CACHE_DIR_NAME))
        self._cohort = cohort or SequenceCohorts.DEFAULT
        self._isLoaded = False

    def load(self):
        if self._isLoaded:
            return
        super(GameLoadingCdnCache, self).load()
        self._isLoaded = True
        _logger.debug('Structure loaded.')

    def getLoaded(self):
        self.load()
        return super(GameLoadingCdnCache, self).getLoaded()

    def nextSlide(self):
        selectedSequence = self._history.selectedSequence
        return self._safeSelectSlideFromSequence(selectedSequence) or self._selectSlideFromDefaultSequence() if selectedSequence and selectedSequence.isActive else self._selectSlideFromDefaultSequence()

    @property
    def _history(self):
        return history.getOrCreateViewHistory(self._historyDirPath)

    def _selectSlideFromSequence(self, sequence):
        if not sequence:
            _logger.debug('No sequence to select slide.')
            return None
        else:
            _logger.debug('Selecting slide from sequence: %s.', sequence)
            downloadedSlides = 0
            existingSlidesByViewsCount = {}
            for slide in sequence.slides:
                if slide.isDownloaded(self):
                    viewsCount = self._history.getSequenceSlideViewsCount(sequence, slide)
                    existingSlidesByViewsCount.setdefault(viewsCount, []).append(slide)
                    downloadedSlides += 1
                _logger.debug('Sequence [%s] slide [%s] not downloaded.', sequence.name, slide)

            if downloadedSlides < sequence.minSlidesCountToView:
                _logger.debug('Sequence [%s] has not reached minimal slides count to view. [%s < %s].', sequence.name, downloadedSlides, sequence.minSlidesCountToView)
                return None
            for _viewsCount in sorted(existingSlidesByViewsCount):
                slides = existingSlidesByViewsCount[_viewsCount]
                if sequence.order == SequenceOrders.RANDOM:
                    random.shuffle(slides)
                    _logger.debug('Sequence [%s] slides with views [%s] shuffled.', sequence.name, _viewsCount)
                for _slide in slides:
                    localSlide = _slide.convertToLocal(self, self.defaults.minShowTimeSec, self.defaults.transition) if not isinstance(_slide, LocalSlideModel) else _slide
                    if localSlide:
                        self._history.addSequenceSlideViewsCount(sequence, _slide)
                        return localSlide
                    _logger.debug('Sequence [%s] slide [%s] files was deleted manually.', sequence.name, localSlide)

            return None

    def _safeSelectSlideFromSequence(self, sequence):
        try:
            return self._selectSlideFromSequence(sequence)
        except Exception:
            _logger.exception('Can not select slide from sequence: %s.', sequence.name)
            return None

        return None

    def _selectSlideFromDefaultSequence(self):
        return self._safeSelectSlideFromSequence(self.defaults.sequence)

    def _createManifest(self, config=None):
        _logger.debug('Creating manifest to download from config.')
        config = createConfigModel(config)
        if config is None:
            return
        elif not config.enabled:
            self._history.delete()
            return []
        else:
            urlsToKeepInCache = []
            prioritizedSequences = {}
            for sequence in config.sequences:
                if sequence.isActive:
                    if 0 < sequence.views <= self._history.getSequenceViewsCount(sequence):
                        _logger.debug('Sequence [%s] already watched.', sequence.name)
                        continue
                    for _slide in sequence.slides:
                        if _slide.isDownloaded(self):
                            urlsToKeepInCache += _slide.urls

                    if sequence.cohorts != SequenceCohorts.getDefaults() and self._cohort not in sequence.cohorts:
                        _logger.debug('Sequence [%s] skipped be cohort: %s.', sequence.name, self._cohort)
                        continue
                    prioritizedSequences.setdefault(sequence.priority, []).append(sequence)
                self._history.removeSequenceFromHistory(sequence)

            toDownloadUrls = []
            if prioritizedSequences:
                selectedSequence = random.choice(prioritizedSequences[max(prioritizedSequences)])
                self._history.selectSequence(selectedSequence)
                notDownloadedUrls, notViewedSlidesCount = [], 0
                for slide in selectedSequence.slides:
                    if not slide.isDownloaded(self):
                        notDownloadedUrls.append(slide.urls)
                    _logger.debug('Sequence [%s] slide [%s] already downloaded.', selectedSequence.name, slide)
                    if not self._history.getSequenceSlideViewsCount(selectedSequence, slide):
                        _logger.debug('Sequence [%s] slide [%s] not viewed.', selectedSequence.name, slide)
                        notViewedSlidesCount += 1

                if notDownloadedUrls:
                    maxSlidesCount = selectedSequence.minSlidesCountToView * DOWNLOAD_SLIDES_MULTIPLAYER
                    slidesCount = min(max(maxSlidesCount - notViewedSlidesCount, 0), len(notDownloadedUrls))
                    if selectedSequence.order == SequenceOrders.RANDOM:
                        toDownloadUrls = random.sample(notDownloadedUrls, slidesCount)
                    else:
                        toDownloadUrls = notDownloadedUrls[:slidesCount]
                _logger.debug('Sequence [%s] slide [%s] to download.', selectedSequence.name, len(toDownloadUrls))
            else:
                self._history.deleteSelectedSequence()
                _logger.debug('No sequences to select from.')
            toDownloadByHosts = {}
            for url in set(urlsToKeepInCache + list(itertools.chain(*toDownloadUrls))):
                parsedUrl = urlparse.urlparse(url)
                host = urlparse.urlunsplit((parsedUrl.scheme,
                 parsedUrl.netloc,
                 '',
                 '',
                 ''))
                toDownloadByHosts.setdefault(host, []).append(parsedUrl.path)

            return [ createManifestRecord(appName='slides', host=host, files=relativeUrls) for host, relativeUrls in toDownloadByHosts.iteritems() ]


class GameLoadingCdnCacheMgr(BaseExternalCacheManager):
    _REQUEST_TIMEOUT = CDN_CACHE_SYNC_TIMEOUT
    _DEFAULT_SYNC_TIMEOUT = _REQUEST_TIMEOUT

    def __init__(self, defaults):
        super(GameLoadingCdnCacheMgr, self).__init__()
        self._itemsCache = None
        self._lobbyCtx = None
        self._cacheParams = CdnCacheParamsModel()
        self._downloadResult = None
        self._defaults = defaults
        return

    def destroy(self):
        self.onDisconnected()
        super(GameLoadingCdnCacheMgr, self).destroy()
        history.saveViewHistory()

    def stopSync(self, *args, **kwargs):
        self._destroyCache()

    def onConnected(self):
        playerEvents.onAccountBecomeNonPlayer += self.stopSync
        playerEvents.onAccountShowGUI += self._tryToDownload
        self._itemsCache = dependency.instance(IItemsCache)
        self._itemsCache.onSyncCompleted += self._onItemsCacheUpdated
        self._lobbyCtx = dependency.instance(ILobbyContext)
        self._lobbyCtx.onServerSettingsChanged += self._onServerSettingsChanged
        self._lobbyCtx.getServerSettings().onServerSettingsChange += self._onServerSettingsUpdated
        _logger.debug('On connected called: items=%s, lobby=%s.', self._itemsCache, self._lobbyCtx)

    def onDisconnected(self):
        self.stopSync()
        self._downloadResult = None
        self._cacheParams.reset()
        playerEvents.onAccountShowGUI -= self._tryToDownload
        playerEvents.onAccountBecomeNonPlayer -= self.stopSync
        if self._itemsCache:
            self._itemsCache.onSyncCompleted -= self._onItemsCacheUpdated
        self._itemsCache = None
        if self._lobbyCtx:
            self._lobbyCtx.getServerSettings().onServerSettingsChange -= self._onServerSettingsUpdated
            self._lobbyCtx.onServerSettingsChanged -= self._onServerSettingsChanged
        self._lobbyCtx = None
        _logger.debug('On disconnected called.')
        return

    def nextSlide(self):
        self.load()
        if self._cache is None:
            _logger.warning('Can not load cache to select slide.')
            return
        else:
            return self._cache.nextSlide()

    def _tryToDownload(self, *args, **kwargs):
        if self._downloadResult == CachePrefetchResult.SUCCESS:
            _logger.debug('Already synced.')
            return
        if not self._cacheParams.isReady:
            _logger.debug('Not ready to sync yet.')
            return
        if not isPlayerAccount():
            _logger.warning('Can not sync while not in hangar.')
            return
        _logger.debug('Downloading cdn resources.')
        self.sync(self._onSynced)

    def _createCache(self):
        if self._cacheParams.isReady:
            _logger.debug('Selecting web cache.')
            return GameLoadingCdnCache(self._defaults, externalConfigUrl=self._cacheParams.configUrl, cohort=self._cacheParams.cohort)
        else:
            _logger.debug('Selecting static cache.')
            return GameLoadingCdnCache(self._defaults, externalConfigUrl=None, cohort=None)

    def _onSynced(self, result):
        self._downloadResult = result
        _logger.debug('Got sync result: [%s].', result)

    def _onItemsCacheUpdated(self, *args, **kwargs):
        if self._cacheParams.isItemsCacheParamsReady:
            return
        cohort = self._getCohort()
        if cohort:
            self._cacheParams.cohort = cohort
            _logger.debug('[ItemsCache] Cohort: %s selected.', cohort)
            self._tryToDownload()

    def _onServerSettingsChanged(self, *args, **kwargs):
        self._lobbyCtx.getServerSettings().onServerSettingsChange += self._onServerSettingsUpdated

    def _onServerSettingsUpdated(self, *args, **kwargs):
        if self._cacheParams.isServerSettingsParamsReady:
            return
        configUrl = self._getExternalConfigUrl()
        if configUrl:
            self._cacheParams.configUrl = configUrl
            _logger.debug('[ServerSettings] config url: %s selected.', configUrl)
            self._tryToDownload()

    def _getCohort(self):
        if self._itemsCache is None or not self._itemsCache.isSynced():
            _logger.debug('ItemCache service not synced.')
            return
        else:
            battlesCount = self._itemsCache.items.getAccountDossier().getTotalStats().getBattlesCount()
            return SequenceCohorts.NEWBIES if battlesCount < NEWBIES_BATTLES_LIMIT else SequenceCohorts.DEFAULT

    def _getExternalConfigUrl(self):
        if self._lobbyCtx is None:
            _logger.debug('Lobby context service not created yet.')
            return
        else:
            url = self._lobbyCtx.getServerSettings().fileServer.getGameLoadingConfigUrl()
            if not url:
                _logger.debug('External url not configured yet.')
                return
            return url
