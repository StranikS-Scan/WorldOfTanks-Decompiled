# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/Ticker.py
import BigWorld, time, constants
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.daapi.view.meta.TickerMeta import TickerMeta
from gui import GUI_SETTINGS, game_control

class Ticker(TickerMeta):
    UPDATE_INTERVAL = 600
    RSS_URL = 'http://wot.kongzhong.com/erji/ticker.xml'

    def __init__(self):
        super(Ticker, self).__init__()
        self.__lastUpdateTime = -1
        self.__lastRSS = {}

    def _populate(self):
        super(Ticker, self)._populate()
        self.__updateCbID = None
        self.__updateCallback()
        return

    def _dispose(self):
        super(Ticker, self)._dispose()
        self.__clearCallback()
        self.__lastRSS = None
        return

    def showBrowser(self, entryID):
        """
        Showing browser with given @entryID.
        @param entryID: <str> rss entry id
        """
        entry = self.__findEntry(entryID)
        if entry is not None:
            link = entry.get('link', '')
            openBrowser = BigWorld.wg_openWebBrowser
            if GUI_SETTINGS.movingText.internalBrowser:
                browser = game_control.g_instance.browser
                if browser is not None:
                    openBrowser = browser.load
                else:
                    LOG_ERROR('Attempting to open internal browser with page: `%s`,but browser is not exist. External browser will be opened.' % str(link))
            if len(link):
                LOG_DEBUG('Open browser at page: ', link)
                openBrowser(link)
        return

    def __clearCallback(self):
        """ Clear news updating callback """
        if self.__updateCbID is not None:
            BigWorld.cancelCallback(self.__updateCbID)
            self.__updateCbID = None
        return

    def __updateCallback(self):
        """ New updating interval handler """
        self.__update()
        self.__clearCallback()
        self.__updateCbID = BigWorld.callback(self.UPDATE_INTERVAL, self.__updateCallback)

    def __update(self):
        if not GUI_SETTINGS.movingText.show:
            return
        else:
            self.__lastUpdateTime = time.time()
            downloadUrl = None
            if constants.IS_CHINA:
                downloadUrl = Ticker.RSS_URL
            from helpers.RSSDownloader import g_downloader
            if g_downloader is not None:
                g_downloader.download(self.__rssDownloadReceived, url=downloadUrl)
            return

    def __rssDownloadReceived(self, rssFeed):
        """ Rss data received handler """
        self.__lastRSS = rssFeed
        self.as_setItemsS(self.__getEntries(rssFeed))

    @classmethod
    def __getEntries(cls, rssFeed):
        """
        @return: <list of dict< 'id':<str>, 'title':<str>, 'summary':<str> >
                list of rss entries data
        """
        result = []
        for entry in rssFeed.get('entries', []):
            result.append({'id': entry.get('id'),
             'title': entry.get('title'),
             'summary': entry.get('summary')})

        return result

    def __findEntry(self, entryID):
        """
        Returns rss entry.
        
        @param entryID: <str> rss id to find
        @return: <dict> entry data
        """
        for entry in self.__lastRSS.get('entries', []):
            if entry.get('id') == entryID:
                return entry

        return None
