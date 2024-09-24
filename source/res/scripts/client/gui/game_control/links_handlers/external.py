# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/links_handlers/external.py
from collections import defaultdict
import typing
import logging
import urlparse
import BigWorld
from constants import DISTRIBUTION_PLATFORM
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.Scaleform.daapi.view.lobby.store.browser import shop_helpers
from gui.shared.event_dispatcher import showShop
from helpers import dependency
from helpers.http.url_formatters import addParamsToUrlQuery
from skeletons.gui.login_manager import ILoginManager
_PLATFORM_PARAM = 'platform'
_WOT_PLATFORM_PARAM = 'wot_platform'
_INGAME_SHOP_PARAM = 'ingame_shop'
_PATH_TO_CHECK_ARGS = '/id/signin/token'
_URL_ARGS_TO_CHECK = ('next',)
_logger = logging.getLogger(__name__)
CheckHandleResult = typing.NamedTuple('CheckHandleResult', (('handled', bool), ('externalAllowed', bool)))

class ILinksHandler(object):

    def checkHandle(self, url):
        raise NotImplementedError

    def handle(self, url):
        raise NotImplementedError


class OpenBrowserHandler(ILinksHandler):

    def checkHandle(self, url):
        return CheckHandleResult(True, True)

    def handle(self, url):
        try:
            BigWorld.wg_openWebBrowser(url)
            return True
        except Exception:
            _logger.error('There is error while opening web browser at page: %s', url)
            LOG_CURRENT_EXCEPTION()

        return False


class AddPlatformTagLinksHandler(OpenBrowserHandler):
    __loginManager = dependency.descriptor(ILoginManager)

    def checkHandle(self, url):
        return CheckHandleResult(bool(self._getPlatform()) and self._hasWotPlatformTags(url), True)

    def handle(self, url):
        platform = self._getPlatform()
        if platform and self._hasWotPlatformTags(url):
            url = self._addPlatformParamToUrl(url, platform)
            return super(AddPlatformTagLinksHandler, self).handle(url)
        return False

    def _getPlatform(self):
        return DISTRIBUTION_PLATFORM.STEAM.value if self.__loginManager.isWgcSteam else ''

    def _hasWotPlatformTags(self, url):
        query = urlparse.urlparse(url).query
        if not query:
            return False
        tags = urlparse.parse_qs(query, keep_blank_values=True)
        return _WOT_PLATFORM_PARAM in tags

    def _addPlatformParamToUrl(self, url, param):
        return addParamsToUrlQuery(url, {_PLATFORM_PARAM: [param]}, keepBlankValues=True)


def _getUrlsMapFromLinkArgs(url):
    parts = urlparse.urlparse(url)
    if not parts.query or not parts.path or not parts.path.startswith(_PATH_TO_CHECK_ARGS):
        return {}
    tags = urlparse.parse_qs(parts.query, keep_blank_values=False)
    return {arg:tags[arg][0] for arg in _URL_ARGS_TO_CHECK if arg in tags}


class AddPlatformTagLinksToArgsUrlHandler(AddPlatformTagLinksHandler):

    def _hasWotPlatformTags(self, url):
        urls = _getUrlsMapFromLinkArgs(url)
        for argUrl in urls.itervalues():
            if super(AddPlatformTagLinksToArgsUrlHandler, self)._hasWotPlatformTags(argUrl):
                return True

        return False

    def handle(self, url):
        platform = self._getPlatform()
        if platform:
            urls = _getUrlsMapFromLinkArgs(url)
            if urls:
                urls = {arg:[self._addPlatformParamToUrl(url, platform)] for arg, url in urls.iteritems() if AddPlatformTagLinksHandler._hasWotPlatformTags(self, url)}
                url = addParamsToUrlQuery(url, urls, keepBlankValues=True)
                return OpenBrowserHandler.handle(self, url)
        return False


class PremShopLinksHandler(ILinksHandler):

    def checkHandle(self, url):
        hasShopArgs = bool(self.__getIngameShopArgs(url))
        return CheckHandleResult(hasShopArgs, not hasShopArgs)

    def handle(self, url):
        shopArgs = self.__getIngameShopArgs(url)
        if shopArgs:
            showShop(shop_helpers.getSplitPageUrl(shopArgs))
            return True
        return False

    def __getIngameShopArgs(self, url):
        query = urlparse.urlparse(url).query
        if not query:
            return {}
        tags = urlparse.parse_qs(query, keep_blank_values=True)
        args = defaultdict(list)
        for t, v in tags.iteritems():
            if t.startswith(_INGAME_SHOP_PARAM):
                args.update({t: v})

        return args


class PremShopLinksForArgsUrlHandler(PremShopLinksHandler):

    def checkHandle(self, url):
        urls = _getUrlsMapFromLinkArgs(url)
        for argUrl in urls.itervalues():
            res = super(PremShopLinksForArgsUrlHandler, self).checkHandle(argUrl)
            if res.handled:
                return res

        return CheckHandleResult(bool(urls), True)

    def handle(self, url):
        urls = _getUrlsMapFromLinkArgs(url)
        for argUrl in urls.itervalues():
            if super(PremShopLinksForArgsUrlHandler, self).handle(argUrl):
                return True

        return False
