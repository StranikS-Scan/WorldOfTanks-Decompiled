# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCIntroVideoPage.py
import BigWorld
import SoundGroups
from gui.Scaleform.daapi.view.meta.BCIntroVideoPageMeta import BCIntroVideoPageMeta
from gui.Scaleform.Waiting import Waiting
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.app_loader.settings import APP_NAME_SPACE
from gui.app_loader import g_appLoader
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.account_helpers.settings_core import ISettingsCore
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampSettings import getBattleDefaults
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP, LOG_ERROR_BOOTCAMP
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import BootcampEvent
from gui.Scaleform.locale.BOOTCAMP import BOOTCAMP
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
PATH_BACKGROUNDS_SMALL = '../maps/icons/bootcamp/loading/{0}_small.png'
PATH_BACKGROUNDS_SMALL_CORE = '../maps/icons/bootcamp/loading/{0}_small_core.png'
PATH_BACKGROUNDS_BIG = '../maps/icons/bootcamp/loading/{0}_big.png'
PATH_BACKGROUNDS_BIG_CORE = '../maps/icons/bootcamp/loading/{0}_big_core.png'
LINKAGE_BACKGROUNDS_BIG = '{0}PageBigUI'
LINKAGE_BACKGROUNDS_SMALL = '{0}PageSmallUI'

class INTRO_HIGHLIGHT_TYPE(object):
    START_BUTTON = 0
    ARROWS = 1


class BCIntroVideoPage(BCIntroVideoPageMeta, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, settings):
        super(BCIntroVideoPage, self).__init__()
        self.__backgroundImage = settings.get('backgroundImage', '')
        self.__movieFile = settings.get('video', '')
        self.__lessonNumber = settings.get('lessonNumber', 0)
        self.__tutorialPages = settings.get('tutorialPages', [])
        self.__autoStart = settings.get('autoStart', False)
        self.__showSkipOption = settings.get('skipOption', False)
        self.__soundValue = SoundGroups.g_instance.getMasterVolume() / 2
        self.__highlightingMask = 0

    def onIntroVideoLoaded(self):
        self.as_loadedS()

    def stopVideo(self):
        self.__onFinish()

    def handleError(self, data):
        self.__onFinish()

    def videoFinished(self):
        self.__onFinish()
        self.as_showIntroPageS(len(self.__tutorialPages) == 0)

    def goToBattle(self):
        evt = g_bootcampEvents.onIntroVideoAccept() if self.__showSkipOption else g_bootcampEvents.onIntroVideoGoNext()
        BigWorld.callback(0.1, lambda : evt)
        if self.__isCurrentlyHighlighting(INTRO_HIGHLIGHT_TYPE.START_BUTTON):
            self.__setHighlighting(INTRO_HIGHLIGHT_TYPE.START_BUTTON, False)

    def onArenaStarted(self):
        self.destroy()

    @staticmethod
    def getBackgroundBlind(formatStr, pageId):
        imagePath = formatStr.format(pageId)
        return imagePath if imagePath in RES_ICONS.MAPS_ICONS_BOOTCAMP_LOADING_ALL_CORE_ENUM else ''

    @staticmethod
    def getTutorialPageVO(pageId, bigSize):
        battleDefaults = getBattleDefaults()
        lessonProps = battleDefaults['lessonPages'][pageId]
        if bigSize:
            voSettings = {'background': PATH_BACKGROUNDS_BIG.format(pageId),
             'backgroundBlind': BCIntroVideoPage.getBackgroundBlind(PATH_BACKGROUNDS_BIG_CORE, pageId),
             'rendererLinkage': LINKAGE_BACKGROUNDS_BIG.format(pageId)}
        else:
            voSettings = {'background': PATH_BACKGROUNDS_SMALL.format(pageId),
             'backgroundBlind': BCIntroVideoPage.getBackgroundBlind(PATH_BACKGROUNDS_SMALL_CORE, pageId),
             'rendererLinkage': LINKAGE_BACKGROUNDS_SMALL.format(pageId)}
        voSettings.update(lessonProps)
        return voSettings

    def updateSpaceLoadProgress(self, progress):
        self.as_updateProgressS(progress)
        if progress == 1.0:
            if self.__isCurrentlyHighlighting(INTRO_HIGHLIGHT_TYPE.ARROWS):
                self.__setHighlighting(INTRO_HIGHLIGHT_TYPE.ARROWS, False)
            if self.__shouldHighlight(INTRO_HIGHLIGHT_TYPE.START_BUTTON):
                self.__setHighlighting(INTRO_HIGHLIGHT_TYPE.START_BUTTON, True)

    def skipBootcamp(self):
        g_bootcampEvents.onIntroVideoSkip()

    def _populate(self):
        super(BCIntroVideoPage, self)._populate()
        Waiting.hide('login')
        self.sessionProvider.addArenaCtrl(self)
        self.as_showIntroPageS(False)
        g_bootcampEvents.onArenaStarted += self.onArenaStarted
        g_bootcampEvents.onIntroVideoLoaded += self.onIntroVideoLoaded
        self.__showMovie()
        if self.__shouldHighlight(INTRO_HIGHLIGHT_TYPE.ARROWS):
            self.__setHighlighting(INTRO_HIGHLIGHT_TYPE.ARROWS, True)

    def _dispose(self):
        for highlightType in (INTRO_HIGHLIGHT_TYPE.ARROWS, INTRO_HIGHLIGHT_TYPE.START_BUTTON):
            if self.__isCurrentlyHighlighting(highlightType):
                self.__setHighlighting(highlightType, False)

        g_bootcampEvents.onIntroVideoLoaded -= self.onIntroVideoLoaded
        g_bootcampEvents.onArenaStarted -= self.onArenaStarted
        self.sessionProvider.removeArenaCtrl(self)
        g_appLoader.detachCursor(APP_NAME_SPACE.SF_BATTLE)
        super(BCIntroVideoPage, self)._dispose()

    def __showMovie(self):
        LOG_DEBUG_DEV_BOOTCAMP('Startup Video: START - movie = %s, sound volume = %d per cent' % (self.__movieFile, self.__soundValue * 100))
        listSmall = []
        listBig = []
        for pageId in self.__tutorialPages:
            listSmall.append(BCIntroVideoPage.getTutorialPageVO(pageId, False))
            listBig.append(BCIntroVideoPage.getTutorialPageVO(pageId, True))

        pageCount = len(listSmall)
        label = BOOTCAMP.BTN_TUTORIAL_START if self.__showSkipOption and self.__lessonNumber == 0 else BOOTCAMP.BTN_CONTINUE_PREBATTLE
        self.as_playVideoS({'showTutorialPages': pageCount > 0,
         'backgroundImage': self.__backgroundImage,
         'source': self.__movieFile,
         'volume': self.__soundValue,
         'lessonPagesSmallData': listSmall,
         'lessonPagesBigData': listBig,
         'autoStart': self.__autoStart,
         'navigationButtonsVisible': pageCount > 1,
         'videoPlayerVisible': True,
         'allowSkipButton': self.__showSkipOption,
         'selectButtonLabel': label})

    def __onFinish(self):
        g_bootcampEvents.onIntroVideoStop()

    def __isCurrentlyHighlighting(self, highlightType):
        return self.__highlightingMask & 1 << highlightType != 0

    def __setHighlighting(self, highlightType, doHighlight):
        eventId = BootcampEvent.ADD_HIGHLIGHT if doHighlight else BootcampEvent.REMOVE_HIGHLIGHT
        if highlightType == INTRO_HIGHLIGHT_TYPE.START_BUTTON:
            g_eventBus.handleEvent(events.LoadViewEvent(eventId, None, 'StartBattleButton'), EVENT_BUS_SCOPE.BATTLE)
        elif highlightType == INTRO_HIGHLIGHT_TYPE.ARROWS:
            for highlightName in ('LoadingRightButton', 'LoadingLeftButton'):
                g_eventBus.handleEvent(events.LoadViewEvent(eventId, None, highlightName), EVENT_BUS_SCOPE.BATTLE)

        else:
            LOG_ERROR_BOOTCAMP('Unknown highlight type - {0}'.format(highlightType))
        if doHighlight:
            self.__highlightingMask |= 1 << highlightType
        else:
            self.__highlightingMask &= ~(1 << highlightType)
        return

    def __shouldHighlight(self, highlightType):
        if self.__autoStart:
            return False
        if highlightType == INTRO_HIGHLIGHT_TYPE.START_BUTTON:
            return True
        if highlightType == INTRO_HIGHLIGHT_TYPE.ARROWS:
            return len(self.__tutorialPages) > 1
        LOG_ERROR_BOOTCAMP('Unknown highlight type - {0}'.format(highlightType))
        return False
