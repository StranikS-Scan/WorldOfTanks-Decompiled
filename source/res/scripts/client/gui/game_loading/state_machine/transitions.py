# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/transitions.py
import typing
from frameworks.state_machine.transitions import StringEventTransition
from gui.game_loading.resources.cdn.models import LocalSlideModel
from gui.game_loading.state_machine.const import GameLoadingStatesEvents
from gui.game_loading.state_machine.states.client_loading import ClientLoadingSlideState
from gui.game_loading.state_machine.states.login_screen import LoginScreenState
from gui.game_loading.state_machine.states.player_loading import PlayerLoadingState
from gui.game_loading.state_machine.states.slide import SlideState
if typing.TYPE_CHECKING:
    from frameworks.state_machine.events import StringEvent

class LogosShownTransition(StringEventTransition):
    __slots__ = ()

    def __init__(self, priority=0):
        super(LogosShownTransition, self).__init__(token=GameLoadingStatesEvents.LOGOS_SHOWN.value, priority=priority)


class ClientLoadingTransition(StringEventTransition):
    __slots__ = ()

    def __init__(self, priority=0):
        super(ClientLoadingTransition, self).__init__(token=GameLoadingStatesEvents.CLIENT_LOADING.value, priority=priority)


class PlayerLoadingTransition(StringEventTransition):
    __slots__ = ()

    def __init__(self, priority=0):
        super(PlayerLoadingTransition, self).__init__(token=GameLoadingStatesEvents.PLAYER_LOADING.value, priority=priority)

    def execute(self, event):
        result = super(PlayerLoadingTransition, self).execute(event)
        if result:
            source = self.getSource()
            if source:
                image = None
                nextSlideDuration = 0
                vfx = None
                if isinstance(source, LoginScreenState):
                    image = source.lastShownImage
                    if image:
                        nextSlideDuration = max(source.nextSlideDuration, 0)
                        vfx = image.vfx
                elif isinstance(source, ClientLoadingSlideState):
                    image = source.lastShownImage
                    if image:
                        nextSlideDuration = max(source.timeLeft, 0)
                if image is not None:
                    slide = LocalSlideModel(imageRelativePath=image.imageRelativePath, minShowTimeSec=nextSlideDuration, localizationText=image.localizationText, descriptionText=image.descriptionText, vfx=vfx)
                    targetList = self.getTargets()
                    for target in targetList:
                        if isinstance(target, PlayerLoadingState):
                            target.setRetainMilestones(event.getArgument('retainMilestones', False))
                            target.mainState.setImage(slide)

        return result


class IdlTransition(StringEventTransition):
    __slots__ = ()

    def __init__(self, priority=0):
        super(IdlTransition, self).__init__(token=GameLoadingStatesEvents.IDL.value, priority=priority)


class LoginScreenTransition(StringEventTransition):
    __slots__ = ()

    def __init__(self, priority=0):
        super(LoginScreenTransition, self).__init__(token=GameLoadingStatesEvents.LOGIN_SCREEN.value, priority=priority)

    def execute(self, event):
        result = super(LoginScreenTransition, self).execute(event)
        if result:
            source = self.getSource()
            if not source or not isinstance(source, SlideState):
                return result
            image = source.lastShownImage
            if not image:
                return result
            for target in self.getTargets():
                if target and isinstance(target, LoginScreenState):
                    target.setImage(image)
                    break

        return result
