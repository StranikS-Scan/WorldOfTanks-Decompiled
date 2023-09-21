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
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode_common.story_mode_constants import LOGGER_NAME
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


@ifNotArenaLoaded
def showIntroVideo():
    _logger.debug('showIntroVideo')
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.STORY_MODE_INTRO_VIDEO_WINDOW)), EVENT_BUS_SCOPE.BATTLE)


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
def showCongratulationsWindow(isCloseVisible=False, onClose=None):
    _logger.debug('showCongratulationsWindow')
    from story_mode.gui.impl.common.congratulations_window import CongratulationsWindow
    window = CongratulationsWindow(isCloseVisible=isCloseVisible, onClose=onClose)
    window.load()


@UseHeaderNavigationImpossible()
@UseStoryModeFading(layer=WindowLayer.TOP_SUB_VIEW, waitForLayoutReady=R.views.story_mode.lobby.MissionSelectionView())
def showMissionSelectionView():
    _logger.debug('showMissionSelectionView')
    contentResId = R.views.story_mode.lobby.MissionSelectionView()
    if dependency.instance(IGuiLoader).windowsManager.getViewByLayoutID(contentResId) is not None:
        sendViewLoadedEvent(contentResId)
        return
    else:
        from story_mode.gui.impl.lobby.mission_selection_view import MissionSelectionView
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(contentResId, MissionSelectionView, ScopeTemplates.DEFAULT_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
        return


def showBattleResultWindow(arenaUniqueId):
    from story_mode.gui.impl.lobby.battle_result_view import BattleResultWindow
    BattleResultWindow(arenaUniqueId).load()


def sendViewLoadedEvent(layoutID):
    from story_mode.gui.shared.event import StoryModeViewReadyEvent
    g_eventBus.handleEvent(StoryModeViewReadyEvent(layoutID))
