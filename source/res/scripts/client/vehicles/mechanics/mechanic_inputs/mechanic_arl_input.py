# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_inputs/mechanic_arl_input.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
import BigWorld
from aih_constants import CTRL_MODE_NAME
from events_handler import eventHandler
from gui.battle_control import avatar_getter
from vehicles.mechanics.mechanic_inputs.mechanic_base_input import BaseMechanicInput
from vehicles.mechanics.mechanic_inputs.mechanic_input_profile import MechanicInputProfile, PlayerVehicleInputPredicate
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if TYPE_CHECKING:
    from vehicles.mechanics.gun_mechanics.auxiliary_rocket_launcher import AuxiliaryRocketLauncherState

class AuxiliaryRocketLauncherInputPredicate(PlayerVehicleInputPredicate):

    def __call__(self):
        if not super(AuxiliaryRocketLauncherInputPredicate, self).__call__():
            return False
        else:
            player = BigWorld.player()
            if player is None or not player.isOnArena:
                return False
            inputHandler = avatar_getter.getInputHandler()
            return inputHandler is not None and inputHandler.ctrlModeName in (CTRL_MODE_NAME.ARCADE, CTRL_MODE_NAME.SNIPER)


class AuxiliaryRocketLauncherInput(BaseMechanicInput, IMechanicStatesListenerLogic):

    def __init__(self, component, switchModeProfileName, switchModeActionName, activateProfileName, activateActionName, switchModeCallback, activateCallback):
        super(AuxiliaryRocketLauncherInput, self).__init__()
        vehicle = component.entity
        self._register(MechanicInputProfile(vehicle, switchModeProfileName, switchModeActionName, switchModeCallback))
        self.__activateProfile = self._register(MechanicInputProfile(vehicle, activateProfileName, activateActionName, activateCallback, predicateFactory=AuxiliaryRocketLauncherInputPredicate, activateOnAttach=False))

    @eventHandler
    def onStatePrepared(self, state):
        if state.isInAimingMode:
            self.__activateProfile.activate()

    @eventHandler
    def onStateTransition(self, prevState, newState):
        if prevState.isInAimingMode == newState.isInAimingMode:
            return
        if newState.isInAimingMode:
            self.__activateProfile.activate()
        else:
            self.__activateProfile.deactivate()
