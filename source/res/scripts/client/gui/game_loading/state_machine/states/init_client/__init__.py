# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/states/init_client/__init__.py
import typing
from frameworks.state_machine import StateFlags
from gui.game_loading import loggers
from gui.game_loading.state_machine.const import GameLoadingStates
from gui.game_loading.state_machine.states.base import BaseGroupTickingStates
from gui.game_loading.state_machine.states.init_client.client_loading import ClientLoadingState, ClientLoadingSlideState
from gui.game_loading.state_machine.states.init_client.client_loading_stub import ClientLoadingStubState
from gui.game_loading.state_machine.states.init_client.logos_loading import LogosLoadingState
from gui.game_loading.state_machine.states.init_client.transitions import LogosShownToClientLoadingStubTransition, LogosShownToClientLoadingTransition, ClientLoadingTransition
if typing.TYPE_CHECKING:
    from frameworks.state_machine.transitions import BaseTransition
    from gui.game_loading.resources.cdn.images import CdnImagesResources
    from gui.game_loading.preferences import GameLoadingPreferences
    from gui.game_loading.resources.local.base import LocalResources
    from gui.game_loading.state_machine.states.base import BaseState
    from gui.game_loading.state_machine.models import ProgressSettingsModel as PSM, ImageViewSettingsModel
_logger = loggers.getStatesLogger()

class ClientInitState(BaseGroupTickingStates):
    __slots__ = ()

    def __init__(self):
        super(ClientInitState, self).__init__(stateID=GameLoadingStates.CLIENT_INIT.value, flags=StateFlags.INITIAL | StateFlags.SINGULAR)

    def configure(self, preferences, logos, clientLoadingImages, milestonesSettings, clientLoadingProgressSetting, clientLoadingViewSettings):
        logosLoadingState = LogosLoadingState(logos, clientLoadingViewSettings.ageRatingPath)
        clientLoadingState = ClientLoadingState()
        clientLoadingStubState = ClientLoadingStubState(clientLoadingImages)
        logosLoadingState.configure()
        clientLoadingState.configure(preferences=preferences, images=clientLoadingImages, milestonesSettings=milestonesSettings, progressSetting=clientLoadingProgressSetting, viewSettings=clientLoadingViewSettings)
        clientLoadingStubState.configure()
        self.initWaiting()
        clientLoadingState.mainState.initWaiting(self._waiting)
        clientLoadingStubState.initWaiting(self._waiting)
        logosLoadingState.addTransition(LogosShownToClientLoadingStubTransition(), target=clientLoadingStubState)
        logosLoadingState.addTransition(LogosShownToClientLoadingTransition(), target=clientLoadingState)
        logosLoadingState.addTransition(ClientLoadingTransition(), target=clientLoadingState)
        self.addChildState(logosLoadingState)
        self.addChildState(clientLoadingState)
        self.addChildState(clientLoadingStubState)

    def addTransitionToGroupState(self, transitionFactory, target=None):
        self._logosLoadingState.addTransition(transitionFactory(), target=target)
        self._clientLoadingState.mainState.addTransition(transitionFactory(), target=target)
        self._clientLoadingStubState.addTransition(transitionFactory(), target=target)

    @property
    def _logosLoadingState(self):
        return self.getChildByIndex(0)

    @property
    def _clientLoadingState(self):
        return self.getChildByIndex(1)

    @property
    def _clientLoadingStubState(self):
        return self.getChildByIndex(2)
