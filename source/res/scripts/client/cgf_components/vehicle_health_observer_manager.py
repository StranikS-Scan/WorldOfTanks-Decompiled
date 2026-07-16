# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/vehicle_health_observer_manager.py
from __future__ import absolute_import
import BigWorld
import CGF
import logging
from collections import defaultdict
from constants import SPECIAL_VEHICLE_HEALTH, IS_EDITOR, IS_CGF_DUMP
from GenericComponents import StateSwitcherComponent
from cgf_components_common.state_components import VehicleHealthObserverComponent
_logger = logging.getLogger(__name__)
if IS_EDITOR or IS_CGF_DUMP:

    class Vehicle(object):
        pass


else:
    from Vehicle import Vehicle

class VehicleHealthObserverSystem(CGF.System):
    ObserverActivated = CGF.ActivateReaction(CGF.GameObject, CGF.Rw(StateSwitcherComponent), CGF.ReactRw(VehicleHealthObserverComponent))
    ObserverDeactivated = CGF.DeactivateReaction(CGF.GameObject, CGF.Rw(StateSwitcherComponent), CGF.ReactRw(VehicleHealthObserverComponent))
    SwitcherAccess = CGF.AccessReaction(CGF.Rw(StateSwitcherComponent))
    VehicleAccess = CGF.AccessReaction(CGF.Rw(Vehicle))
    Reactions = CGF.Reactions(ObserverActivated, ObserverDeactivated, SwitcherAccess, VehicleAccess)

    def __init__(self):
        super(VehicleHealthObserverSystem, self).__init__()
        self.__switchersGroupedByVehicle = defaultdict(list)
        self.__switchersToVehiclesMap = {}

    def update(self):
        vehicleAccess = self.reaction(self.VehicleAccess)
        for go, switcher, observer in self.reaction(self.ObserverDeactivated):
            vehicleID = self.__switchersToVehiclesMap.pop(go, None)
            if vehicleID is None:
                continue
            switchers = self.__switchersGroupedByVehicle[vehicleID]
            switchers = [ switcherGO for switcherGO in switchers if switcherGO.id != go.id ]
            self.__switchersGroupedByVehicle[vehicleID] = switchers
            if switchers:
                continue
            vehicle = BigWorld.entities.get(vehicleID)
            if vehicle and not vehicle.isDestroyed:
                _logger.debug('No switchers left. Unsubscribing from vehicle %s', vehicle.id)
                vehicle.events.onVehicleHealthChanged -= self.__onHealthChanged

        for go, switcher, observer in self.reaction(self.ObserverActivated):
            vehicle = CGF.findParentWithReaction(go, vehicleAccess)
            if not vehicle:
                switcher.requestState(observer.state)
                continue
            currentState = self.__determineState(vehicle.health)
            switcher.requestState(currentState)
            self.__switchersGroupedByVehicle[vehicle.id].append(go)
            self.__switchersToVehiclesMap[go.id] = vehicle.id
            vehicle.events.onVehicleHealthChanged += self.__onHealthChanged

        return

    @staticmethod
    def __determineState(health):
        if health > 0:
            return StateSwitcherComponent.NORMAL_STATE
        return StateSwitcherComponent.CRITICAL_STATE if SPECIAL_VEHICLE_HEALTH.IS_AMMO_BAY_EXPLODED(health) else StateSwitcherComponent.DAMAGED_STATE

    def __onHealthChanged(self, vehicleID, newHealth, _):
        newState = self.__determineState(newHealth)
        switcherAccess = self.reaction(self.SwitcherAccess)
        for go in self.__switchersGroupedByVehicle[vehicleID]:
            if not go:
                continue
            stateSwitcher = switcherAccess.find(go)
            if not stateSwitcher:
                _logger.error('Failed to find StateSwitcherComponent component for go=%s', go.name)
                continue
            if newState != stateSwitcher.getState():
                _logger.debug('Switching damage state of %s %s to %s', vehicleID, go.name, newState)
                stateSwitcher.requestState(newState)
