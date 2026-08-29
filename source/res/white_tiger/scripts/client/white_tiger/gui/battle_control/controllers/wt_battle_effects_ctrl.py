# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/battle_control/controllers/wt_battle_effects_ctrl.py
from functools import partial
from enum import IntEnum
from Math import Vector3
import BigWorld
import CGF
from helpers.events_handler import EventsHandler
from helpers.CallbackDelayer import CallbackDelayer
from PlayerEvents import g_playerEvents
from gui.battle_control.battle_constants import BATTLE_CTRL_NAMES
from gui.battle_control.controllers.interfaces import IBattleController
from gui.shared import EVENT_BUS_SCOPE, EventPriority
from WTTeamInfoComponent import WTCloneInfoEvent
from white_tiger_common.wt_constants import WT_TEAMS

class WTBattleEffectsCtrl(IBattleController):

    def __init__(self):
        super(WTBattleEffectsCtrl, self).__init__()
        self.__ctrls = self.__initializeCtrls()

    def startControl(self):
        for ctrl in self.__ctrls:
            ctrl.startControl()

    def stopControl(self):
        for ctrl in self.__ctrls:
            ctrl.stopControl()

        self.__ctrls = None
        return

    def getControllerID(self):
        return len(BATTLE_CTRL_NAMES) + 1

    def __initializeCtrls(self):
        return [_CloneEffectCtrl()]


class _EffectCtrlBase(EventsHandler, IBattleController):

    def getControllerID(self):
        return None

    def startControl(self):
        self._subscribe()

    def stopControl(self):
        self._unsubscribe()

    def loadPrefabInHierarchy(self, prefabPath, parentGO, prefabStorage, offset=Vector3()):
        wrappedCb = partial(self.__onPrefabLoaded, prefabStorage, parentGO.id)
        CGF.loadGameObjectIntoHierarchy(prefabPath, parentGO, offset, wrappedCb)

    def unloadPrefab(self, prefabStorage, goID):
        if goID in prefabStorage:
            go = prefabStorage.get(goID)
            self._removeGO(go)
            prefabStorage.pop(goID)

    def _getListeners(self):
        raise NotImplementedError

    def _removeGO(self, go):
        if go and go.isValid():
            CGF.removeGameObject(go)

    def __onPrefabLoaded(self, prefabStorage, entityID, go):
        if entityID in prefabStorage:
            go = prefabStorage.get(entityID)
            self._removeGO(go)
            prefabStorage[entityID] = None
        prefabStorage[entityID] = go
        return


class _CloneVehicleStatus(IntEnum):
    NONE = 0
    ADDED = 1
    READY = 2


class _CloneEffectCtrl(_EffectCtrlBase):
    __CLONE_SPAWN_PREFAB = 'content/WtPrefabs/abilities/CloneSpawn.prefab'
    __VEHICLE_APPEAR_OFFSET_SECONDS = 5

    def __init__(self):
        super(_CloneEffectCtrl, self).__init__()
        self.__clonesData = {}
        self.__cloneSpawnGOs = {}
        self.__cd = CallbackDelayer()
        self.__isControl = True

    def startControl(self):
        super(_CloneEffectCtrl, self).startControl()
        BigWorld.player().onVehicleEnterWorld += self.__handleVehicleEnterWorld
        g_playerEvents.onRoundFinished += self.__onRoundFinished

    def stopControl(self):
        if self.__isControl:
            self.__stopControl()
        super(_CloneEffectCtrl, self).stopControl()

    def _getListeners(self):
        return [(WTCloneInfoEvent.CLONE_VEHICLE_INFOS_UPDATED,
          self.__onVehicleInfosUpdated,
          EVENT_BUS_SCOPE.BATTLE,
          EventPriority.HIGH)]

    def __handleVehicleEnterWorld(self, vehicle):
        if vehicle.team != WT_TEAMS.HUNTERS_TEAM or vehicle.avatarID != 0:
            return
        self.__handleVehicleData(vehicle.id)

    def __onVehicleInfosUpdated(self, data):
        cloneVehicleInfo = data.ctx['cloneVehicleInfo']
        currentVehIDs = set()
        for vehInfo in cloneVehicleInfo:
            vehicleID = vehInfo['vehicleId']
            currentVehIDs.add(vehicleID)

        removedIDs = set(self.__clonesData.keys()).difference(currentVehIDs)
        for removedID in removedIDs:
            vehicle = BigWorld.entities.get(removedID)
            if vehicle is None:
                return
            self.unloadPrefab(self.__cloneSpawnGOs, vehicle.entityGameObject.id)
            del self.__clonesData[removedID]

        addIDs = set(currentVehIDs).difference(self.__clonesData.keys())
        for addID in addIDs:
            if addID not in self.__clonesData:
                self.__clonesData[addID] = _CloneVehicleStatus.ADDED
                if BigWorld.entities.get(addID):
                    self.__handleVehicleData(addID)

        return

    def __handleVehicleData(self, vehicleID, isLastCheck=False):
        if vehicleID not in self.__clonesData:
            if isLastCheck:
                self.__clonesData[vehicleID] = _CloneVehicleStatus.READY
                return
            self.__cd.delayCallback(self.__VEHICLE_APPEAR_OFFSET_SECONDS, partial(self.__handleVehicleData, vehicleID, isLastCheck=True))
        elif self.__clonesData.get(vehicleID) == _CloneVehicleStatus.ADDED:
            self.__clonesData[vehicleID] = _CloneVehicleStatus.READY
            vehicle = BigWorld.entities.get(vehicleID)
            self.loadPrefabInHierarchy(self.__CLONE_SPAWN_PREFAB, vehicle.entityGameObject, self.__cloneSpawnGOs)

    def __onRoundFinished(self, winnerTeam, reason, extraData):
        self.__stopControl()

    def __stopControl(self):
        self.__isControl = False
        BigWorld.player().onVehicleEnterWorld -= self.__handleVehicleEnterWorld
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        self.__cd.destroy()
        self.__cd = None
        for go in self.__cloneSpawnGOs.itervalues():
            self._removeGO(go)

        self.__cloneSpawnGOs.clear()
        self.__cloneSpawnGOs = None
        self.__clonesData.clear()
        self.__clonesData = None
        return
