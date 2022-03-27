# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_field_ctrl.py
import typing
import BigWorld
import Event
from constants import ATTACK_REASON_INDICES, ATTACK_REASON
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.interfaces import IBattleFieldController, IVehiclesAndPositionsController
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE, VehicleSpottedStatus, INVALIDATE_OP
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from gui.battle_control import avatar_getter
from gui.sounds.r4_sound_constants import R4_SOUND
if typing.TYPE_CHECKING:
    from typing import Dict, Iterator, List
    from Math import Vector3
    from gui.battle_control.arena_info.arena_vos import VehicleArenaInfoVO

class IBattleFieldListener(object):

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        pass

    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        pass

    def updateTeamHealth(self, alliesHP, enemiesHP, totalAlliesHP, totalEnemiesHP):
        pass


class BattleFieldCtrl(IBattleFieldController, IVehiclesAndPositionsController, ViewComponentsController):

    def __init__(self):
        super(BattleFieldCtrl, self).__init__()
        self._isEnabled = True
        self.__battleCtx = None
        self._aliveAllies = {}
        self._aliveEnemies = {}
        self.__alliesHealth = 0
        self.__enemiesHealth = 0
        self.__totalAlliesHealth = 0
        self.__totalEnemiesHealth = 0
        self.__deadAllies = set()
        self.__deadEnemies = set()
        self.__eManager = Event.EventManager()
        self.onSpottedStatusChanged = Event.Event(self.__eManager)
        return

    def getCtrlScope(self):
        return _SCOPE.VEHICLES | _SCOPE.LOAD | _SCOPE.POSITIONS

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_FIELD_CTRL

    def getVehicleHealthInfo(self, vehicleID):
        if vehicleID in self._aliveAllies:
            healthInfo = self._aliveAllies[vehicleID]
            return (healthInfo[0], healthInfo[1])
        else:
            return self._aliveEnemies.get(vehicleID, None)

    def startControl(self, battleCtx, arenaVisitor):
        self.__battleCtx = battleCtx
        self._isEnabled = not arenaVisitor.isArenaFogOfWarEnabled()

    def stopControl(self):
        super(BattleFieldCtrl, self).stopControl()
        self.clearViewComponents()
        self._clear()
        if self.__eManager is not None:
            self.__eManager.clear()
            self.__eManager = None
        self.__battleCtx = None
        return

    def setViewComponents(self, *components):
        super(BattleFieldCtrl, self).setViewComponents(*components)
        if self._isEnabled:
            self.__initializeVehiclesInfo()

    def setVehicleHealth(self, vehicleID, newHealth, attackReasonID=None):
        if self._isEnabled:
            self._changeVehicleHealth(vehicleID, newHealth, attackReasonID=attackReasonID)
            self.__updateVehicleHealth(vehicleID)

    def setVehicleVisible(self, vehicleID, health):
        if self._isEnabled:
            self._changeVehicleHealth(vehicleID, health)
            self.__updateVehicleHealth(vehicleID)
            self.__updateSpottedStatus(vehicleID, VehicleSpottedStatus.SPOTTED)

    def updatePositions(self, iterator):
        handled = set()
        arenaDP = self.__battleCtx.getArenaDP()
        for vInfo, _ in iterator():
            vehicleID = vInfo.vehicleID
            if vehicleID not in self._aliveEnemies or not vInfo.isAlive():
                continue
            handled.add(vehicleID)
            vStats = arenaDP.getVehicleStats(vehicleID)
            if vStats.spottedStatus in (VehicleSpottedStatus.DEFAULT, VehicleSpottedStatus.UNSPOTTED):
                self.__updateSpottedStatus(vehicleID, VehicleSpottedStatus.SPOTTED)

        for vehicleID in set(self._aliveEnemies).difference(handled):
            vStats = arenaDP.getVehicleStats(vehicleID)
            vehicle = BigWorld.entity(vehicleID)
            if vehicle is None and vStats.spottedStatus == VehicleSpottedStatus.SPOTTED:
                self.__updateSpottedStatus(vehicleID, VehicleSpottedStatus.UNSPOTTED)

        return

    def stopVehicleVisual(self, vehicleID):
        self.__updateSpottedStatus(vehicleID, VehicleSpottedStatus.UNSPOTTED)

    def addVehicleInfo(self, vInfoVO, arenaDP):
        if self._isEnabled and vInfoVO.isAlive():
            self._registerAliveVehicle(vInfoVO, arenaDP)
            self.__updateVehiclesHealth()

    def updateVehiclesInfo(self, updated, arenaDP):
        if self._isEnabled:
            for _, vInfoVO in updated:
                if not vInfoVO.isAlive():
                    continue
                vehicleID = vInfoVO.vehicleID
                if vehicleID in self._aliveEnemies or vehicleID in self._aliveAllies:
                    self.__changeMaxVehicleHealth(vehicleID, vInfoVO.vehicleType.maxHealth)
                self.addVehicleInfo(vInfoVO, arenaDP)

    def invalidateFogOfWarEnabledFlag(self, flag):
        self._isEnabled = not flag

    def invalidateArenaInfo(self):
        if self._isEnabled and self._viewComponents:
            self.__initializeVehiclesInfo()

    def invalidateVehicleStatus(self, flags, vInfoVO, arenaDP):
        if self._isEnabled and not vInfoVO.isAlive():
            self._registerDeadVehicle(vInfoVO, arenaDP)
            self.__updateDeadVehicles()
            vehicleId = vInfoVO.vehicleID
            if vehicleId in self._aliveEnemies:
                currH, _ = self._aliveEnemies[vehicleId]
                self.__enemiesHealth -= currH
                del self._aliveEnemies[vehicleId]
                self.__updateVehiclesHealth()
                vStats = arenaDP.getVehicleStats(vehicleId)
                if vStats.spottedStatus != VehicleSpottedStatus.DEFAULT:
                    self.__updateSpottedStatus(vehicleId, VehicleSpottedStatus.DEFAULT)
            elif vehicleId in self._aliveAllies:
                currH, _ = self._aliveAllies[vehicleId]
                self.__alliesHealth -= currH
                del self._aliveAllies[vehicleId]
                self.__updateVehiclesHealth()

    def __initializeVehiclesInfo(self):
        arenaDP = self.__battleCtx.getArenaDP()
        collection = vos_collections.VehiclesInfoCollection()
        self._clear()
        for vInfoVO in collection.iterator(arenaDP):
            if vInfoVO.isObserver() or vInfoVO.isSupply():
                continue
            if not vInfoVO.isAlive():
                self._registerDeadVehicle(vInfoVO, arenaDP)
            self._registerAliveVehicle(vInfoVO, arenaDP)

        self.__updateDeadVehicles()
        self.__updateVehiclesHealth()

    def _registerDeadVehicle(self, vInfoVO, arenaDP):
        if arenaDP.isEnemyTeam(vInfoVO.team):
            self.__deadEnemies.add(vInfoVO.vehicleID)
        else:
            self.__deadAllies.add(vInfoVO.vehicleID)

    def _registerAliveVehicle(self, vInfoVO, arenaDP):
        maxHealth = vInfoVO.vehicleType.maxHealth
        if maxHealth is None:
            return
        else:
            if arenaDP.isEnemyTeam(vInfoVO.team):
                tList = self._aliveEnemies
                self.__enemiesHealth += maxHealth
                self.__totalEnemiesHealth += maxHealth
            else:
                tList = self._aliveAllies
                self.__alliesHealth += maxHealth
                self.__totalAlliesHealth += maxHealth
            tList[vInfoVO.vehicleID] = [maxHealth, maxHealth]
            self.__updateVehicleHealth(vehicleID=vInfoVO.vehicleID)
            return

    def __updateVehiclesHealth(self):
        for viewCmp in self._viewComponents:
            viewCmp.updateTeamHealth(self.__alliesHealth, self.__enemiesHealth, self.__totalAlliesHealth, self.__totalEnemiesHealth)

    def __updateDeadVehicles(self):
        for viewCmp in self._viewComponents:
            viewCmp.updateDeadVehicles(set(self._aliveAllies.iterkeys()), self.__deadAllies, set(self._aliveEnemies.iterkeys()), self.__deadEnemies)

    def __updateVehicleHealth(self, vehicleID):
        if vehicleID in self._aliveAllies:
            currH, maxH = self._aliveAllies[vehicleID]
            for viewCmp in self._viewComponents:
                viewCmp.updateVehicleHealth(vehicleID, currH, maxH)

        elif vehicleID in self._aliveEnemies:
            currH, maxH = self._aliveEnemies[vehicleID]
            for viewCmp in self._viewComponents:
                viewCmp.updateVehicleHealth(vehicleID, currH, maxH)

    def _changeVehicleHealth(self, vehicleID, newHealth, needUpdate=True, attackReasonID=None):
        setter = None
        currentHealth = 0
        if vehicleID in self._aliveEnemies:
            currentHealth, _ = self._aliveEnemies[vehicleID]
            setter = self.__setEnemyHealth
        elif vehicleID in self._aliveAllies:
            currentHealth, _ = self._aliveAllies[vehicleID]
            setter = self.__setAllyHealth
        if setter is not None and currentHealth != newHealth:
            setter(vehicleID, currentHealth, newHealth)
            if needUpdate:
                self.__updateVehiclesHealth()
        return

    def __setEnemyHealth(self, vehicleID, currentHealth, newHealth):
        self.__enemiesHealth -= currentHealth
        self.__enemiesHealth += newHealth
        self._aliveEnemies[vehicleID][0] = newHealth

    def __setAllyHealth(self, vehicleID, currentHealth, newHealth):
        self.__alliesHealth -= currentHealth
        self.__alliesHealth += newHealth
        self._aliveAllies[vehicleID][0] = newHealth

    def __changeMaxVehicleHealth(self, vehicleID, newMaxHealth):
        setter = None
        currentMaxHealth = 0
        currentHealth = 0
        if vehicleID in self._aliveEnemies:
            setter = self.__setEnemyMaxHealth
            currentHealth, currentMaxHealth = self._aliveEnemies[vehicleID]
        elif vehicleID in self._aliveAllies:
            setter = self.__setAllyMaxHealth
            currentHealth, currentMaxHealth = self._aliveAllies[vehicleID]
        if setter is not None and currentMaxHealth != newMaxHealth:
            setter(vehicleID, currentMaxHealth, newMaxHealth)
            if currentHealth == currentMaxHealth:
                self._changeVehicleHealth(vehicleID, newMaxHealth, needUpdate=False)
            self.__updateVehiclesHealth()
        return

    def __setEnemyMaxHealth(self, vehicleID, currentMaxHealth, newMaxHealth):
        self.__totalEnemiesHealth -= currentMaxHealth
        self.__totalEnemiesHealth += newMaxHealth
        self._aliveEnemies[vehicleID][1] = newMaxHealth

    def __setAllyMaxHealth(self, vehicleID, currentMaxHealth, newMaxHealth):
        self.__totalAlliesHealth -= currentMaxHealth
        self.__totalAlliesHealth += newMaxHealth
        self._aliveAllies[vehicleID][1] = newMaxHealth

    def __updateSpottedStatus(self, vehicleID, vehicleSpottedStatus):
        if vehicleID in self._aliveAllies or vehicleID in self.__deadAllies:
            return
        else:
            vehicle = BigWorld.entity(vehicleID)
            if vehicle is not None:
                isAlive = vehicle.isAlive()
            elif vehicleID in self._aliveEnemies:
                isAlive = True
            else:
                isAlive = False
            if isAlive:
                spottedState = vehicleSpottedStatus
            else:
                spottedState = VehicleSpottedStatus.DEFAULT
            flags, vo = self.__battleCtx.getArenaDP().updateVehicleSpottedStatus(vehicleID, spottedState)
            if flags != INVALIDATE_OP.NONE:
                self.onSpottedStatusChanged([(flags, vo)], self.__battleCtx.getArenaDP())
            return

    def _clear(self):
        self.__deadAllies.clear()
        self.__deadEnemies.clear()
        self._aliveAllies = {}
        self._aliveEnemies = {}
        self.__alliesHealth = 0
        self.__enemiesHealth = 0
        self.__totalAlliesHealth = 0
        self.__totalEnemiesHealth = 0


class DAMAGE_STATE(object):
    NO_DAMAGE, FIRST_DAMAGE, MEDIUM_DAMAGE, BIG_DAMAGE = range(1, 5)
    SOUNDS = {NO_DAMAGE: None,
     FIRST_DAMAGE: R4_SOUND.R4_ALLY_GET_FIRST_DAMAGE,
     MEDIUM_DAMAGE: R4_SOUND.R4_ALLY_GET_MEDIUM_DAMAGE,
     BIG_DAMAGE: R4_SOUND.R4_ALLY_GET_BIG_DAMAGE}
    ATTACK_REASON_IDS_FOR_SOUND = (ATTACK_REASON_INDICES[ATTACK_REASON.SHOT], ATTACK_REASON_INDICES[ATTACK_REASON.SUPPLY_SHOT])


class R4BattleFieldCtrl(BattleFieldCtrl):

    def __init__(self):
        super(R4BattleFieldCtrl, self).__init__()
        self.__alliesState = {}

    def invalidateVehicleStatus(self, flags, vInfoVO, arenaDP):
        super(R4BattleFieldCtrl, self).invalidateVehicleStatus(flags, vInfoVO, arenaDP)
        if self._isEnabled and not vInfoVO.isAlive():
            vehicleId = vInfoVO.vehicleID
            if vehicleId in self.__alliesState:
                del self.__alliesState[vehicleId]

    def _registerAliveVehicle(self, vInfoVO, arenaDP):
        super(R4BattleFieldCtrl, self)._registerAliveVehicle(vInfoVO, arenaDP)
        if arenaDP.isAllyTeam(vInfoVO.team):
            self.__alliesState[vInfoVO.vehicleID] = DAMAGE_STATE.NO_DAMAGE

    def _clear(self):
        super(R4BattleFieldCtrl, self)._clear()
        self.__alliesState = {}

    def _changeVehicleHealth(self, vehicleID, newHealth, needUpdate=True, attackReasonID=None):
        super(R4BattleFieldCtrl, self)._changeVehicleHealth(vehicleID, newHealth, needUpdate, attackReasonID)
        if vehicleID not in self._aliveAllies:
            return
        vehicle = BigWorld.entity(vehicleID)
        vehicleTags = vehicle.typeDescriptor.type.tags
        if any((tag in vehicleTags for tag in ('observer', 'commander'))):
            return
        currentHealth, maxHealth = self._aliveAllies[vehicleID]
        state = self.__alliesState[vehicleID]
        currentHealthRatio = float(currentHealth) / maxHealth
        if currentHealthRatio < 0.3 and state < DAMAGE_STATE.BIG_DAMAGE:
            state = DAMAGE_STATE.BIG_DAMAGE
        elif currentHealthRatio < 0.6 and state < DAMAGE_STATE.MEDIUM_DAMAGE:
            state = DAMAGE_STATE.MEDIUM_DAMAGE
        elif currentHealthRatio < 1.0 and state < DAMAGE_STATE.FIRST_DAMAGE:
            state = DAMAGE_STATE.FIRST_DAMAGE
        else:
            return
        self.__alliesState[vehicleID] = state
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play') and attackReasonID in DAMAGE_STATE.ATTACK_REASON_IDS_FOR_SOUND:
            soundNotifications.play(DAMAGE_STATE.SOUNDS[state], vehicleID)


def createBattleFieldCtrl(setup):
    return R4BattleFieldCtrl() if avatar_getter.isPlayerCommander() else BattleFieldCtrl()
