# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/machine.py
from functools import wraps
import typing
from frameworks.state_machine import StateMachine, StringEvent
from gui.game_loading import loggers
from gui.game_loading.resources.cdn.images import CdnImagesResources
from gui.game_loading.resources.consts import LoadingTypes
from gui.game_loading.resources.local.base import LocalResources
from gui.game_loading.state_machine.const import GameLoadingStatesEvents
from gui.game_loading.state_machine.states.base import BaseTickingState, BaseGroupTickingStates
from gui.game_loading.state_machine.states.client_loading import ClientLoadingState
from gui.game_loading.state_machine.states.idl import IdlState
from gui.game_loading.state_machine.states.login_screen import LoginScreenState
from gui.game_loading.state_machine.states.logos_loading import LogosLoadingState
from gui.game_loading.state_machine.states.player_loading import PlayerLoadingState
from gui.game_loading.state_machine.transitions import LoginScreenTransition, LogosShownTransition, ClientLoadingTransition, PlayerLoadingTransition, IdlTransition
if typing.TYPE_CHECKING:
    from frameworks.state_machine import StateEvent
    from gui.game_loading.settings import GameLoadingSettings
    from gui.game_loading.preferences import GameLoadingPreferences
_logger = loggers.getStateMachineLogger()

def _ifNotRunning(result=None):

    def inner(function):

        @wraps(function)
        def wrapper(self, *args, **kwargs):
            if not self.isRunning():
                _logger.warning('State machine is not running. Skipping %s call with result: %s.', function, result)
                return result
            return function(self, *args, **kwargs)

        return wrapper

    return inner


class GameLoadingStateMachine(StateMachine):
    __slots__ = ('_cdnImages', '_logos', '_statusTexts')

    def __init__(self):
        super(GameLoadingStateMachine, self).__init__()
        self._cdnImages = None
        self._logos = None
        self._statusTexts = None
        return

    def stop(self):
        self.idl()
        super(GameLoadingStateMachine, self).stop()
        if self._cdnImages:
            self._cdnImages.destroy()
        if self._logos:
            self._logos.destroy()
        if self._statusTexts:
            self._statusTexts.destroy()

    @_ifNotRunning()
    def post(self, event):
        super(GameLoadingStateMachine, self).post(event)

    def configure(self, preferences, settings):
        self._cdnImages = CdnImagesResources(settings.getCdnCacheDefaults())
        self._logos = LocalResources(settings.getLogos(), cycle=False)
        self._statusTexts = LocalResources(settings.getStatusTexts(), cycle=False)
        loginNextSlideDuration = settings.getLoginNextSlideDuration()
        clientProgressSettings = settings.getProgressSettingsByType(LoadingTypes.CLIENT)
        playerProgressSettings = settings.getProgressSettingsByType(LoadingTypes.PLAYER)
        playerProgressMilestones = settings.getProgressMilestones(LoadingTypes.PLAYER)
        clientLoadingViewSettings = settings.getClientLoadingStateViewSettings()
        loginViewSettings = settings.getLoginStateViewSettings()
        playerLoadingViewSettings = settings.getPlayerLoadingStateViewSettings()
        logosLoadingState = LogosLoadingState(self._logos, clientLoadingViewSettings.ageRatingPath)
        clientLoadingState = ClientLoadingState()
        loginScreenState = LoginScreenState(self._cdnImages, loginNextSlideDuration, loginViewSettings)
        playerLoadingState = PlayerLoadingState()
        idlState = IdlState()
        logosLoadingState.configure()
        clientLoadingState.configure(preferences=preferences, images=self._cdnImages, texts=self._statusTexts, progressSetting=clientProgressSettings, viewSettings=clientLoadingViewSettings)
        loginScreenState.configure()
        playerLoadingState.configure(preferences=preferences, images=self._cdnImages, progressSetting=playerProgressSettings, milestonesSettings=playerProgressMilestones, viewSettings=playerLoadingViewSettings)
        idlState.configure()
        logosLoadingState.addTransition(LogosShownTransition(), target=clientLoadingState)
        logosLoadingState.addTransition(ClientLoadingTransition(), target=clientLoadingState)
        logosLoadingState.addTransition(LoginScreenTransition(), target=loginScreenState)
        logosLoadingState.addTransition(IdlTransition(), target=idlState)
        clientLoadingState.mainState.addTransition(LoginScreenTransition(), target=loginScreenState)
        clientLoadingState.mainState.addTransition(PlayerLoadingTransition(), target=playerLoadingState)
        clientLoadingState.mainState.addTransition(IdlTransition(), target=idlState)
        loginScreenState.addTransition(PlayerLoadingTransition(), target=playerLoadingState)
        loginScreenState.addTransition(IdlTransition(), target=idlState)
        playerLoadingState.mainState.addTransition(LoginScreenTransition(), target=loginScreenState)
        playerLoadingState.mainState.addTransition(IdlTransition(), target=idlState)
        idlState.addTransition(LoginScreenTransition(), target=loginScreenState)
        idlState.addTransition(PlayerLoadingTransition(), target=playerLoadingState)
        self.addState(logosLoadingState)
        self.addState(clientLoadingState)
        self.addState(loginScreenState)
        self.addState(playerLoadingState)
        self.addState(idlState)

    @_ifNotRunning()
    def onConnected(self):
        if self._cdnImages:
            self._cdnImages.onConnected()

    @_ifNotRunning()
    def onDisconnected(self):
        if self._cdnImages:
            self._cdnImages.onDisconnected()

    @_ifNotRunning()
    def tick(self, stepNumber):
        for state in self.getChildrenStates():
            isTickingState = isinstance(state, (BaseTickingState, BaseGroupTickingStates))
            if isTickingState and self.isStateEntered(state.getStateID()):
                state.manualTick(stepNumber)

    @_ifNotRunning()
    def clientLoading(self):
        self.post(StringEvent(GameLoadingStatesEvents.CLIENT_LOADING.value))

    @_ifNotRunning()
    def loginScreen(self):
        self.post(StringEvent(GameLoadingStatesEvents.LOGIN_SCREEN.value))

    @_ifNotRunning()
    def playerLoading(self, retainMilestones=False):
        self.post(StringEvent(GameLoadingStatesEvents.PLAYER_LOADING.value, retainMilestones=retainMilestones))

    @_ifNotRunning()
    def idl(self):
        self.post(StringEvent(GameLoadingStatesEvents.IDL.value))
