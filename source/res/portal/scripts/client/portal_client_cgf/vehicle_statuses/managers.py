# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/vehicle_statuses/managers.py
import typing
import CGF
import BigWorld
import Triggers
from helpers import dependency
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from skeletons.gui.battle_session import IBattleSessionProvider
from items.utils import isclose
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, DestroyTimerViewState, TIMER_VIEW_STATE
from portal_common_cgf.portal_helpers import registerPortalManager, getVehicleFromGO
from portal_common_cgf.vehicle_buffs.components import PortalAuraComponent
from portal_client_cgf.teleport.managers import TeleportManager
from TeleportReplicableComponent import TeleportReplicableComponent
if typing.TYPE_CHECKING:
    from PortalBattleStateComponent import PortalBattleStateComponent

@registerPortalManager(CGF.DomainOption.DomainClient)
class VehicleStatusManager(CGF.ComponentManager):
    __RATTE_AURA_GO_NAME = 'incineratingAura'
    __ANOMALY_GO_NAME_PREFIX = 'anomaly_'
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, *args):
        super(VehicleStatusManager, self).__init__(*args)
        self.__auraZones = None
        return

    def activate(self):
        self.__auraZones = {}
        TeleportReplicableComponent.onTeleportingChanged += self.__onTeleportingChanged

    def deactivate(self):
        TeleportReplicableComponent.onTeleportingChanged -= self.__onTeleportingChanged
        self.__auraZones = None
        return

    @property
    def battleState(self):
        arenaInfo = BigWorld.player().arena.arenaInfo
        return arenaInfo.portalBattleStateComponent

    @onAddedQuery(CGF.GameObject, PortalAuraComponent)
    def onAuraZoneAdded(self, go, auraComponent):
        vehicleState = None
        if go.name == self.__RATTE_AURA_GO_NAME:
            vehicleState = VEHICLE_VIEW_STATE.PORTAL_RATTE_AURA
        elif go.name.startswith(self.__ANOMALY_GO_NAME_PREFIX):
            vehicleState = VEHICLE_VIEW_STATE.PORTAL_ANOMALY
        if vehicleState:
            self.__subscribeToAuraZone(go, vehicleState)
        return

    @onRemovedQuery(CGF.GameObject, PortalAuraComponent)
    def onAuraZomeRemoved(self, go, auraComponent):
        if self.__auraZones and go.id in self.__auraZones:
            self.__unsubscribeFromAuraZone(go)

    def __subscribeToAuraZone(self, go, vehicleState):
        trigger = go.findComponentByType(Triggers.AreaTriggerComponent)
        if trigger:
            enterReactionID = trigger.addEnterReaction(self.__onEnteredAuraZone)
            exitReactionID = trigger.addExitReaction(self.__onExitedAuraZone)
            self.__auraZones[go.id] = (vehicleState, enterReactionID, exitReactionID)

    def __unsubscribeFromAuraZone(self, go):
        _, enterReactionID, exitReactionID = self.__auraZones.pop(go.id)
        trigger = go.findComponentByType(Triggers.AreaTriggerComponent)
        if trigger:
            trigger.removeEnterReaction(enterReactionID)
            trigger.removeExitReaction(exitReactionID)

    def __onEnteredAuraZone(self, who, where):
        vehicle = getVehicleFromGO(who, self.spaceID)
        if vehicle:
            if vehicle.id == avatar_getter.getVehicleIDAttached():
                vehicleState, _, _ = self.__auraZones[where.id]
                state = DestroyTimerViewState(vehicleState, 0, TIMER_VIEW_STATE.WARNING, 0)
                self.__invalidateVehicleState(vehicleState, state)

    def __onExitedAuraZone(self, who, where):
        vehicle = getVehicleFromGO(who, self.spaceID)
        if vehicle:
            if vehicle.id == avatar_getter.getVehicleIDAttached():
                vehicleState, _, _ = self.__auraZones[where.id]
                state = DestroyTimerViewState.makeCloseTimerState(vehicleState)
                self.__invalidateVehicleState(vehicleState, state)

    def __onTeleportingChanged(self, go, vehicleID, finishTime):
        if vehicleID == avatar_getter.getVehicleIDAttached():
            teleportGO = TeleportManager.getCampTeleport(go, self.spaceID)
            frontier = self.battleState.getTeleportFrontier(teleportGO.name)
            state = {'isVisible': not isclose(finishTime, 0.0),
             'frontier': frontier,
             'duration': finishTime - BigWorld.serverTime(),
             'finishTime': finishTime}
            self.__invalidateVehicleState(VEHICLE_VIEW_STATE.PORTAL_TELEPORT, state)

    def __invalidateVehicleState(self, vehicleState, state):
        self.__sessionProvider.invalidateVehicleState(vehicleState, state)
