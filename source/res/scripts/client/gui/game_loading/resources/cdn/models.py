# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/resources/cdn/models.py
from datetime import datetime
import typing
from typing import Optional, Union
import ResMgr
from dict2model.models import Model as BaseConfigModel
from gui.game_loading import loggers
from gui.game_loading.resources.cdn.consts import MIN_SLIDES_COUNT_TO_VIEW, SequenceCohorts
from gui.game_loading.resources.consts import ImageVfxs
from gui.game_loading.resources.models import LocalImageModel
from helpers import getClientLanguage, time_utils
from web.cache.web_cache import generateKey
if typing.TYPE_CHECKING:
    from gui.game_loading.resources.cdn.consts import SequenceOrders
    from gui.game_loading.resources.cdn.cache import GameLoadingCdnCache
_logger = loggers.getCdnConfigLogger()

class LocalSlideModel(LocalImageModel):
    __slots__ = ('_historyKey',)

    def __init__(self, imageRelativePath, vfx=None, localizationText=None, descriptionText=None, minShowTimeSec=0, transition=0):
        super(LocalSlideModel, self).__init__(imageRelativePath=imageRelativePath, vfx=vfx, localizationText=localizationText, descriptionText=descriptionText, minShowTimeSec=minShowTimeSec, transition=transition)
        self._historyKey = generateKey(self.imageRelativePath)

    @property
    def historyKey(self):
        return self._historyKey

    @staticmethod
    def isDownloaded(*args):
        return True


class LocalSequenceModel(object):
    __slots__ = ('name', 'order', 'slides')

    def __init__(self, name, order, slides):
        self.name = name
        self.order = order
        self.slides = list(slides)

    @property
    def minSlidesCountToView(self):
        return max(len(self.slides), 1)

    def __repr__(self):
        return '<LocalSequenceModel(name={}, slides={})>'.format(self.name, len(self.slides))


class ConfigSlideModel(BaseConfigModel):
    __slots__ = ('image', 'vfx', 'localization', '_imageCacheKey', '_localizationCacheKey', '_cacheKeysToUrls', '_langCode')

    def __init__(self, image, vfx, localization):
        super(ConfigSlideModel, self).__init__()
        self.image = image
        self.vfx = vfx
        self.localization = localization
        self._imageCacheKey = generateKey(self.image)
        self._cacheKeysToUrls = {self._imageCacheKey: self.image}
        if self.localization:
            self._localizationCacheKey = generateKey(self.localization)
            self._cacheKeysToUrls[self._localizationCacheKey] = self.localization
        else:
            self._localizationCacheKey = None
        self._langCode = getClientLanguage()
        return

    @property
    def historyKey(self):
        return self._imageCacheKey

    @property
    def urls(self):
        return list(self._cacheKeysToUrls.values())

    def isDownloaded(self, fileCache):
        currentCacheKeys = set(fileCache.getLoaded())
        return currentCacheKeys.issuperset(set(self._cacheKeysToUrls))

    def convertToLocal(self, fileCache, minShowTimeSec=0, transition=0):
        if not fileCache:
            _logger.warning('File cache object missing.')
            return
        else:
            localImagePath = fileCache.getRelativePath(self.image)
            if not localImagePath:
                _logger.warning('Image file for url [%s] is missing.', self.image)
                return
            localizationText = None
            descriptionText = None
            if self.localization:
                localLocalizationPath = fileCache.get(self.localization)
                if not localLocalizationPath:
                    _logger.warning('Localization file for url [%s] is missing.', self.localization)
                    return
                localizations = ResMgr.openSection(localLocalizationPath)
                if localizations:
                    titleSection = localizations['title']
                    if titleSection:
                        localizationText = titleSection.readString(self._langCode, default=None)
                    descriptionSection = localizations['description']
                    if descriptionSection:
                        descriptionText = descriptionSection.readString(self._langCode, default=None)
                    _logger.debug('Localization for lang [%s] is [%s] [%s].', self._langCode, localizationText, descriptionText)
            return LocalSlideModel(imageRelativePath=localImagePath, vfx=self.vfx, localizationText=localizationText or None, descriptionText=descriptionText or None, minShowTimeSec=minShowTimeSec, transition=transition)

    def __repr__(self):
        return '<ConfigSlideModel(image={}, vfx={}, localization={})>'.format(self.image, self.vfx, self.localization)


class ConfigSequenceModel(BaseConfigModel):
    __slots__ = ('name', 'start', 'finish', 'priority', 'order', 'views', 'enabled', 'cohorts', 'slides')

    def __init__(self, name, order, slides, start, finish, priority, views, enabled, cohorts):
        super(ConfigSequenceModel, self).__init__()
        self.name = name
        self.order = order
        self.slides = list(slides)
        self.start = start
        self.finish = finish
        self.priority = priority
        self.views = views
        self.enabled = enabled
        self.cohorts = list(cohorts or SequenceCohorts.getDefaults())

    @property
    def isActive(self):
        utcnow = datetime.utcfromtimestamp(time_utils.getServerUTCTime())
        return self.enabled and self.start <= utcnow < self.finish

    @property
    def minSlidesCountToView(self):
        return min(max(len(self.slides), 1), MIN_SLIDES_COUNT_TO_VIEW)

    def __repr__(self):
        return '<ConfigSequenceModel(name={}, active={}, priority={}, slides={})>'.format(self.name, self.isActive, self.priority, len(self.slides))


class ConfigModel(BaseConfigModel):
    __slots__ = ('enabled', 'sequences')

    def __init__(self, enabled, sequences):
        super(ConfigModel, self).__init__()
        self.sequences = sequences
        self.enabled = enabled

    def __repr__(self):
        return '<ConfigModel(enabled={}, sequences={})>'.format(self.enabled, len(self.sequences))


class CdnCacheDefaultsModel(object):
    __slots__ = ('sequence', 'minShowTimeSec', 'transition')

    def __init__(self, sequence, minShowTimeSec=0, transition=0):
        self.sequence = sequence
        self.minShowTimeSec = minShowTimeSec
        self.transition = transition

    def __repr__(self):
        return '<CdnCacheDefaultsModel(slides={}, minShowTimeSec={}, transition={})>'.format(len(self.sequence.slides), self.minShowTimeSec, self.transition)


class CdnCacheParamsModel(object):
    __slots__ = ('configUrl', 'cohort')

    def __init__(self, configUrl=None, cohort=None):
        self.configUrl = configUrl
        self.cohort = cohort

    @property
    def isItemsCacheParamsReady(self):
        return bool(self.cohort)

    @property
    def isServerSettingsParamsReady(self):
        return bool(self.configUrl)

    @property
    def isReady(self):
        return self.isItemsCacheParamsReady and self.isServerSettingsParamsReady

    def reset(self):
        self.configUrl = None
        self.cohort = None
        return

    def __repr__(self):
        return '<CdnCacheParamsModel(configUrl={}, cohort={})>'.format(self.configUrl, self.cohort)
