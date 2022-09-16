# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/RssNewsFeed.py
import logging
import uuid
import BigWorld
import ResMgr
from adisp import adisp_process, adisp_async
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.meta.RssNewsFeedMeta import RssNewsFeedMeta
from gui.game_control.links import URLMacros
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IExternalLinksController, IBrowserController
_logger = logging.getLogger(__name__)

class RssNewsFeed(RssNewsFeedMeta):
    UPDATE_INTERVAL = 60
    DESCRIPTION_MAX_LENGTH = 250
    DESCRIPTION_TAIL = '...'
    DESCRIPTION_CUT_LENGTH = DESCRIPTION_MAX_LENGTH - len(DESCRIPTION_TAIL)
    SHOW_NEWS_COUNT = 3
    externalBrowser = dependency.descriptor(IExternalLinksController)
    internalBrowser = dependency.descriptor(IBrowserController)

    def __init__(self):
        super(RssNewsFeed, self).__init__()
        self.__requestCbID = None
        self.__feed = []
        self.__urlMacros = URLMacros()
        return

    def getFeed(self):
        return self.__feed

    def openBrowser(self, linkToOpen):
        if linkToOpen:
            openBrowser = self.externalBrowser.open
            if GUI_SETTINGS.loginRssFeed.internalBrowser:
                browser = self.internalBrowser
                if browser is not None:
                    openBrowser = browser.load
                else:
                    _logger.error('Attempting to open internal browser, but browseris not exist. External browser will be opened: %r', linkToOpen)
            _logger.debug('Open browser: %r', linkToOpen)
            openBrowser(linkToOpen)
        return

    def _populate(self):
        super(RssNewsFeed, self)._populate()
        self.__updateCallback()

    def _dispose(self):
        self.__urlMacros.clear()
        self.__urlMacros = None
        self.__feed = []
        self.__clearCallback()
        super(RssNewsFeed, self)._dispose()
        return

    @adisp_process
    def __requestFeed(self):
        yield lambda callback: callback(True)
        if GUI_SETTINGS.loginRssFeed.show:
            requestUrl = yield self.__getRssUrl()
            from helpers.RSSDownloader import g_downloader as g_rss
            if g_rss is not None:
                g_rss.download(self.__onRssFeedReceived, url=requestUrl)
            _logger.debug('Requesting login RSS news: %s', requestUrl)
        return

    def __onRssFeedReceived(self, data):
        if self.isDisposed():
            return
        else:
            self.__feed = []
            for entry in reversed(data.get('entries', [])):
                data = self.__prepareData(entry)
                if data is not None:
                    self.__feed.append(data)

            _logger.debug('RSS feed received, entries count %d', len(self.__feed))
            self.as_updateFeedS(self.__feed[:self.SHOW_NEWS_COUNT])
            return

    def __clearCallback(self):
        if self.__requestCbID is not None:
            BigWorld.cancelCallback(self.__requestCbID)
            self.__requestCbID = None
        return

    def __updateCallback(self):
        self.__requestFeed()
        self.__clearCallback()
        self.__requestCbID = BigWorld.callback(self.UPDATE_INTERVAL, self.__updateCallback)

    @adisp_async
    @adisp_process
    def __getRssUrl(self, callback):
        url = yield self.__urlMacros.parse(str(GUI_SETTINGS.loginRssFeed.url))
        callback(url)

    def __prepareData(self, entryData):
        description = entryData.get('description')
        if description is not None:
            try:
                section = ResMgr.DataSection()
                section.createSectionFromString(description)
                _, section = findFirst(lambda (name, _): name == 'div', section.items())
                description = section.asWideString
                if len(description) > self.DESCRIPTION_MAX_LENGTH:
                    description = description[:self.DESCRIPTION_CUT_LENGTH] + self.DESCRIPTION_TAIL
            except Exception:
                _logger.exception('Invalid RSS entry description: %r, %r', entryData, description)
                return

        return {'id': entryData.get('id', str(uuid.uuid4())),
         'link': entryData.get('link'),
         'description': description}
