# Embedded file name: scripts/client/gui/Scaleform/MovingText.py
import time
import BigWorld
import constants
from debug_utils import *
from gui.battle_control import g_sessionProvider
from windows import UIInterface
from gui import GUI_SETTINGS

class MovingText(UIInterface):
    """
    Client moving text overall.
    """
    UPDATE_INTERVAL = 600
    RSS_URL = 'http://wot.kongzhong.com/erji/ticker.xml'

    def __init__(self):
        """ Ctor. """
        UIInterface.__init__(self)
        self.__lastUpdateTime = -1
        self.__lastRSS = {}

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.addExternalCallbacks({'movingText.setDisplayObject': self.onSetDisplayObject})
        self.flashDO = None
        self.__updateCbID = None
        self.__updateCallback()
        return

    def dispossessUI(self):
        if self.uiHolder is not None:
            self.uiHolder.removeExternalCallbacks('movingText.setDisplayObject')
        self.__clearCallback()
        if self.flashDO is not None:
            self.flashDO.script = None
            self.flashDO = None
        UIInterface.dispossessUI(self)
        return

    def onSetDisplayObject(self, cid, moviePath):
        """
        Setting to this python class corresponded flash component.
        Called from flash by external interface.
        
        @param cid: callback id
        @param moviePath: path of the display object in flash
        """
        try:
            self.flashDO = self.uiHolder.getMember(moviePath)
            self.flashDO.script = self
            self.uiHolder.respond([cid, True, g_sessionProvider.getCtx().isInBattle])
        except Exception:
            LOG_ERROR('There is error while getting moving text display object')
            LOG_CURRENT_EXCEPTION()
            self.uiHolder.respond([cid, False, g_sessionProvider.getCtx().isInBattle])

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
            LOG_DEBUG('Requesting RSS news')
            downloadUrl = None
            if constants.IS_CHINA:
                downloadUrl = MovingText.RSS_URL
            from helpers.RSSDownloader import g_downloader
            if g_downloader is not None:
                g_downloader.download(self.__rssDownloadReceived, url=downloadUrl)
            return

    def __rssDownloadReceived(self, rssFeed):
        """ Rss data received handler """
        if self.flashDO is not None:
            try:
                self.__lastRSS = rssFeed
                self.flashDO.updateEntries(self.__getEntries(rssFeed))
            except Exception:
                LOG_ERROR('There is error while updating moving text entries')
                LOG_CURRENT_EXCEPTION()

        return

    @classmethod
    def isShowMovingText(cls):
        """
        Called from flash.
        
        @return: <bool> value from gui_settings.xml to show
                moving text or not
        """
        return GUI_SETTINGS.movingText.show

    @classmethod
    def __getEntries(cls, rssFeed):
        """
        @param rssFeed: rss feed from feedparser request
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
                browser = getattr(self.uiHolder, 'browser')
                if browser is not None:
                    openBrowser = browser.openBrowser
                else:
                    LOG_ERROR('Attempting to open internal browser with page: `%s`, but\t\t\t\t\t\tbrowser is not exist. External browser will be opened.' % str(link))
            if len(link):
                LOG_DEBUG('Open browser at page: ', link)
                openBrowser(link)
            del openBrowser
        return
