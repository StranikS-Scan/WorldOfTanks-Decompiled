# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_logging/mechanic_input_logger.py
from __future__ import absolute_import
import json
import logging
import typing
import weakref
from functools import partial
import BigWorld
import constants
from events_containers.common.containers import ContainersListener
from events_containers.components.life_cycle import IComponentLifeCycleListenerLogic
from events_handler import eventHandler
from uilogging.base.logger import MetricsLogger
from uilogging.constants import InputLogActions
from wotdecorators import noexcept
if constants.IS_CLIENT:
    import Input
    from Input import KeyInputAction, InputTriggerPressed, TriggerEvent, InputLayer
if typing.TYPE_CHECKING:
    from events_containers.components.life_cycle import ILifeCycleComponent
    from vehicles.mechanics.mechanic_logging.mechanic_interfaces import IMechanicInputLoggingComponent
_logger = logging.getLogger(__name__)
_MECHANIC_INPUT_LOGGING_FEATURE_NAME = 'mechanic_input'

class MechanicInputLogger(ContainersListener, IComponentLifeCycleListenerLogic):
    _INPUT_PROFILE_NAME = 'MECHANIC_INPUT_PROFILE'

    def __init__(self, mechanicComponent, *commands):
        super(MechanicInputLogger, self).__init__()
        self._mechanicComponent = weakref.ref(mechanicComponent)
        self._uiLogger = MetricsLogger(_MECHANIC_INPUT_LOGGING_FEATURE_NAME)
        actions = []
        for command in commands:
            actionName = '{}_log_input'.format(command)
            action = KeyInputAction(actionName, command, [InputTriggerPressed()], isConsuming=False)
            action.bindEventReaction(TriggerEvent.Triggered, partial(self.log, command))
            actions.append(action)

        Input.inputSystem().addProfile(self._INPUT_PROFILE_NAME, InputLayer.AVATAR_INPUT_LAYER, actions, priority=0)
        self.__arenaUniqueID = None
        self.__vehCD = None
        mechanicComponent.lifeCycleEvents.lateSubscribe(self)
        return

    def start(self):
        if self._uiLogger.disabled:
            _logger.info('UILogger disabled')
            return
        player = BigWorld.player()
        typeDescr = player.vehicle.typeDescriptor
        self.__vehCD = typeDescr.type.compactDescr
        self.__arenaUniqueID = player.arenaUniqueID
        Input.inputSystem().activateProfile(self._INPUT_PROFILE_NAME)

    def destroy(self):
        Input.inputSystem().removeProfile(self._INPUT_PROFILE_NAME)
        self._mechanicComponent = None
        self._uiLogger = None
        self.__vehCD = None
        self.__arenaUniqueID = None
        return

    @eventHandler
    def onComponentDestroyed(self, component):
        self.destroy()

    @noexcept
    def log(self, triggeredAction):
        if self._mechanicComponent() is not None:
            logRecord = {'arena_id': self.__arenaUniqueID}
            logRecord.update(self._mechanicComponent().getMechanicLogState())
            self._uiLogger.log(action=str(triggeredAction), item=str(self.__vehCD), itemState=InputLogActions.TRIGGERED, info=json.dumps(logRecord))
        return
