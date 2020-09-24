# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/bc_intro_page.py
import WWISE
import BigWorld
import BattleReplay
import Windowing
from PlayerEvents import g_playerEvents
from constants import WOT_GAMEPLAY
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.BCIntroVideoPageMeta import BCIntroVideoPageMeta
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.app_loader.settings import APP_NAME_SPACE
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampSettings import getBattleDefaults
from debug_utils_bootcamp import LOG_ERROR_BOOTCAMP
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.Scaleform.locale.BOOTCAMP import BOOTCAMP
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBootcampController
PATH_BACKGROUNDS = '../maps/icons/bootcamp/loading/{0}_{1}.png'
PATH_BACKGROUNDS_CORE = '../maps/icons/bootcamp/loading/{0}_{1}_core.png'
LINKAGE_BACKGROUNDS = '{0}Page{1}UI'

class INTRO_HIGHLIGHT_TYPE(object):
    START_BUTTON = 0
    ARROWS = 1


class BCIntroPage(BCIntroVideoPageMeta):
    bootcampCtrl = dependency.descriptor(IBootcampController)
    appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, settings):
        super(BCIntroPage, self).__init__()
        self._videoPlayerVisible = False
        self._movieFile = None
        self._backgroundVideo = None
        self._backgroundVideoBufferTime = None
        self._backgroundMusicStartEvent = None
        self._backgroundMusicStopEvent = None
        self._backgroundMusicPauseEvent = None
        self._backgroundMusicResumeEvent = None
        self._lessonNumber = settings.get('lessonNumber', 0)
        self._tutorialPages = settings.get('tutorialPages', [])
        self._autoStart = settings.get('autoStart', False)
        self._showSkipOption = settings.get('showSkipOption', True) if not BattleReplay.isPlaying() else False
        self._isReferralEnabled = settings.get('isReferralEnabled', False)
        self._isChoice = settings.get('isChoice', False)
        self._highlightingMask = 0
        self._goToBattleEvent = lambda : g_bootcampEvents.onGameplayChoice(WOT_GAMEPLAY.BOOTCAMP, WOT_GAMEPLAY.ON)
        self._isWindowAccessible = True
        self._delayedVideoStart = False
        return

    def videoFinished(self):
        self._onFinish()
        self.as_showIntroPageS(len(self._tutorialPages) == 0)

    def videoStarted(self):
        if self._movieFile and self._backgroundMusicStartEvent:
            WWISE.WW_eventGlobal(self._backgroundMusicStartEvent)

    def goToBattle(self):
        BigWorld.callback(0.1, self._goToBattleEvent)
        if self._isCurrentlyHighlighting(INTRO_HIGHLIGHT_TYPE.START_BUTTON):
            self._setHighlighting(INTRO_HIGHLIGHT_TYPE.START_BUTTON, False)

    def skipBootcamp(self):
        if self._isChoice:
            g_bootcampEvents.onGameplayChoice(WOT_GAMEPLAY.BOOTCAMP, WOT_GAMEPLAY.OFF)
        else:
            self.bootcampCtrl.runBootcamp()

    def handleError(self, data):
        LOG_ERROR_BOOTCAMP('Video error - {0}'.format(data))
        self._onFinish()

    @staticmethod
    def _getBackgroundBlind(imagePath):
        return imagePath if imagePath in RES_ICONS.MAPS_ICONS_BOOTCAMP_LOADING_ALL_CORE_ENUM else ''

    @staticmethod
    def _getTutorialPageVO(pageId, bigSize):
        battleDefaults = getBattleDefaults()
        lessonProps = battleDefaults['lessonPages'][pageId]
        pathBackgroundSize = 'big' if bigSize else 'small'
        linkageBackgroundSize = 'Big' if bigSize else 'Small'
        voSettings = {'background': PATH_BACKGROUNDS.format(pageId, pathBackgroundSize),
         'backgroundBlind': BCIntroPage._getBackgroundBlind(PATH_BACKGROUNDS_CORE.format(pageId, pathBackgroundSize)),
         'rendererLinkage': LINKAGE_BACKGROUNDS.format(pageId, linkageBackgroundSize)}
        voSettings.update(lessonProps)
        return voSettings

    def _populate(self):
        super(BCIntroPage, self)._populate()
        Waiting.hide('login')
        self.as_showIntroPageS(False)
        self._isWindowAccessible = Windowing.isWindowAccessible() if self._canWindowBePaused() else True
        if self._movieFile:
            if self._isWindowAccessible:
                self._start()
            else:
                self._delayedVideoStart = True
            if self._canWindowBePaused():
                Windowing.addWindowAccessibilitynHandler(self._onWindowAccessibilityChanged)
        else:
            self._start()
        if self._shouldHighlight(INTRO_HIGHLIGHT_TYPE.ARROWS):
            self._setHighlighting(INTRO_HIGHLIGHT_TYPE.ARROWS, True)
        g_playerEvents.onDisconnected += self._onDisconnected

    def _canWindowBePaused(self):
        return not BigWorld.checkUnattended()

    def _dispose(self):
        g_playerEvents.onDisconnected -= self._onDisconnected
        for highlightType in (INTRO_HIGHLIGHT_TYPE.ARROWS, INTRO_HIGHLIGHT_TYPE.START_BUTTON):
            if self._isCurrentlyHighlighting(highlightType):
                self._setHighlighting(highlightType, False)

        self.appLoader.detachCursor(APP_NAME_SPACE.SF_BATTLE)
        if self._movieFile and self._canWindowBePaused():
            Windowing.removeWindowAccessibilityHandler(self._onWindowAccessibilityChanged)
        if self._movieFile and self._backgroundMusicStopEvent:
            WWISE.WW_eventGlobal(self._backgroundMusicStopEvent)
        super(BCIntroPage, self)._dispose()

    def _start(self):
        listSmall = []
        listBig = []
        for pageId in self._tutorialPages:
            listSmall.append(self._getTutorialPageVO(pageId, False))
            listBig.append(self._getTutorialPageVO(pageId, True))

        pageCount = len(listSmall)
        label = BOOTCAMP.BTN_TUTORIAL_START if self._showSkipOption and self._lessonNumber == 0 else BOOTCAMP.BTN_CONTINUE_PREBATTLE
        self.as_setDataS({'isReferralEnabled': self._isReferralEnabled,
         'isBootcampCloseEnabled': self._isReferralEnabled,
         'referralDescription': BOOTCAMP.WELLCOME_BOOTCAMP_REFERRAL,
         'showTutorialPages': pageCount > 0,
         'backgroundVideo': self._backgroundVideo,
         'source': self._movieFile,
         'lessonPagesSmallData': listSmall,
         'lessonPagesBigData': listBig,
         'autoStart': self._autoStart,
         'navigationButtonsVisible': pageCount > 1,
         'videoPlayerVisible': self._videoPlayerVisible,
         'allowSkipButton': self._showSkipOption,
         'selectButtonLabel': label,
         'bufferTime': self._backgroundVideoBufferTime})

    def _onDisconnected(self):
        self.destroy()

    def _onFinish(self):
        self.as_loadedS()

    def _isCurrentlyHighlighting(self, highlightType):
        return self._highlightingMask & 1 << highlightType != 0

    def _setHighlighting(self, highlightType, doHighlight):
        eventId = VIEW_ALIAS.BOOTCAMP_ADD_HIGHLIGHT if doHighlight else VIEW_ALIAS.BOOTCAMP_REMOVE_HIGHLIGHT
        if highlightType == INTRO_HIGHLIGHT_TYPE.START_BUTTON:
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(eventId), ctx='StartBattleButton'), EVENT_BUS_SCOPE.BATTLE)
        elif highlightType == INTRO_HIGHLIGHT_TYPE.ARROWS:
            for highlightName in ('LoadingRightButton', 'LoadingLeftButton'):
                g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(eventId), ctx=highlightName), EVENT_BUS_SCOPE.BATTLE)

        else:
            LOG_ERROR_BOOTCAMP('Unknown highlight type - {0}'.format(highlightType))
        if doHighlight:
            self._highlightingMask |= 1 << highlightType
        else:
            self._highlightingMask &= ~(1 << highlightType)

    def _shouldHighlight(self, highlightType):
        if self._autoStart:
            return False
        if highlightType == INTRO_HIGHLIGHT_TYPE.START_BUTTON:
            return True
        if highlightType == INTRO_HIGHLIGHT_TYPE.ARROWS:
            return len(self._tutorialPages) > 1
        LOG_ERROR_BOOTCAMP('Unknown highlight type - {0}'.format(highlightType))
        return False

    def _onWindowAccessibilityChanged(self, isAccessible):
        if self._isWindowAccessible == isAccessible:
            return
        self._isWindowAccessible = isAccessible
        if isAccessible and self._delayedVideoStart:
            self._start()
            self._delayedVideoStart = False
        else:
            self._applyWindowAccessibility()

    def _applyWindowAccessibility(self):
        if self._isWindowAccessible:
            self._resumePlayback()
        else:
            self._pausePlayback()

    def _pausePlayback(self):
        self.as_pausePlaybackS()
        if self._backgroundMusicPauseEvent:
            WWISE.WW_eventGlobal(self._backgroundMusicPauseEvent)

    def _resumePlayback(self):
        self.as_resumePlaybackS()
        if self._backgroundMusicResumeEvent:
            WWISE.WW_eventGlobal(self._backgroundMusicResumeEvent)
