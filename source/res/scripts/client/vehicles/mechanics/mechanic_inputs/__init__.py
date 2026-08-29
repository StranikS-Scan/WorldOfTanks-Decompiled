# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_inputs/__init__.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
from vehicles.mechanics.mechanic_inputs.mechanic_arl_input import AuxiliaryRocketLauncherInput
from vehicles.mechanics.mechanic_inputs.mechanic_single_input import MechanicSingleInput
if TYPE_CHECKING:
    from typing import Any, Optional, Callable
__all__ = ('createMechanicSingleInput', 'createAuxiliaryRocketLauncherInput')

def createMechanicSingleInput(component, profileName, actionName, inputCallback):
    mechanicSingleInput = MechanicSingleInput(component, profileName, actionName, inputCallback)
    component.lifeCycleEvents.lateSubscribe(mechanicSingleInput)
    return mechanicSingleInput


def createAuxiliaryRocketLauncherInput(component, switchModeProfileName, switchModeActionName, activateProfileName, activateActionName, switchModeCallback, activateCallback):
    auxiliaryRocketLauncherInput = AuxiliaryRocketLauncherInput(component, switchModeProfileName, switchModeActionName, activateProfileName, activateActionName, switchModeCallback, activateCallback)
    component.lifeCycleEvents.lateSubscribe(auxiliaryRocketLauncherInput)
    component.statesEvents.lateSubscribe(auxiliaryRocketLauncherInput)
    return auxiliaryRocketLauncherInput
