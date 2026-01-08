# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/entities/vehicle_events/interfaces.py
from __future__ import absolute_import
import typing
from events_containers.common.containers import IClientEventsContainer, IClientEventsContainerListener
if typing.TYPE_CHECKING:
    from gui.battle_control.components_states.ammo import IComponentAmmoState
    from items.components.gun_installation_components import GunInstallationSlot

class IVehicleEventsLogic(object):
    onAppearanceReady = None
    onSiegeStateUpdated = None
    onVehicleDestroyed = None
    onCollectAmmoStates = None
    onDynamicComponentCreated = None
    onDynamicComponentDestroyed = None
    onDiscreteShotDone = None
    onShowDamageFromShot = None
    onVehicleHealthChanged = None

    def collectAmmoStates(self):
        raise NotImplementedError


class IVehicleEvents(IClientEventsContainer, IVehicleEventsLogic):
    pass


class IVehicleEventsListenerLogic(object):

    def onAppearanceReady(self):
        pass

    def onSiegeStateUpdated(self, newState, timeToNextMode):
        pass

    def onVehicleDestroyed(self):
        pass

    def onCollectAmmoStates(self, ammoStates):
        pass

    def onDynamicComponentCreated(self, component):
        pass

    def onDynamicComponentDestroyed(self, component):
        pass

    def onDiscreteShotDone(self, gunInstallationSlot):
        pass

    def onShowDamageFromShot(self, attackerID, hitPoints, effectsIndex, damageFactor, lastMaterialIsShield):
        pass

    def onVehicleHealthChanged(self, vehicleID, newHealth, oldHealth):
        pass


class IVehicleEventsListener(IClientEventsContainerListener, IVehicleEventsListenerLogic):
    pass
