# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/offers/cache.py
import logging
import urlparse
import typing
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
from web.cache.web_cache import createManifestRecord, BaseExternalCache, BaseExternalCacheManager
_logger = logging.getLogger(__name__)
_CDN_CACHE_DIR = 'offers_cache'
_CDN_WORKERS = 2

class ExternalCache(BaseExternalCache):
    _lobbyCtx = dependency.descriptor(ILobbyContext)
    _offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self, cacheName, workersLimit):
        super(ExternalCache, self).__init__(cacheName, workersLimit)
        self._cdnRootUrl = ''

    def get(self, cdnRelativePath):
        if not self._cdnRootUrl:
            return None
        else:
            url = urlparse.urljoin(self._cdnRootUrl, cdnRelativePath)
            return super(ExternalCache, self).get(url)

    def _createManifest(self, config=None):
        url = self._lobbyCtx.getServerSettings().fileServer.getOffersRootUrl()
        if not isinstance(url, str):
            _logger.error('Broken url: %s. Check server settings', url)
            url = ''
        if not url:
            return None
        else:
            if not url.endswith('/'):
                url += '/'
            self._cdnRootUrl = url
            root = urlparse.urlparse(self._cdnRootUrl)
            host = urlparse.urlunsplit((root.scheme,
             root.netloc,
             '',
             '',
             ''))
            resMap = {'localizations': set(),
             'images': set()}
            for offer in self._offersProvider.iAvailableOffers():
                resMap['localizations'].update({offer.cdnLocFilePath})
                resMap['images'].update({offer.cdnBannerLogoPath,
                 offer.cdnLogoPath,
                 offer.cdnGiftsBackgroundPath,
                 offer.cdnGiftsTokenImgPath})
                for gift in offer.availableGifts:
                    resMap['localizations'].update({gift.cdnLocFilePath})
                    resMap['images'].update({gift.cdnImagePath, gift.cdnIconPath})

            manifest = []
            for resName, filePaths in resMap.iteritems():
                record = createManifestRecord(appName=resName, host=host, files=[ urlparse.urljoin(root.path, path) for path in filePaths if path ], code='OK', description='SUCCESS')
                manifest.append(record)

            return manifest


class CdnResourcesCache(BaseExternalCacheManager):
    _REQUEST_TIMEOUT = 300.0
    _DEFAULT_SYNC_TIMEOUT = 180.0

    def _createCache(self):
        return ExternalCache(_CDN_CACHE_DIR, _CDN_WORKERS)
