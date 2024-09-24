# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/on_player_in_zone_manager.py
import BigWorld
import CGF
import Math
from collections import OrderedDict, defaultdict, namedtuple
from functools import partial
from typing import Optional
from Triggers import AreaTriggerComponent
from Vehicular import OnPlayerInZoneComponent
from vehicle_systems.cgf_helpers import getVehicleEntityByGameObject
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from PlayerEvents import g_playerEvents
from helpers import isPlayerAvatar

def _isAvatarReady():
    return isPlayerAvatar() and BigWorld.player().userSeesWorld()


_ActivePrefabInfo = namedtuple('_ActivePrefabInfo', ['vehicleId', 'prefabPath', 'prefabGO'])

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class OnPlayerInZoneManager(CGF.ComponentManager):

    def __init__(self):
        super(OnPlayerInZoneManager, self).__init__()
        self.__prefabPathMap = defaultdict(OrderedDict)
        self.__activePrefab = None
        if _isAvatarReady():
            self.__onAvatarReady()
        else:
            g_playerEvents.onAvatarReady += self.__onAvatarReady
        return

    def deactivate(self):
        self.__prefabPathMap.clear()
        self.__removeActivePrefab()
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        if BigWorld.player() and isPlayerAvatar():
            BigWorld.player().onAvatarVehicleChanged -= self.__onAvatarVehicleChanged
            BigWorld.player().onVehicleLeaveWorld -= self.__onVehicleLeaveWorld

    @onAddedQuery(OnPlayerInZoneComponent, AreaTriggerComponent, tickGroup='Simulation')
    def onAdded(self, component, trigger):
        component.enterReactionID = trigger.addEnterReaction(self.__onEnterReaction)
        component.exitReactionID = trigger.addExitReaction(self.__onExitReaction)

    @onRemovedQuery(OnPlayerInZoneComponent, AreaTriggerComponent, tickGroup='Simulation')
    def onRemoved(self, component, trigger):
        trigger.removeEnterReaction(component.enterReactionID)
        trigger.removeExitReaction(component.exitReactionID)

    def __onPrefabLoaded(self, vehicleId, prefabPath, prefab):
        playerVehicle = BigWorld.player().getVehicleAttached()
        if not playerVehicle:
            CGF.removeGameObject(prefab)
            return
        playerPrefabPaths = list((path for path in self.__prefabPathMap[playerVehicle.id].itervalues()))
        if not playerPrefabPaths:
            CGF.removeGameObject(prefab)
            return
        if vehicleId != playerVehicle.id or prefabPath != playerPrefabPaths[-1]:
            CGF.removeGameObject(prefab)
            return
        if self.__activePrefab and self.__activePrefab.prefabGO:
            CGF.removeGameObject(prefab)
            return
        self.__activePrefab = _ActivePrefabInfo(vehicleId, prefabPath, prefab)

    def __updatePlayerPrefab(self):
        playerVehicle = BigWorld.player().getVehicleAttached()
        if not playerVehicle:
            self.__removeActivePrefab()
            return
        else:
            playerPrefabPaths = list((path for path in self.__prefabPathMap[playerVehicle.id].itervalues()))
            if not playerPrefabPaths:
                self.__removeActivePrefab()
                return
            prefabPath = playerPrefabPaths[-1]
            if self.__activePrefab:
                if self.__activePrefab.vehicleId == playerVehicle.id and self.__activePrefab.prefabPath == prefabPath:
                    return
                self.__removeActivePrefab()
            self.__activePrefab = _ActivePrefabInfo(playerVehicle.id, prefabPath, None)
            CGF.loadGameObjectIntoHierarchy(prefabPath, playerVehicle.entityGameObject, Math.Vector3(0, 0, 0), partial(self.__onPrefabLoaded, playerVehicle.id, prefabPath))
            return

    def __removeActivePrefab(self):
        if self.__activePrefab and self.__activePrefab.prefabGO:
            CGF.removeGameObject(self.__activePrefab.prefabGO)
        self.__activePrefab = None
        return

    def __onEnterReaction(self, who, where):
        component = where.findComponentByType(OnPlayerInZoneComponent)
        if not component:
            return
        vehicle = getVehicleEntityByGameObject(who)
        if not vehicle:
            return
        self.__prefabPathMap[vehicle.id][where.id] = component.prefabPath
        self.__updatePlayerPrefab()

    def __onExitReaction(self, who, where):
        component = where.findComponentByType(OnPlayerInZoneComponent)
        if not component:
            return
        else:
            vehicle = getVehicleEntityByGameObject(who)
            if not vehicle:
                return
            self.__prefabPathMap[vehicle.id].pop(where.id, None)
            self.__updatePlayerPrefab()
            return

    def __onAvatarReady(self):
        BigWorld.player().onAvatarVehicleChanged += self.__onAvatarVehicleChanged
        BigWorld.player().onVehicleLeaveWorld += self.__onVehicleLeaveWorld
        self.__updatePlayerPrefab()

    def __onAvatarVehicleChanged(self):
        self.__updatePlayerPrefab()

    def __onVehicleLeaveWorld(self, vehicle):
        self.__prefabPathMap.pop(vehicle.id, None)
        self.__updatePlayerPrefab()
        return
