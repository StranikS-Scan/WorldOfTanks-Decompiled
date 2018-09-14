# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/RssNewsFeed.py
import uuid
import BigWorld
import ResMgr
import constants
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION
from helpers.i18n import encodeUtf8
from shared_utils import findFirst
from external_strings_utils import unicode_from_utf8
from adisp import process, async
from gui import GUI_SETTINGS, game_control
from gui.game_control.links import URLMarcos
from gui.Scaleform.daapi.view.meta.RssNewsFeedMeta import RssNewsFeedMeta

class RssNewsFeed(RssNewsFeedMeta):
    UPDATE_INTERVAL = 60
    DESCRIPTION_MAX_LENGTH = 250
    DESCRIPTION_TAIL = '...'
    DESCRIPTION_CUT_LENGTH = DESCRIPTION_MAX_LENGTH - len(DESCRIPTION_TAIL)
    SHOW_NEWS_COUNT = 3

    def __init__(self):
        super(RssNewsFeed, self).__init__()
        self.__requestCbID = None
        self.__feed = []
        self.__urlMacros = URLMarcos()
        return

    def getFeed(self):
        return self.__feed

    def openBrowser(self, linkToOpen):
        if linkToOpen:
            openBrowser = game_control.g_instance.links.open
            if GUI_SETTINGS.loginRssFeed.internalBrowser:
                browser = game_control.g_instance.browser
                if browser is not None:
                    openBrowser = browser.load
                else:
                    LOG_ERROR('Attempting to open internal browser, but browseris not exist. External browser will be opened', str(linkToOpen))
            LOG_DEBUG('Open browser', linkToOpen)
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

    @process
    def __requestFeed(self):
        yield lambda callback: callback(True)
        if GUI_SETTINGS.loginRssFeed.show:
            requestUrl = yield self.__getRssUrl()
            from helpers.RSSDownloader import g_downloader as g_rss
            if g_rss is not None:
                g_rss.download(self.__onRssFeedReceived, url=requestUrl)
            LOG_DEBUG('Requesting login RSS news', requestUrl)
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

            LOG_DEBUG('RSS feed received, entries count', len(self.__feed))
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

    @async
    @process
    def __getRssUrl(self, callback):
        if constants.IS_CHINA:
            callback('http://wot.kongzhong.com/erji/login_ticker.xml')
        url = yield self.__urlMacros.parse(str(GUI_SETTINGS.loginRssFeed.url))
        callback(url)

    def __prepareData(self, entryData):
        description = entryData.get('description')
        if description is not None:
            try:
                section = ResMgr.DataSection()
                section.createSectionFromString(encodeUtf8(description))
                _, section = findFirst(lambda (name, _): name == 'div', section.items())
                description, _ = unicode_from_utf8(section.asString)
                if len(description) > self.DESCRIPTION_MAX_LENGTH:
                    description = description[:self.DESCRIPTION_CUT_LENGTH] + self.DESCRIPTION_TAIL
            except Exception:
                LOG_ERROR('Invalid RSS entry description', entryData, description)
                LOG_CURRENT_EXCEPTION()
                return

        return {'id': entryData.get('id', str(uuid.uuid4())),
         'link': entryData.get('link'),
         'description': encodeUtf8(description)}
