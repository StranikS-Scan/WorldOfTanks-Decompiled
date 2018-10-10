# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/battle_field_ctrl.py
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.interfaces import IBattleFieldController
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController

class IBattleFieldListener(object):

    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        pass

    def updateTeamHealth(self, alliesHP, enemiesHP, totalAlliesHP, totalEnemiesHP):
        pass


class BattleFieldCtrl(IBattleFieldController, ViewComponentsController):

    def __init__(self):
        super(BattleFieldCtrl, self).__init__()
        self.__isEnabled = True
        self.__battleCtx = None
        self._aliveAllies = {}
        self._aliveEnemies = {}
        self.__alliesHealth = 0
        self.__enemiesHealth = 0
        self.__totalAlliesHealth = 0
        self.__totalEnemiesHealth = 0
        self.__deadAllies = set()
        self.__deadEnemies = set()
        return

    def getCtrlScope(self):
        return _SCOPE.VEHICLES | _SCOPE.LOAD

    def getControllerID(self):
        return BATTLE_CTRL_ID.BATTLE_FIELD_CTRL

    def startControl(self, battleCtx, arenaVisitor):
        self.__battleCtx = battleCtx
        self.__isEnabled = not arenaVisitor.isArenaFogOfWarEnabled()

    def stopControl(self):
        super(BattleFieldCtrl, self).stopControl()
        self.clearViewComponents()
        self.__clear()
        self.__battleCtx = None
        return

    def setViewComponents(self, *components):
        super(BattleFieldCtrl, self).setViewComponents(*components)
        if self.__isEnabled:
            self.__initializeVehiclesInfo()

    def setVehicleHealth(self, vehicleID, newHealth):
        if self.__isEnabled:
            self.__changeVehicleHealth(vehicleID, newHealth)

    def setVehicleVisible(self, vehicleID, health):
        if self.__isEnabled:
            self.__changeVehicleHealth(vehicleID, health)

    def addVehicleInfo(self, vInfoVO, arenaDP):
        if self.__isEnabled and vInfoVO.isAlive():
            self.__registerAliveVehicle(vInfoVO, arenaDP)
            self.__updateVehiclesHealth()

    def invalidateFogOfWarEnabledFlag(self, flag):
        self.__isEnabled = not flag

    def invalidateArenaInfo(self):
        if self.__isEnabled and self._viewComponents:
            self.__initializeVehiclesInfo()

    def invalidateVehicleStatus(self, flags, vInfoVO, arenaDP):
        if self.__isEnabled and not vInfoVO.isAlive():
            self.__registerDeadVehicle(vInfoVO, arenaDP)
            self.__updateDeadVehicles()
            vehicleId = vInfoVO.vehicleID
            if vehicleId in self._aliveEnemies:
                currH, _ = self._aliveEnemies[vehicleId]
                self.__enemiesHealth -= currH
                del self._aliveEnemies[vehicleId]
                self.__updateVehiclesHealth()
            elif vehicleId in self._aliveAllies:
                currH, _ = self._aliveAllies[vehicleId]
                self.__alliesHealth -= currH
                del self._aliveAllies[vehicleId]
                self.__updateVehiclesHealth()

    def __initializeVehiclesInfo(self):
        arenaDP = self.__battleCtx.getArenaDP()
        collection = vos_collections.VehiclesInfoCollection()
        self.__clear()
        for vInfoVO in collection.iterator(arenaDP):
            if not vInfoVO.isAlive():
                self.__registerDeadVehicle(vInfoVO, arenaDP)
            self.__registerAliveVehicle(vInfoVO, arenaDP)

        self.__updateDeadVehicles()
        self.__updateVehiclesHealth()

    def __registerDeadVehicle(self, vInfoVO, arenaDP):
        if arenaDP.isEnemyTeam(vInfoVO.team):
            self.__deadEnemies.add(vInfoVO.vehicleID)
        else:
            self.__deadAllies.add(vInfoVO.vehicleID)

    def __registerAliveVehicle(self, vInfoVO, arenaDP):
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
            return

    def __updateVehiclesHealth(self):
        for viewCmp in self._viewComponents:
            viewCmp.updateTeamHealth(self.__alliesHealth, self.__enemiesHealth, self.__totalAlliesHealth, self.__totalEnemiesHealth)

    def __updateDeadVehicles(self):
        for viewCmp in self._viewComponents:
            viewCmp.updateDeadVehicles(set(self._aliveAllies.iterkeys()), self.__deadAllies, set(self._aliveEnemies.iterkeys()), self.__deadEnemies)

    def __changeVehicleHealth(self, vehicleID, newHealth):
        if vehicleID in self._aliveEnemies:
            currH, _ = self._aliveEnemies[vehicleID]
            self.__enemiesHealth -= currH
            self.__enemiesHealth += newHealth
            self._aliveEnemies[vehicleID][0] = newHealth
            self.__updateVehiclesHealth()
        elif vehicleID in self._aliveAllies:
            currH, _ = self._aliveAllies[vehicleID]
            self.__alliesHealth -= currH
            self.__alliesHealth += newHealth
            self._aliveAllies[vehicleID][0] = newHealth
            self.__updateVehiclesHealth()

    def __clear(self):
        self.__deadAllies.clear()
        self.__deadEnemies.clear()
        self._aliveAllies = {}
        self._aliveEnemies = {}
        self.__alliesHealth = 0
        self.__enemiesHealth = 0
        self.__totalAlliesHealth = 0
        self.__totalEnemiesHealth = 0
