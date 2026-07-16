# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/on_player_in_zone_manager.py
from __future__ import absolute_import
import BigWorld
import CGF
import Math
from collections import OrderedDict, defaultdict, namedtuple
from functools import partial
from typing import Optional, List
from Triggers import AreaTriggerComponent
from Vehicular import OnPlayerInZoneComponent
from PlayerEvents import g_playerEvents
from helpers import isPlayerAvatar
from constants import IS_EDITOR, IS_CGF_DUMP
if IS_EDITOR or IS_CGF_DUMP:

    class Vehicle(object):
        pass


else:
    from Vehicle import Vehicle

def _isAvatarReady():
    return isPlayerAvatar() and BigWorld.player().userSeesWorld()


_ActivePrefabInfo = namedtuple('_ActivePrefabInfo', ['vehicleId', 'prefabPath', 'prefabGO'])

class OnPlayerInZoneSystem(CGF.System):
    PlayerZoneActivated = CGF.ActivateReaction(CGF.ReactRw(OnPlayerInZoneComponent), CGF.Rw(AreaTriggerComponent))
    PlayerZoneDeactivated = CGF.DeactivateReaction(CGF.ReactRw(OnPlayerInZoneComponent), CGF.Rw(AreaTriggerComponent))
    PlayerZoneAccess = CGF.AccessReaction(CGF.Ro(OnPlayerInZoneComponent))
    VehicleAccess = CGF.AccessReaction(CGF.Rw(Vehicle))
    Reactions = CGF.Reactions(PlayerZoneActivated, PlayerZoneDeactivated, PlayerZoneAccess, VehicleAccess)

    def update(self):
        for component, trigger in self.reaction(self.PlayerZoneDeactivated):
            self.onRemoved(component, trigger)

        for component, trigger in self.reaction(self.PlayerZoneActivated):
            self.onAdded(component, trigger)

    def __init__(self):
        super(OnPlayerInZoneSystem, self).__init__()
        self.__prefabPathMap = defaultdict(OrderedDict)
        self.__activePrefab = None
        return

    def onMappingLoaded(self):
        if _isAvatarReady():
            self.__onAvatarReady()
        else:
            g_playerEvents.onAvatarReady += self.__onAvatarReady

    def onMappingUnloaded(self):
        self.__prefabPathMap.clear()
        self.__removeActivePrefab()
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        if BigWorld.player() and isPlayerAvatar():
            BigWorld.player().onAvatarVehicleChanged -= self.__onAvatarVehicleChanged
            BigWorld.player().onVehicleLeaveWorld -= self.__onVehicleLeaveWorld

    def onAdded(self, component, trigger):
        component.enterReactionID = trigger.addEnterReaction(self.__onEnterReaction)
        component.exitReactionID = trigger.addExitReaction(self.__onExitReaction)

    def onRemoved(self, component, trigger):
        trigger.removeEnterReaction(component.enterReactionID)
        trigger.removeExitReaction(component.exitReactionID)

    def __onPrefabLoaded(self, vehicleId, prefabPath, objects, queue):
        prefab = queue.gameObject(objects[0])
        playerVehicle = BigWorld.player().getVehicleAttached()
        if not playerVehicle:
            return False
        playerPrefabPaths = list((path for path in self.__prefabPathMap[playerVehicle.id].values()))
        if not playerPrefabPaths:
            return False
        if vehicleId != playerVehicle.id or prefabPath != playerPrefabPaths[-1]:
            return False
        if self.__activePrefab and self.__activePrefab.prefabGO:
            return False
        self.__activePrefab = _ActivePrefabInfo(vehicleId, prefabPath, prefab)
        return True

    def __updatePlayerPrefab(self):
        playerVehicle = BigWorld.player().getVehicleAttached()
        if not playerVehicle:
            self.__removeActivePrefab()
            return
        else:
            playerPrefabPaths = list((path for path in self.__prefabPathMap[playerVehicle.id].values()))
            if not playerPrefabPaths:
                self.__removeActivePrefab()
                return
            prefabPath = playerPrefabPaths[-1]
            if self.__activePrefab:
                if self.__activePrefab.vehicleId == playerVehicle.id and self.__activePrefab.prefabPath == prefabPath:
                    return
                self.__removeActivePrefab()
            self.__activePrefab = _ActivePrefabInfo(playerVehicle.id, prefabPath, None)
            CGF.loadAndCreatePrefabWithParent(prefabPath, playerVehicle.entityGameObject, Math.Vector3(0, 0, 0), partial(self.__onPrefabLoaded, playerVehicle.id, prefabPath))
            return

    def __removeActivePrefab(self):
        if self.__activePrefab and self.__activePrefab.prefabGO:
            q = CGF.CommandQueue(self.gom)
            q.removeGameObject(self.__activePrefab.prefabGO)
        self.__activePrefab = None
        return

    def __onEnterReaction(self, who, where):
        playerZoneAccess = self.reaction(self.PlayerZoneAccess)
        component = playerZoneAccess.find(where)
        if not component:
            return
        vehicleAccess = self.reaction(self.VehicleAccess)
        vehicle = vehicleAccess.find(who)
        if not vehicle:
            vehicle = CGF.findParentWithReaction(who, vehicleAccess)
        if not vehicle:
            return
        self.__prefabPathMap[vehicle.id][where.id] = component.prefabPath
        self.__updatePlayerPrefab()

    def __onExitReaction(self, who, where):
        playerZoneAccess = self.reaction(self.PlayerZoneAccess)
        component = playerZoneAccess.find(where)
        if not component:
            return
        else:
            vehicleAccess = self.reaction(self.VehicleAccess)
            vehicle = vehicleAccess.find(who)
            if not vehicle:
                vehicle = CGF.findParentWithReaction(who, vehicleAccess)
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
