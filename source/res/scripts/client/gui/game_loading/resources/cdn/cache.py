# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/resources/cdn/cache.py
import os
import random
import itertools
import typing
import urlparse
from constants import MAX_VEHICLE_LEVEL, BATTLE_MODE_VEHICLE_TAGS
from helpers import dependency, isPlayerAccount
from gui.game_loading import loggers
from gui.game_loading.resources.cdn import history
from gui.game_loading.resources.cdn.consts import CDN_CACHE_SYNC_TIMEOUT, DOWNLOAD_SLIDES_MULTIPLAYER, SequenceOrders, SequenceCohorts
from gui.game_loading.resources.cdn.models import LocalSlideModel, CdnCacheParams
from gui.game_loading.resources.cdn.config import createConfigModel
from PlayerEvents import g_playerEvents as playerEvents
from bootcamp.BootCampEvents import g_bootcampEvents as bootcampPlayerEvents
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from web.cache.web_cache import BaseExternalCache, BaseExternalCacheManager, createManifestRecord, CachePrefetchResult
if typing.TYPE_CHECKING:
    from gui.game_loading.resources.cdn.types import SequenceType
    from gui.game_loading.resources.cdn.models import CdnCacheDefaultsModel, ConfigSlideModel, ConfigSequenceModel, NewbiesCohortSettingsModel

def _getNewbieVehicleCriteria(level):
    from gui.shared.utils.requesters import REQ_CRITERIA
    criteria = REQ_CRITERIA.INVENTORY
    criteria |= REQ_CRITERIA.VEHICLE.LEVELS(range(level, MAX_VEHICLE_LEVEL + 1))
    criteria |= ~REQ_CRITERIA.VEHICLE.RENT
    criteria |= ~REQ_CRITERIA.SECRET
    criteria |= ~REQ_CRITERIA.VEHICLE.HAS_ANY_TAG(BATTLE_MODE_VEHICLE_TAGS)
    return criteria


_logger = loggers.getCdnCacheLogger()

class GameLoadingCdnCache(BaseExternalCache):
    _CACHE_DIR_NAME = 'game_loading_cache_mt'
    _RESOURCES_SUB_DIR_NAME = 'cdn'
    _WORKERS_LIMIT = 2
    _CONFIGS_DIR_NAME = None

    def __init__(self, defaults, externalConfigUrl=None, itemsCache=None):
        super(GameLoadingCdnCache, self).__init__(os.path.join(self._CACHE_DIR_NAME, self._RESOURCES_SUB_DIR_NAME), self._WORKERS_LIMIT)
        self.defaults = defaults
        self._EXTERNAL_CONFIG_URL = externalConfigUrl
        self._historyDirPath = os.path.normpath(os.path.join(self.rootDirPath, self._CACHE_DIR_NAME))
        self._itemsCache = itemsCache
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
            cohort = self._resolveCohort(config.newbiesCohort)
            _logger.debug('Resolved player cohort: %s.', cohort)
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

                    if sequence.cohorts != SequenceCohorts.getDefaults() and cohort not in sequence.cohorts:
                        _logger.debug('Sequence [%s] skipped be cohort: %s.', sequence.name, cohort)
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

    def _resolveCohort(self, newbiesSettings):
        if self._itemsCache is None or not self._itemsCache.isSynced():
            _logger.debug('ItemsCache service not synced, fallback to default cohort.')
            return SequenceCohorts.DEFAULT
        else:
            return SequenceCohorts.NEWBIES if self._isNewbie(newbiesSettings) else SequenceCohorts.DEFAULT

    def _isNewbie(self, newbiesSettings):
        items = self._itemsCache.items
        battlesCount = self._getNewbieBattlesCount(items.getAccountDossier())
        if battlesCount >= newbiesSettings.battlesCount:
            return False
        criteria = _getNewbieVehicleCriteria(newbiesSettings.vehicleLevel)
        return False if items.getVehicles(criteria) else True

    @staticmethod
    def _getNewbieBattlesCount(dossier):
        from comp7_common import COMP7_ARCHIVE_NAMES, COMP7_SEASON_NUMBERS
        battleStats = [dossier.getRandomStats(),
         dossier.getEpicRandomStats(),
         dossier.getFortBattlesStats(),
         dossier.getFortSortiesStats(),
         dossier.getRankedStats(),
         dossier.getRanked10x10Stats(),
         dossier.getVersusAIStats(),
         dossier.getBattleRoyaleSoloStats(),
         dossier.getBattleRoyaleSquadStats()]
        battleStats.extend((dossier.getComp7Stats(season=seasonID) for seasonID in COMP7_SEASON_NUMBERS))
        battleStats.extend((dossier.getComp7Stats(archive=archiveName) for archiveName in COMP7_ARCHIVE_NAMES))
        return sum((stats.getBattlesCount() for stats in battleStats))


class GameLoadingCdnCacheMgr(BaseExternalCacheManager):
    _REQUEST_TIMEOUT = CDN_CACHE_SYNC_TIMEOUT
    _DEFAULT_SYNC_TIMEOUT = _REQUEST_TIMEOUT
    _itemsCache = dependency.descriptor(IItemsCache)
    _lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, defaults):
        super(GameLoadingCdnCacheMgr, self).__init__()
        self._cacheParams = CdnCacheParams()
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
        bootcampPlayerEvents.onBootcampBecomeNonPlayer += self.stopSync
        playerEvents.onAccountShowGUI += self._tryToDownload
        bootcampPlayerEvents.onAccountShowGUI += self._tryToDownload
        self._itemsCache.onSyncCompleted += self._onItemsCacheUpdated
        self._lobbyCtx.onServerSettingsChanged += self._onServerSettingsChanged
        self._lobbyCtx.getServerSettings().onServerSettingsChange += self._onServerSettingsUpdated
        _logger.debug('On connected called: items=%s, lobby=%s.', self._itemsCache, self._lobbyCtx)

    def onDisconnected(self):
        self.stopSync()
        self._downloadResult = None
        self._cacheParams.reset()
        playerEvents.onAccountShowGUI -= self._tryToDownload
        bootcampPlayerEvents.onAccountShowGUI -= self._tryToDownload
        playerEvents.onAccountBecomeNonPlayer -= self.stopSync
        bootcampPlayerEvents.onBootcampBecomeNonPlayer -= self.stopSync
        self._itemsCache.onSyncCompleted -= self._onItemsCacheUpdated
        self._lobbyCtx.getServerSettings().onServerSettingsChange -= self._onServerSettingsUpdated
        self._lobbyCtx.onServerSettingsChanged -= self._onServerSettingsChanged
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
            return GameLoadingCdnCache(self._defaults, externalConfigUrl=self._cacheParams.configUrl, itemsCache=self._itemsCache)
        else:
            _logger.debug('Selecting static cache.')
            return GameLoadingCdnCache(self._defaults, externalConfigUrl=None, itemsCache=None)

    def _onSynced(self, result):
        self._downloadResult = result
        _logger.debug('Got sync result: [%s].', result)

    def _onItemsCacheUpdated(self, *args, **kwargs):
        if self._cacheParams.isItemsCacheParamsReady:
            return
        else:
            if self._itemsCache is not None and self._itemsCache.isSynced():
                self._cacheParams.itemsCacheSynced = True
                _logger.debug('[ItemsCache] synced, ready to resolve cohort.')
                self._tryToDownload()
            return

    def _onServerSettingsChanged(self, *args, **kwargs):
        self._getExternalConfigURLParam()
        self._lobbyCtx.getServerSettings().onServerSettingsChange += self._onServerSettingsUpdated

    def _onServerSettingsUpdated(self, *args, **kwargs):
        self._getExternalConfigURLParam()

    def _getExternalConfigURLParam(self):
        if self._cacheParams.isServerSettingsParamsReady:
            return
        configUrl = self._getExternalConfigUrl()
        if configUrl:
            self._cacheParams.configUrl = configUrl
            _logger.debug('[ServerSettings] config url: %s selected.', configUrl)
            self._tryToDownload()

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
