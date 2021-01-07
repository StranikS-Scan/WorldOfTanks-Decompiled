# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PlatoonLighting.py
import logging
from enum import Enum
import BigWorld
import AnimationSequence
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from skeletons.gui.game_control import IPlatoonController
from vehicle_systems.stricted_loading import makeCallbackWeak
from ClientSelectableObject import ClientSelectableObject
from helpers import dependency
_logger = logging.getLogger(__name__)

class _PlatoonLightingStateMachineTriggers(Enum):
    PLATOON_LEFT_ENTER = 'PlatoonLeftEnter'
    PLATOON_LEFT_EXIT = 'PlatoonLeftExit'
    PLATOON_RIGHT_ENTER = 'PlatoonRightEnter'
    PLATOON_RIGHT_EXIT = 'PlatoonRightExit'
    PLATOON_PLAYER_ENTER = 'PlatoonPlayerEnter'
    PLATOON_PLAYER_EXIT = 'PlatoonPlayerExit'


class _PlatoonLightingStateMachineStates(Enum):
    PLAYER_ORIGINAL_LIGHTING = 'PlayerOriginalLighting'
    PLAYER_PLATOON_LIGHTING = 'PlayerPlatoonLighting'
    RIGHT_TANK_READY = 'PlatoonRightTankReady'
    LEFT_TANK_READY = 'PlatoonLeftTankReady'
    FULL_PLATOON = 'PlatoonBothTanksReady'


class PlatoonLighting(ClientSelectableObject):
    __platoonController = dependency.descriptor(IPlatoonController)

    def __init__(self):
        super(PlatoonLighting, self).__init__()
        self.__animator = None
        return

    def onEnterWorld(self, prereqs):
        _logger.debug('Starting platoon lighting state machine.')
        if self.animationStateMachine:
            animationLoader = AnimationSequence.Loader(self.animationStateMachine, self.spaceID)
            BigWorld.loadResourceListBG((animationLoader,), makeCallbackWeak(self.__onAnimatorLoaded))
        super(PlatoonLighting, self).onEnterWorld(prereqs)

    def onLeaveWorld(self):
        _logger.debug('Stopping platoon lighting state machine.')
        super(PlatoonLighting, self).onLeaveWorld()
        if self.__animator is not None:
            self.__animator.stop()
            self.__animator = None
            g_eventBus.removeListener(events.HangarVehicleEvent.ON_PLATOON_TANK_LOADED, self.__onPlatoonTankEnter, scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.removeListener(events.HangarVehicleEvent.ON_PLATOON_TANK_DESTROY, self.__onPlatoonTankLeave, scope=EVENT_BUS_SCOPE.LOBBY)
            self.__platoonController.onPlatoonTankVisualizationChanged -= self.__enablePlatoonLighting
        return

    def __enterPlatoon(self):
        name = self.__animator.getCurrNodeName()
        _logger.debug('Entering platoon %s.', name)
        if name == _PlatoonLightingStateMachineStates.PLAYER_ORIGINAL_LIGHTING.value:
            self.__animator.setTrigger(_PlatoonLightingStateMachineTriggers.PLATOON_PLAYER_ENTER.value)

    def __onAnimatorLoaded(self, resourceList):
        if self.animationStateMachine in resourceList.failedIDs:
            return
        elif self.model is None:
            _logger.error('Could not spawn animation "%s", because model is not loaded: "%s"', self.animationStateMachine, self.modelName)
            return
        else:
            self.__animator = resourceList[self.animationStateMachine]
            self.__animator.bindTo(AnimationSequence.ModelWrapperContainer(self.model, self.spaceID))
            self.__animator.start()
            g_eventBus.addListener(events.HangarVehicleEvent.ON_PLATOON_TANK_LOADED, self.__onPlatoonTankEnter, scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.addListener(events.HangarVehicleEvent.ON_PLATOON_TANK_DESTROY, self.__onPlatoonTankLeave, scope=EVENT_BUS_SCOPE.LOBBY)
            self.__platoonController.onPlatoonTankVisualizationChanged += self.__enablePlatoonLighting
            return

    def __onPlatoonTankEnter(self, event):
        name = self.__animator.getCurrNodeName()
        if name == _PlatoonLightingStateMachineStates.FULL_PLATOON.value:
            return
        _logger.debug('Tank entering platoon %s.', name)
        entity = event.ctx['entity']
        if entity.slotIndex == 0:
            if name != _PlatoonLightingStateMachineStates.RIGHT_TANK_READY.value:
                self.__animator.setTrigger(_PlatoonLightingStateMachineTriggers.PLATOON_RIGHT_ENTER.value)
        elif name != _PlatoonLightingStateMachineStates.LEFT_TANK_READY.value:
            self.__animator.setTrigger(_PlatoonLightingStateMachineTriggers.PLATOON_LEFT_ENTER.value)

    def __onPlatoonTankLeave(self, event):
        name = self.__animator.getCurrNodeName()
        if name in (_PlatoonLightingStateMachineStates.PLAYER_PLATOON_LIGHTING.value, _PlatoonLightingStateMachineStates.PLAYER_ORIGINAL_LIGHTING.value):
            return
        _logger.debug('Tank leave platoon %s.', name)
        entity = event.ctx['entity']
        if entity.slotIndex == 0:
            if name != _PlatoonLightingStateMachineStates.LEFT_TANK_READY.value:
                self.__animator.setTrigger(_PlatoonLightingStateMachineTriggers.PLATOON_RIGHT_EXIT.value)
        elif name != _PlatoonLightingStateMachineStates.RIGHT_TANK_READY.value:
            self.__animator.setTrigger(_PlatoonLightingStateMachineTriggers.PLATOON_LEFT_EXIT.value)

    def __leavePlatoon(self):
        name = self.__animator.getCurrNodeName()
        _logger.debug('Leaving platoon %s.', name)
        if name != _PlatoonLightingStateMachineStates.PLAYER_ORIGINAL_LIGHTING.value:
            self.__animator.setTrigger(_PlatoonLightingStateMachineTriggers.PLATOON_PLAYER_EXIT.value)

    def __enablePlatoonLighting(self, isEnabled):
        if isEnabled:
            self.__enterPlatoon()
        else:
            self.__leavePlatoon()
