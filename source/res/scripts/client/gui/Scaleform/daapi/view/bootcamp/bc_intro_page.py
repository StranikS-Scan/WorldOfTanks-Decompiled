# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/bc_intro_page.py
import BigWorld
import BattleReplay
from PlayerEvents import g_playerEvents
from constants import WOT_GAMEPLAY
from gui.Scaleform.daapi.view.meta.BCIntroVideoPageMeta import BCIntroVideoPageMeta
from gui.Scaleform.Waiting import Waiting
from gui.app_loader.settings import APP_NAME_SPACE
from bootcamp.BootCampEvents import g_bootcampEvents
from bootcamp.BootcampSettings import getBattleDefaults
from debug_utils_bootcamp import LOG_ERROR_BOOTCAMP
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import BootcampEvent
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
        self._backgroundImage = settings.get('backgroundImage', '')
        self._videoPlayerVisible = False
        self._movieFile = None
        self._soundValue = 0
        self._lessonNumber = settings.get('lessonNumber', 0)
        self._tutorialPages = settings.get('tutorialPages', [])
        self._autoStart = settings.get('autoStart', False)
        self._showSkipOption = settings.get('showSkipOption', True) if not BattleReplay.isPlaying() else False
        self._isReferralEnabled = settings.get('isReferralEnabled', False)
        self._isChoice = settings.get('isChoice', False)
        self._highlightingMask = 0
        self._goToBattleEvent = lambda : g_bootcampEvents.onGameplayChoice(WOT_GAMEPLAY.BOOTCAMP, WOT_GAMEPLAY.ON)
        return

    def videoFinished(self):
        self._onFinish()
        self.as_showIntroPageS(len(self._tutorialPages) == 0)

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
        self.__start()
        if self._shouldHighlight(INTRO_HIGHLIGHT_TYPE.ARROWS):
            self._setHighlighting(INTRO_HIGHLIGHT_TYPE.ARROWS, True)
        g_playerEvents.onDisconnected += self.__onDisconnected

    def _dispose(self):
        g_playerEvents.onDisconnected -= self.__onDisconnected
        for highlightType in (INTRO_HIGHLIGHT_TYPE.ARROWS, INTRO_HIGHLIGHT_TYPE.START_BUTTON):
            if self._isCurrentlyHighlighting(highlightType):
                self._setHighlighting(highlightType, False)

        self.appLoader.detachCursor(APP_NAME_SPACE.SF_BATTLE)
        super(BCIntroPage, self)._dispose()

    def __start(self):
        listSmall = []
        listBig = []
        for pageId in self._tutorialPages:
            listSmall.append(self._getTutorialPageVO(pageId, False))
            listBig.append(self._getTutorialPageVO(pageId, True))

        pageCount = len(listSmall)
        label = BOOTCAMP.BTN_TUTORIAL_START if self._showSkipOption and self._lessonNumber == 0 else BOOTCAMP.BTN_CONTINUE_PREBATTLE
        self.as_playVideoS({'isReferralEnabled': self._isReferralEnabled,
         'isBootcampCloseEnabled': self._isReferralEnabled,
         'referralDescription': BOOTCAMP.WELLCOME_BOOTCAMP_REFERRAL,
         'showTutorialPages': pageCount > 0,
         'backgroundImage': self._backgroundImage,
         'source': self._movieFile,
         'volume': self._soundValue,
         'lessonPagesSmallData': listSmall,
         'lessonPagesBigData': listBig,
         'autoStart': self._autoStart,
         'navigationButtonsVisible': pageCount > 1,
         'videoPlayerVisible': self._videoPlayerVisible,
         'allowSkipButton': self._showSkipOption,
         'selectButtonLabel': label})

    def __onDisconnected(self):
        self.destroy()

    def _onFinish(self):
        self.as_loadedS()

    def _isCurrentlyHighlighting(self, highlightType):
        return self._highlightingMask & 1 << highlightType != 0

    def _setHighlighting(self, highlightType, doHighlight):
        eventId = BootcampEvent.ADD_HIGHLIGHT if doHighlight else BootcampEvent.REMOVE_HIGHLIGHT
        if highlightType == INTRO_HIGHLIGHT_TYPE.START_BUTTON:
            g_eventBus.handleEvent(events.LoadViewEvent(eventId, None, 'StartBattleButton'), EVENT_BUS_SCOPE.BATTLE)
        elif highlightType == INTRO_HIGHLIGHT_TYPE.ARROWS:
            for highlightName in ('LoadingRightButton', 'LoadingLeftButton'):
                g_eventBus.handleEvent(events.LoadViewEvent(eventId, None, highlightName), EVENT_BUS_SCOPE.BATTLE)

        else:
            LOG_ERROR_BOOTCAMP('Unknown highlight type - {0}'.format(highlightType))
        if doHighlight:
            self._highlightingMask |= 1 << highlightType
        else:
            self._highlightingMask &= ~(1 << highlightType)
        return

    def _shouldHighlight(self, highlightType):
        if self._autoStart:
            return False
        if highlightType == INTRO_HIGHLIGHT_TYPE.START_BUTTON:
            return True
        if highlightType == INTRO_HIGHLIGHT_TYPE.ARROWS:
            return len(self._tutorialPages) > 1
        LOG_ERROR_BOOTCAMP('Unknown highlight type - {0}'.format(highlightType))
        return False
