# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/states/player_loading.py
import typing
import game_loading_bindings
from frameworks.state_machine import StateFlags
from gui.game_loading.preferences import GameLoadingPreferences
from gui.game_loading.state_machine.const import GameLoadingStates, MINIMUM_PLAYER_LOADING_PROGRESS_BAR_MAX_VALUE
from gui.game_loading.state_machine.models import ImageViewSettingsModel
from gui.game_loading.state_machine.states.base import BaseGroupTickingStates
from gui.game_loading.state_machine.states.components.progress_bar import MilestoneProgressBarStateComponent
from gui.game_loading.state_machine.states.components.status_text import MilestoneStatusTextStateComponent
from gui.game_loading.state_machine.states.slide import SlideState
if typing.TYPE_CHECKING:
    from gui.game_loading.resources.cdn.images import CdnImagesResources
    from gui.game_loading.state_machine.models import ProgressSettingsModel as PSM

class PlayerLoadingSlideState(SlideState):
    __slots__ = ()

    def __init__(self, images, viewSettings):
        super(PlayerLoadingSlideState, self).__init__(stateID=GameLoadingStates.PLAYER_LOADING_SLIDE.value, flags=StateFlags.UNDEFINED, images=images, imageViewSettings=viewSettings, isSelfTicking=True, onCompleteEvent=None)
        return


class PlayerLoadingMilestoneProgressStateComponent(MilestoneProgressBarStateComponent):
    __slots__ = ()

    def __init__(self, preferences, settings, milestonesSettings):
        super(PlayerLoadingMilestoneProgressStateComponent, self).__init__(preferences=preferences, settings=settings, milestonesSettings=milestonesSettings, stateID=GameLoadingStates.PLAYER_LOADING_PROGRESS.value, flags=StateFlags.UNDEFINED, isSelfTicking=True, onCompleteEvent=None)
        return

    def _saveProgressMax(self, progressMax):
        minimumProgressMax = MINIMUM_PLAYER_LOADING_PROGRESS_BAR_MAX_VALUE
        progressMax = progressMax if progressMax > minimumProgressMax else minimumProgressMax
        super(PlayerLoadingMilestoneProgressStateComponent, self)._saveProgressMax(progressMax)


class PlayerLoadingStatusTextStateComponent(MilestoneStatusTextStateComponent):
    __slots__ = ()

    def __init__(self, milestonesSettings):
        super(PlayerLoadingStatusTextStateComponent, self).__init__(stateID=GameLoadingStates.PLAYER_LOADING_STATUS.value, flags=StateFlags.UNDEFINED, milestonesSettings=milestonesSettings, isSelfTicking=True, onCompleteEvent=None)
        return


class PlayerLoadingState(BaseGroupTickingStates):
    __slots__ = ()

    def __init__(self):
        super(PlayerLoadingState, self).__init__(stateID=GameLoadingStates.PLAYER_LOADING.value, flags=StateFlags.PARALLEL | StateFlags.UNDEFINED)

    @property
    def mainState(self):
        return self.getChildByIndex(0)

    @property
    def progressState(self):
        return self.getChildByIndex(1)

    @property
    def statusTextState(self):
        return self.getChildByIndex(2)

    def configure(self, preferences, images, progressSetting, milestonesSettings, viewSettings):
        playerLoadingSlideState = PlayerLoadingSlideState(images=images, viewSettings=viewSettings)
        playerLoadingProgressMixinState = PlayerLoadingMilestoneProgressStateComponent(preferences=preferences, settings=progressSetting, milestonesSettings=milestonesSettings)
        playerLoadingStatusTextComponent = PlayerLoadingStatusTextStateComponent(milestonesSettings=milestonesSettings)
        playerLoadingSlideState.configure()
        playerLoadingProgressMixinState.configure()
        playerLoadingStatusTextComponent.configure()
        self.addChildState(playerLoadingSlideState)
        self.addChildState(playerLoadingProgressMixinState)
        self.addChildState(playerLoadingStatusTextComponent)

    def setRetainMilestones(self, value):
        self.progressState.setRetainMilestones(value)
        self.statusTextState.setRetainMilestones(value)

    def _onEntered(self):
        super(PlayerLoadingState, self)._onEntered()
        game_loading_bindings.bringLoadingViewToTop()
