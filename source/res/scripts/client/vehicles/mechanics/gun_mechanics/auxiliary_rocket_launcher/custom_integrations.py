# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/auxiliary_rocket_launcher/custom_integrations.py
from __future__ import absolute_import
import weakref
import typing
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from gui.armor_flashlight.utils import ArmorFlashlightHideReason
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.components.component_wrappers import ifPlayerVehicle
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from Avatar import PlayerAvatar
    from vehicles.mechanics.gun_mechanics.auxiliary_rocket_launcher.mechanic_models import AuxiliaryRocketLauncherState

class AuxiliaryRocketLauncherCustomIntegrations(ContainersListener, IMechanicStatesListenerLogic):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, component):
        super(AuxiliaryRocketLauncherCustomIntegrations, self).__init__()
        self._component = weakref.proxy(component)

    @eventHandler
    def onStatePrepared(self, state):
        self.__updateArmorFlashlightVisibility(state.isInAimingMode)

    @eventHandler
    def onStateTransition(self, prevState, newState):
        self.__updateArmorFlashlightVisibility(newState.isInAimingMode)

    @eventHandler
    def onEventsContainerDestroy(self, events):
        self.__updateArmorFlashlightVisibility(False)
        self._component = None
        super(AuxiliaryRocketLauncherCustomIntegrations, self).onEventsContainerDestroy(events)
        return

    def isPlayerVehicle(self, player):
        return self._component.isPlayerVehicle(player)

    @ifPlayerVehicle
    def __updateArmorFlashlightVisibility(self, _, isInAimingMode):
        armorFlashlight = self.__sessionProvider.shared.armorFlashlight
        if armorFlashlight is None:
            return
        else:
            if isInAimingMode:
                armorFlashlight.addHideReason(ArmorFlashlightHideReason.HE_ROCKET_AIMING_MODE)
            else:
                armorFlashlight.removeHideReason(ArmorFlashlightHideReason.HE_ROCKET_AIMING_MODE)
            return
