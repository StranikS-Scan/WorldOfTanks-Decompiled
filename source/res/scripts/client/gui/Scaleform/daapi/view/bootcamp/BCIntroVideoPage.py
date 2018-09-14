# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCIntroVideoPage.py
import SoundGroups
from gui.Scaleform.daapi.view.meta.BCIntroVideoPageMeta import BCIntroVideoPageMeta
from gui.Scaleform.Waiting import Waiting
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.app_loader.settings import APP_NAME_SPACE
from gui.app_loader import g_appLoader
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampSettings import getBattleDefaults
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP, LOG_ERROR_BOOTCAMP
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import BootcampEvent
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
PATH_BACKGROUNDS_SMALL = '../maps/bootcamp/loading/{0}_small.png'
PATH_BACKGROUNDS_BIG = '../maps/bootcamp/loading/{0}_big.png'
LINKAGE_BACKGROUNDS_BIG = '{0}PageBigUI'
LINKAGE_BACKGROUNDS_SMALL = '{0}PageSmallUI'

class INTRO_HIGHLIGHT_TYPE:
    START_BUTTON = 0
    ARROWS = 1


class BCIntroVideoPage(BCIntroVideoPageMeta, IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, settings):
        super(BCIntroVideoPage, self).__init__()
        self.__backgroundImage = settings['backgroundImage']
        self.__movieFiles = [settings['video']]
        self.__lessonNumber = settings['lessonNumber']
        self.__tutorialPages = settings['tutorialPages']
        self.__autoStart = settings.get('autoStart', False)
        self.__soundValue = SoundGroups.g_instance.getMasterVolume() / 2
        self.__highlightingMask = 0
        g_bootcampEvents.onIntroVideoLoaded += self.onIntroVideoLoaded

    def onIntroVideoLoaded(self):
        self.as_loadedS()

    def stopVideo(self):
        if self.__movieFiles is not None and len(self.__movieFiles):
            self.__showNextMovie()
            return
        else:
            self.__onFinish()
            return

    def handleError(self, data):
        self.__onFinish()

    def videoFinished(self):
        self.__onFinish()
        self.as_showIntroPageS(len(self.__tutorialPages) == 0)

    def goNext(self):
        import BigWorld
        BigWorld.callback(0.1, lambda : g_bootcampEvents.onIntroVideoGoNext())
        if self.__isCurrentlyHighlighting(INTRO_HIGHLIGHT_TYPE.START_BUTTON):
            self.__setHighlighting(INTRO_HIGHLIGHT_TYPE.START_BUTTON, False)

    def _populate(self):
        super(BCIntroVideoPage, self)._populate()
        Waiting.hide('login')
        self.sessionProvider.addArenaCtrl(self)
        self.as_showIntroPageS(False)
        if self.__movieFiles is not None and len(self.__movieFiles):
            self.__showNextMovie()
        else:
            self.__onFinish()
        if self.__shouldHighlight(INTRO_HIGHLIGHT_TYPE.ARROWS):
            self.__setHighlighting(INTRO_HIGHLIGHT_TYPE.ARROWS, True)
        return

    def _dispose(self):
        for highlightType in (INTRO_HIGHLIGHT_TYPE.ARROWS, INTRO_HIGHLIGHT_TYPE.START_BUTTON):
            if self.__isCurrentlyHighlighting(highlightType):
                self.__setHighlighting(highlightType, False)

        g_bootcampEvents.onIntroVideoLoaded -= self.onIntroVideoLoaded
        self.sessionProvider.removeArenaCtrl(self)
        g_appLoader.detachCursor(APP_NAME_SPACE.SF_BATTLE)
        super(BCIntroVideoPage, self)._dispose()

    def __showNextMovie(self):
        moviePath = self.__movieFiles.pop(0)
        self.__showMovie(moviePath)

    def __showMovie(self, movie):
        LOG_DEBUG_DEV_BOOTCAMP('Startup Video: START - movie = %s, sound volume = %d per cent' % (movie, self.__soundValue * 100))
        listSmall = []
        listBig = []
        for pageId in self.__tutorialPages:
            listSmall.append(BCIntroVideoPage.getTutorialPageVO(pageId, False))
            listBig.append(BCIntroVideoPage.getTutorialPageVO(pageId, True))

        pageCount = len(listSmall)
        self.as_playVideoS({'showTutorialPages': pageCount > 0,
         'backgroundImage': self.__backgroundImage,
         'source': movie,
         'volume': self.__soundValue,
         'lessonPagesSmallData': listSmall,
         'lessonPagesBigData': listBig,
         'autoStart': self.__autoStart,
         'navigationButtonsVisible': pageCount > 1,
         'videoPlayerVisible': len(movie) > 0})

    @staticmethod
    def getTutorialPageVO(pageId, bigSize):
        voSettings = {'background': PATH_BACKGROUNDS_BIG.format(pageId),
         'rendererLinkage': LINKAGE_BACKGROUNDS_BIG.format(pageId)} if bigSize else {'background': PATH_BACKGROUNDS_SMALL.format(pageId),
         'rendererLinkage': LINKAGE_BACKGROUNDS_SMALL.format(pageId)}
        lessonProps = getBattleDefaults()['lessonPages'][pageId]
        voSettings.update(lessonProps)
        return voSettings

    def updateSpaceLoadProgress(self, progress):
        self.as_updateProgressS(progress)
        if progress == 1.0:
            if self.__isCurrentlyHighlighting(INTRO_HIGHLIGHT_TYPE.ARROWS):
                self.__setHighlighting(INTRO_HIGHLIGHT_TYPE.ARROWS, False)
            if self.__shouldHighlight(INTRO_HIGHLIGHT_TYPE.START_BUTTON):
                self.__setHighlighting(INTRO_HIGHLIGHT_TYPE.START_BUTTON, True)

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
        elif highlightType == INTRO_HIGHLIGHT_TYPE.START_BUTTON:
            return True
        elif highlightType == INTRO_HIGHLIGHT_TYPE.ARROWS:
            return len(self.__tutorialPages) > 1
        else:
            LOG_ERROR_BOOTCAMP('Unknown highlight type - {0}'.format(highlightType))
            return False
