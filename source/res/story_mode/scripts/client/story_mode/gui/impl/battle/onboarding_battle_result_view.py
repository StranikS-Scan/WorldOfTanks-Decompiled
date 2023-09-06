# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/battle/onboarding_battle_result_view.py
from functools import partial
import typing
from frameworks.wulf import WindowFlags, ViewSettings
from gui.app_loader import app_getter
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from helpers import dependency
from story_mode.gui.fade_in_out import UseStoryModeFading
from story_mode.gui.impl.gen.view_models.views.battle.onboarding_battle_result_view_model import OnboardingBattleResultViewModel
from story_mode.gui.impl.mixins import DestroyWindowOnDisconnectMixin
from story_mode.gui.shared.event_dispatcher import showPrebattleAndGoToQueue, sendViewLoadedEvent
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode.uilogging.story_mode.consts import LogButtons
from story_mode.uilogging.story_mode.loggers import PostBattleWindowLogger
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.application import AppEntry

class OnboardingBattleResultView(ViewImpl):
    __slots__ = ('_finishReason', '_missionId', '_uiLogger')
    LAYOUT_ID = R.views.story_mode.battle.OnboardingBattleResultView()
    _storyModeCtrl = dependency.descriptor(IStoryModeController)

    def __init__(self, finishReason, missionId):
        settings = ViewSettings(self.LAYOUT_ID)
        settings.model = OnboardingBattleResultViewModel()
        super(OnboardingBattleResultView, self).__init__(settings)
        self._finishReason = finishReason
        self._missionId = missionId
        self._uiLogger = PostBattleWindowLogger()

    @property
    def viewModel(self):
        return super(OnboardingBattleResultView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(OnboardingBattleResultView, self)._onLoading(*args, **kwargs)
        self.viewModel.setCauseText(self._finishReason)
        self.viewModel.setMissionId(self._missionId)

    def _onLoaded(self, *args, **kwargs):
        super(OnboardingBattleResultView, self)._onLoaded(*args, **kwargs)
        self._uiLogger.logOpen(missionId=self._missionId, win=False)

    def _finalize(self):
        self._uiLogger.logClose()
        super(OnboardingBattleResultView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onContinue, self.__onContinueButtonClick), (self.viewModel.onLoaded, partial(sendViewLoadedEvent, self.LAYOUT_ID)))

    @UseStoryModeFading(hide=False)
    def __onContinueButtonClick(self):
        self._uiLogger.logClick(LogButtons.RESTART_BATTLE)
        if not self._storyModeCtrl.settings.enabled:
            self._storyModeCtrl.goToHangar()
        else:
            showPrebattleAndGoToQueue(missionId=self._missionId)
        self.destroyWindow()


class OnboardingBattleResultWindow(DestroyWindowOnDisconnectMixin, WindowImpl):
    __slots__ = ()

    @app_getter
    def app(self):
        return None

    def __init__(self, finishReason, missionId):
        super(OnboardingBattleResultWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=OnboardingBattleResultView(finishReason=finishReason, missionId=missionId))

    def _onContentReady(self):
        super(OnboardingBattleResultWindow, self)._onContentReady()
        self.app.attachCursor()
