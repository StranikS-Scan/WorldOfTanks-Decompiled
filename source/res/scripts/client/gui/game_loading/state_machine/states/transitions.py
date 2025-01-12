# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/states/transitions.py
import typing
from frameworks.state_machine.transitions import StringEventTransition
from gui.game_loading import loggers
from gui.game_loading.resources.cdn.models import LocalSlideModel
from gui.game_loading.state_machine.const import GameLoadingStatesEvents
if typing.TYPE_CHECKING:
    from frameworks.state_machine.events import StringEvent
    from gui.game_loading.state_machine.states.base import BaseState
    from gui.game_loading.state_machine.states.login_screen import LoginScreenState
    from gui.game_loading.state_machine.states.player_loading import PlayerLoadingState
    from gui.game_loading.state_machine.states.init_client.logos_loading import LogosLoadingState
    from gui.game_loading.state_machine.states.init_client.client_loading import ClientLoadingSlideState
    from gui.game_loading.state_machine.states.init_client.client_loading_stub import ClientLoadingStubState
    _ClientInitStates = typing.Union[LogosLoadingState, ClientLoadingSlideState, ClientLoadingStubState]
_logger = loggers.getTransitionsLogger()

class SourceToSingleTargetTransition(StringEventTransition):
    __slots__ = ()

    def execute(self, event):
        result = super(SourceToSingleTargetTransition, self).execute(event)
        if result:
            targetList = self.getTargets()
            if len(targetList) != 1:
                _logger.error('Single target from source transition assigned to multiple|none targets. %s', self)
                return False
            source = self.getSource()
            if not source:
                _logger.error('Single target from source transition missing source. %s', self)
                return False
            result = self._apply(event, source, targetList[0])
        return result

    def _apply(self, event, source, target):
        return True


class LoginScreenTransition(SourceToSingleTargetTransition):
    __slots__ = ()

    def __init__(self, priority=0):
        super(LoginScreenTransition, self).__init__(token=GameLoadingStatesEvents.LOGIN_SCREEN.value, priority=priority)


class LoginScreenTransitionWithLastShownImage(LoginScreenTransition):
    __slots__ = ()

    def _apply(self, event, source, target):
        image = source.lastShownImage
        if image:
            target.setImage(image)
        return True


class PlayerLoadingTransition(SourceToSingleTargetTransition):
    __slots__ = ()

    def __init__(self, priority=0):
        super(PlayerLoadingTransition, self).__init__(token=GameLoadingStatesEvents.PLAYER_LOADING.value, priority=priority)


class PlayerLoadingTransitionWithLastShownImage(PlayerLoadingTransition):
    __slots__ = ()

    def _apply(self, event, source, target):
        image = source.lastShownImage
        if image:
            slide = LocalSlideModel(imageRelativePath=image.imageRelativePath, minShowTimeSec=self._getMinShowTime(source, image), localizationText=image.localizationText, descriptionText=image.descriptionText, vfx=image.vfx)
            target.setRetainMilestones(event.getArgument('retainMilestones', False))
            target.mainState.setImage(slide)
        return True

    def _getMinShowTime(self, source, image):
        return image.minShowTimeSec


class ClientInitToPlayerLoadingTransition(PlayerLoadingTransitionWithLastShownImage):
    __slots__ = ()

    def _getMinShowTime(self, source, image):
        return max(source.timeLeft, 0)


class LoginScreenToPlayerLoadingTransition(PlayerLoadingTransitionWithLastShownImage):
    __slots__ = ()

    def _getMinShowTime(self, source, image):
        return max(source.nextSlideDuration, 0)


class IdleTransition(StringEventTransition):
    __slots__ = ()

    def __init__(self, priority=0):
        super(IdleTransition, self).__init__(token=GameLoadingStatesEvents.IDLE.value, priority=priority)
