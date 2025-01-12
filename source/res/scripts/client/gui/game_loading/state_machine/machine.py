# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/machine.py
import typing
from functools import wraps
import wg_async
from frameworks.state_machine import StateMachine, StringEvent
from gui.game_loading import loggers
from gui.game_loading.resources.cdn.images import CdnImagesResources
from gui.game_loading.resources.consts import LoadingTypes
from gui.game_loading.resources.local.base import LocalResources
from gui.game_loading.state_machine.const import GameLoadingStatesEvents, GameLoadingStates, DEFAULT_WAITING_TIMEOUT
from gui.game_loading.state_machine.states.base import BaseTickingState, BaseGroupTickingStates
from gui.game_loading.state_machine.states.init_client import ClientInitState
from gui.game_loading.state_machine.states.login_screen import LoginScreenState
from gui.game_loading.state_machine.states.player_loading import PlayerLoadingState
from gui.game_loading.state_machine.states.idle import IdleState
from gui.game_loading.state_machine.states.transitions import LoginScreenTransition, LoginScreenTransitionWithLastShownImage, PlayerLoadingTransition, ClientInitToPlayerLoadingTransition, LoginScreenToPlayerLoadingTransition, IdleTransition
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
    __slots__ = ('_cdnImages', '_logos', '_isGameLoadingComplete')

    def __init__(self):
        super(GameLoadingStateMachine, self).__init__()
        self._cdnImages = None
        self._logos = None
        self._isGameLoadingComplete = False
        return

    @property
    def isGameLoadingComplete(self):
        return self._isGameLoadingComplete

    @_ifNotRunning()
    def setGameLoadingComplete(self):
        _logger.debug('Game loading completed.')
        self._isGameLoadingComplete = True

    def stop(self):
        self.idle()
        self._isGameLoadingComplete = False
        super(GameLoadingStateMachine, self).stop()
        if self._cdnImages:
            self._cdnImages.destroy()
        if self._logos:
            self._logos.destroy()

    @_ifNotRunning()
    def post(self, event):
        super(GameLoadingStateMachine, self).post(event)

    def configure(self, preferences, settings):
        self._cdnImages = CdnImagesResources(settings.getCdnCacheDefaults())
        self._logos = LocalResources(settings.getLogos(), cycle=False)
        loginNextSlideDuration = settings.getLoginNextSlideDuration()
        clientProgressMilestones = settings.getProgressMilestones(LoadingTypes.CLIENT)
        clientProgressSettings = settings.getProgressSettingsByType(LoadingTypes.CLIENT)
        playerProgressSettings = settings.getProgressSettingsByType(LoadingTypes.PLAYER)
        playerProgressMilestones = settings.getProgressMilestones(LoadingTypes.PLAYER)
        clientLoadingViewSettings = settings.getClientLoadingStateViewSettings()
        loginViewSettings = settings.getLoginStateViewSettings()
        playerLoadingViewSettings = settings.getPlayerLoadingStateViewSettings()
        clientInitState = ClientInitState()
        loginScreenState = LoginScreenState(self._cdnImages, loginNextSlideDuration, loginViewSettings)
        playerLoadingState = PlayerLoadingState()
        idleState = IdleState()
        clientInitState.configure(preferences=preferences, logos=self._logos, clientLoadingImages=self._cdnImages, milestonesSettings=clientProgressMilestones, clientLoadingProgressSetting=clientProgressSettings, clientLoadingViewSettings=clientLoadingViewSettings)
        loginScreenState.configure()
        playerLoadingState.configure(preferences=preferences, images=self._cdnImages, progressSetting=playerProgressSettings, milestonesSettings=playerProgressMilestones, viewSettings=playerLoadingViewSettings)
        idleState.configure()
        clientInitState.addTransitionToGroupState(LoginScreenTransitionWithLastShownImage, target=loginScreenState)
        clientInitState.addTransitionToGroupState(ClientInitToPlayerLoadingTransition, target=playerLoadingState)
        clientInitState.addTransitionToGroupState(IdleTransition, target=idleState)
        loginScreenState.addTransition(LoginScreenToPlayerLoadingTransition(), target=playerLoadingState)
        loginScreenState.addTransition(IdleTransition(), target=idleState)
        playerLoadingState.mainState.addTransition(LoginScreenTransitionWithLastShownImage(), target=loginScreenState)
        playerLoadingState.mainState.addTransition(IdleTransition(), target=idleState)
        idleState.addTransition(LoginScreenTransition(), target=loginScreenState)
        idleState.addTransition(PlayerLoadingTransition(), target=playerLoadingState)
        self.addState(clientInitState)
        self.addState(loginScreenState)
        self.addState(playerLoadingState)
        self.addState(idleState)

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
    def loginScreen(self):
        self.post(StringEvent(GameLoadingStatesEvents.LOGIN_SCREEN.value))

    @_ifNotRunning()
    def playerLoading(self, retainMilestones=False):
        self.post(StringEvent(GameLoadingStatesEvents.PLAYER_LOADING.value, retainMilestones=retainMilestones))

    @_ifNotRunning()
    def idle(self):
        self.post(StringEvent(GameLoadingStatesEvents.IDLE.value))

    @property
    def isLoading(self):
        return not self.isStateEntered(GameLoadingStates.IDLE.value)

    @wg_async.wg_async
    def wait(self, timeout=DEFAULT_WAITING_TIMEOUT):
        if not self.isRunning():
            _logger.error('Cannot wait. State machine is not running.')
            raise wg_async.AsyncReturn(None)
        for state in self.getChildrenStates():
            if self.isStateEntered(state.getStateID()):
                try:
                    yield wg_async.wg_await(state.wait(), timeout=timeout)
                except wg_async.TimeoutError:
                    _logger.warning('Waiting timeout <%s> reached.', timeout)
                except wg_async.BrokenPromiseError:
                    _logger.debug('State has been changed while waiting.')

                raise wg_async.AsyncReturn(None)

        return
