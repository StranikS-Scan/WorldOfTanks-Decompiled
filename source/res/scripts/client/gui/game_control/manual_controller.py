# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/manual_controller.py
import logging
from account_helpers.AccountSettings import AccountSettings, LOBBY_MENU_MANUAL_TRIGGER_SHOWN
from gui.Scaleform.daapi.view.lobby.manual.states import ManualState, ManualChapterState
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.doc_loaders.manual_xml_data_reader import ManualPageTypes
from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
from helpers import dependency
from skeletons.gui.game_control import IManualController
from skeletons.gui.lobby_context import ILobbyContext
from gui.app_loader import sf_lobby
from gui.doc_loaders import manual_xml_data_reader
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from PlayerEvents import g_playerEvents
_logger = logging.getLogger(__name__)

class ManualController(IManualController):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(ManualController, self).__init__()
        self.__chapters = None
        self._isChapterViewOnScreen = False
        self._descrLabelBackBtn = ''
        return

    def init(self):
        g_eventBus.addListener(events.ManualEvent.CHAPTER_CLOSED, self.__onChapterClosed, EVENT_BUS_SCOPE.LOBBY)
        g_playerEvents.onAccountBecomePlayer += self.__onAccountBecomePlayer

    def fini(self):
        g_eventBus.removeListener(events.ManualEvent.CHAPTER_CLOSED, self.__onChapterClosed, EVENT_BUS_SCOPE.LOBBY)
        g_playerEvents.onAccountBecomePlayer -= self.__onAccountBecomePlayer

    @sf_lobby
    def app(self):
        return None

    def getChaptersUIData(self):
        chaptersUIData = [ i['uiData'] for i in self.__getChapters() ]
        return chaptersUIData

    def getChapterUIData(self, chapterIndex):
        chapterFilename = None
        chapterTitle = ''
        for chapter in self.__getChapters():
            if chapter['uiData']['index'] == chapterIndex:
                chapterFilename = chapter['filePath']
                chapterTitle = chapter['uiData'].get('label', '')

        currentChapter = manual_xml_data_reader.getChapterData(chapterFilename, self.pageFilter, chapterTitle)
        return currentChapter

    def pageFilter(self, pageType):
        return self.lobbyContext.getServerSettings().isMapsTrainingEnabled() if pageType == ManualPageTypes.MAPS_TRAINING_PAGE else True

    def clear(self):
        self.__chapters = None
        return

    def isActivated(self):
        return self.lobbyContext.getServerSettings().isManualEnabled()

    def getChapterView(self):
        lsm = getLobbyStateMachine()
        return lsm.getRelatedView(lsm.getStateByCls(ManualChapterState))

    def getView(self):
        lsm = getLobbyStateMachine()
        return lsm.getRelatedView(lsm.getStateByCls(ManualState))

    def getDescrLabelBackBtn(self):
        return self._descrLabelBackBtn

    def show(self, lessonID=None, descrLabelBackBtn=''):
        self._descrLabelBackBtn = descrLabelBackBtn
        view = self.getView()
        if not lessonID:
            ManualState.goTo()
        else:
            for chapterIndex, chapter in enumerate(self.__getChapters()):
                pageIndex = next((pageIndex for pageIndex, pageID in enumerate(chapter['pageIDs']) if pageID == lessonID), None)
                if pageIndex is not None:
                    if view:
                        self.showChapterView(chapterIndex, pageIndex)
                    else:
                        ManualState.goTo(chapterIndex, pageIndex)
                    return

            _logger.debug('Cant found page to show lesson with id %d', lessonID)
        return

    def isChapterViewOnScreen(self):
        return self._isChapterViewOnScreen

    def showChapterView(self, chapterIndex=0, pageIndex=0):
        self._isChapterViewOnScreen = True
        chapterView = self.getChapterView()
        if chapterView:
            chapterView.setData(chapterIndex, pageIndex)
            return
        ManualChapterState.goTo(chapterIndex, pageIndex)

    def collectUnreadPages(self, chapters):
        return [ chapter['newPageIDs'] for chapter in chapters ]

    def getNewContentCount(self):
        number = self.__countNewContent()
        return number if number and AccountSettings.getManualData(LOBBY_MENU_MANUAL_TRIGGER_SHOWN) else 0

    def __getChapters(self):
        if self.__chapters is None:
            self.__chapters = manual_xml_data_reader.getChapters(self.pageFilter)
        return self.__chapters

    def __onChapterClosed(self, _):
        self._isChapterViewOnScreen = False

    def __onAccountBecomePlayer(self):
        self.__initChaptersSettings()

    def __initChaptersSettings(self):
        chapters = AccountSettings.getManualUnreadPages()
        if chapters is None:
            chapters = self.collectUnreadPages(self.__getChapters())
            AccountSettings.setManualUnreadPages(chapters)
        return

    def __countNewContent(self):
        return sum((len(i) for i in AccountSettings.getManualUnreadPages()))
