# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/vehicle_health_observer_manager.py
import BigWorld
import CGF
import logging
from collections import defaultdict
from constants import SPECIAL_VEHICLE_HEALTH
from GenericComponents import StateSwitcherComponent
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from cgf_components_common.state_components import VehicleHealthObserverComponent
from cgf_common.cgf_helpers import getVehicleEntityByGameObject
_logger = logging.getLogger(__name__)

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class VehicleHealthObserverManager(CGF.ComponentManager):

    def __init__(self):
        super(VehicleHealthObserverManager, self).__init__()
        self.__switchersGroupedByVehicle = defaultdict(list)
        self.__switchersToVehiclesMap = {}

    @onAddedQuery(CGF.GameObject, StateSwitcherComponent, VehicleHealthObserverComponent)
    def onAdded(self, go, stateSwitcher, vehicleHealthObserverComponent):
        vehicle = getVehicleEntityByGameObject(go)
        if not vehicle:
            stateSwitcher.requestState(vehicleHealthObserverComponent.state)
            return
        currentState = self.__determineState(vehicle.health)
        stateSwitcher.requestState(currentState)
        self.__switchersGroupedByVehicle[vehicle.id].append(go)
        self.__switchersToVehiclesMap[go.id] = vehicle.id
        vehicle.onVehicleHealthChanged += self.__onHealthChanged

    @onRemovedQuery(CGF.GameObject, StateSwitcherComponent, VehicleHealthObserverComponent)
    def onRemoved(self, go, stateSwitcher, vehicleHealthObserverComponent):
        vehicleID = self.__switchersToVehiclesMap.pop(go.id, None)
        if vehicleID is None:
            return
        else:
            switchers = self.__switchersGroupedByVehicle[vehicleID]
            switchers = [ switcherGO for switcherGO in switchers if switcherGO.id != go.id ]
            self.__switchersGroupedByVehicle[vehicleID] = switchers
            if switchers:
                return
            vehicle = BigWorld.entities.get(vehicleID)
            if vehicle and not vehicle.isDestroyed:
                _logger.debug('No switchers left. Unsubscribing from vehicle %s', vehicle.id)
                vehicle.onVehicleHealthChanged -= self.__onHealthChanged
            return

    @staticmethod
    def __determineState(health):
        if health > 0:
            return StateSwitcherComponent.NORMAL_STATE
        return StateSwitcherComponent.CRITICAL_STATE if SPECIAL_VEHICLE_HEALTH.IS_AMMO_BAY_EXPLODED(health) else StateSwitcherComponent.DAMAGED_STATE

    def __onHealthChanged(self, vehicleID, newHealth, prevHealth):
        newState = self.__determineState(newHealth)
        for go in self.__switchersGroupedByVehicle[vehicleID]:
            if not go.isValid():
                continue
            stateSwitcher = go.findComponentByType(StateSwitcherComponent)
            if not stateSwitcher:
                _logger.error('Failed to find StateSwitcherComponent component for go=%s', go.name)
                continue
            if newState != stateSwitcher.getState():
                _logger.debug('Switching damage state of %s %s to %s', vehicleID, go.name, newState)
                stateSwitcher.requestState(newState)
