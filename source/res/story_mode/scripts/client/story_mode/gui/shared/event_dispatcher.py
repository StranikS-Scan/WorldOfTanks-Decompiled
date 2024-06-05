# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/shared/event_dispatcher.py
from functools import wraps
from logging import getLogger
import typing
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams, SFViewLoadParams
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from gui.impl.gen import R
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.impl import IGuiLoader
from story_mode.gui.fade_in_out import UseStoryModeFading, UseHeaderNavigationImpossible
from story_mode.gui.scaleform.daapi.view.model.intro_video_settings_model import getSettings
from story_mode.gui.shared.utils import waitForLobby
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode_common.story_mode_constants import LOGGER_NAME, FIRST_MISSION_ID
from wg_async import wg_async, wg_await
_logger = getLogger(LOGGER_NAME)

class _ArenaLoadedChecker(IArenaLoadController):
    __slots__ = ('_isLoaded',)
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(_ArenaLoadedChecker, self).__init__()
        self._isLoaded = False

    def arenaLoadCompleted(self):
        super(_ArenaLoadedChecker, self).arenaLoadCompleted()
        self._isLoaded = True

    def isLoaded(self):
        self._isLoaded = False
        self._sessionProvider.addArenaCtrl(self)
        self._sessionProvider.removeArenaCtrl(self)
        return self._isLoaded


def ifNotArenaLoaded(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not _ArenaLoadedChecker().isLoaded():
            func(*args, **kwargs)

    return wrapper


def isViewLoaded(layoutID):
    uiLoader = dependency.instance(IGuiLoader)
    return True if not uiLoader or not uiLoader.windowsManager or uiLoader.windowsManager.getViewByLayoutID(layoutID) else False


@ifNotArenaLoaded
def showIntro(missionId):
    missionId = missionId or FIRST_MISSION_ID
    videoData = getSettings()
    isMissionHasVideo = next((mission for mission in videoData.missions if mission.id == missionId), None)
    if isMissionHasVideo:
        showIntroVideo(missionId)
    else:
        showPrebattleWindow(missionId)
    return


@ifNotArenaLoaded
def showIntroVideo(missionId):
    _logger.debug('showIntroVideo for mission with id: %s', missionId)
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.STORY_MODE_INTRO_VIDEO_WINDOW), ctx={'missionId': missionId}), EVENT_BUS_SCOPE.BATTLE)


@ifNotArenaLoaded
@UseStoryModeFading(waitForLayoutReady=R.views.story_mode.battle.PrebattleWindow())
def showPrebattleWindow(missionId):
    _logger.debug('showPrebattleWindow')
    from story_mode.gui.impl.battle.prebattle_window import PrebattleWindow
    PrebattleWindow(missionId=missionId).load()


@UseStoryModeFading(waitForLayoutReady=R.views.story_mode.battle.PrebattleWindow())
def showPrebattleAndGoToQueue(missionId):
    _logger.debug('showPrebattleAndGoToQueue')
    showPrebattleWindow(missionId=missionId)
    storyModeCtrl = dependency.instance(IStoryModeController)
    storyModeCtrl.goToQueue()


@UseStoryModeFading(waitForLayoutReady=R.views.story_mode.battle.EpilogueWindow())
def showEpilogueWindow():
    _logger.debug('showEpilogueWindow')
    from story_mode.gui.impl.battle.epilogue_window import EpilogueWindow
    EpilogueWindow().load()


@UseStoryModeFading(waitForLayoutReady=R.views.story_mode.battle.OnboardingBattleResultView())
def showOnboardingBattleResultWindow(finishReason, missionId):
    _logger.debug('showOnboardingBattleResultWindow')
    from story_mode.gui.impl.battle.onboarding_battle_result_view import OnboardingBattleResultWindow
    OnboardingBattleResultWindow(finishReason=finishReason, missionId=missionId).load()


def showQueueWindow(isSkipButtonVisible=False):
    _logger.debug('showQueueWindow: isSkipButtonVisible%s', isSkipButtonVisible)
    from story_mode.gui.impl.common.onboarding_queue_view import OnboardingQueueWindow
    window = OnboardingQueueWindow(isButtonVisible=isSkipButtonVisible)
    window.load()
    return window


@UseStoryModeFading(show=False, waitForLayoutReady=R.views.story_mode.common.CongratulationsWindow())
def showCongratulationsWindow(isCloseVisible=False, onClose=None, awardData=None):
    _logger.debug('showCongratulationsWindow')
    from story_mode.gui.impl.common.congratulations_window import CongratulationsWindow
    window = CongratulationsWindow(isCloseVisible=isCloseVisible, onClose=onClose, awardData=awardData)
    window.load()


@UseHeaderNavigationImpossible()
@UseStoryModeFading(layer=WindowLayer.TOP_SUB_VIEW, waitForLayoutReady=R.views.story_mode.lobby.MissionSelectionView())
@wg_async
def showMissionSelectionView():
    _logger.debug('showMissionSelectionView')
    contentResId = R.views.story_mode.lobby.MissionSelectionView()
    if dependency.instance(IGuiLoader).windowsManager.getViewByLayoutID(contentResId) is not None:
        sendViewLoadedEvent(contentResId)
        return
    else:
        yield wg_await(waitForLobby())
        from story_mode.gui.impl.lobby.mission_selection_view import MissionSelectionView
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, MissionSelectionView, ScopeTemplates.DEFAULT_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
        return


def showBattleResultWindow(arenaUniqueId):
    from story_mode.gui.impl.lobby.battle_result_view import BattleResultWindow
    BattleResultWindow(arenaUniqueId).load()


def sendViewLoadedEvent(layoutID):
    from story_mode.gui.shared.event import StoryModeViewReadyEvent
    g_eventBus.handleEvent(StoryModeViewReadyEvent(layoutID))


def showWelcomeWindow():
    from story_mode.gui.impl.lobby.welcome_view import WelcomeWindow
    WelcomeWindow(R.views.story_mode.lobby.WelcomeView()).load()
