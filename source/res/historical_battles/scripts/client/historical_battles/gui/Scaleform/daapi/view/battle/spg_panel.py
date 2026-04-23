# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/spg_panel.py
import BigWorld
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from historical_battles_common.hb_constants import GoalId
from HBGoalComponent import HBGoalComponent
from historical_battles.gui.Scaleform.daapi.view.meta.HBSPGPanelMeta import HBSPGPanelMeta

class HistoricalBattlesSPGPanel(HBSPGPanelMeta, IArenaVehiclesController, IBattleFieldListener):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    UPDATE_DELAY = 1.0

    def __init__(self):
        super(HistoricalBattlesSPGPanel, self).__init__()
        self.__arenaDP = self.sessionProvider.getArenaDP()
        self.__enabled = False
        self.__deadAlliesCache = set()
        self.__updateDelayer = CallbackDelayer()

    def _populate(self):
        super(HistoricalBattlesSPGPanel, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        HBGoalComponent.onGoalsUpdated += self.__onGoalsUpdated
        arena = BigWorld.player().arena
        if arena.arenaType.geometryName:
            self.__onGoalsUpdated(arena.arenaInfo.goalComponent.goalsInfo)

    def _dispose(self):
        self.sessionProvider.removeArenaCtrl(self)
        self.__updateDelayer.destroy()
        self.__deadAlliesCache.clear()
        self.__updateDelayer = None
        self.__deadAlliesCache = None
        HBGoalComponent.onGoalsUpdated -= self.__onGoalsUpdated
        super(HistoricalBattlesSPGPanel, self)._dispose()
        return

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        vInfo = self.sessionProvider.getArenaDP().getVehicleInfo(vehicleID)
        if vInfo.isBot and vInfo.isSPG() and not vInfo.isEnemy():
            self.as_setSPGHpS(vehicleID, maxHealth, newHealth)

    def postUpdateVehicleHealth(self):
        self.__updateAll()

    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        if self.__enabled and deadAllies:
            for vehId in deadAllies - self.__deadAlliesCache:
                vInfo = self.sessionProvider.getArenaDP().getVehicleInfo(vehId)
                if vInfo.isBot:
                    self.__deadAlliesCache = deadAllies.copy()
                    self.__updateDelayer.delayCallback(self.UPDATE_DELAY, self.__updateAll)
                    return

        if not self.__updateDelayer.hasDelayedCallback(self.__updateAll):
            self.__updateAll()

    def addVehicleInfo(self, vo, arenaDP):
        if vo.isSPG() and vo.isBot and not vo.isEnemy():
            self.__updateAll()

    def __onGoalsUpdated(self, goalsInfo):
        if not goalsInfo:
            return
        if self.__enabled:
            if goalsInfo[-1]['id'] == GoalId.DEFENCE_COUNTER_ATTACK.value:
                self.as_hideTitleS()
            return
        self.as_showS()
        self.__enabled = True

    def __updateAll(self):
        teammateInfos = [ v for v in self.__arenaDP.getVehiclesInfoIterator() if v.isBot and v.isSPG() and not v.isEnemy() ]
        usersList = [ self.__getUserVo(vInfo) for vInfo in teammateInfos ]
        usersList.sort(key=lambda vo: vo['hpCurrent'] == 0)
        if usersList:
            self.as_setSPGListS(usersList)
            return True
        return False

    def __getUserVo(self, vInfo):
        vehicleHealthInfo = self.sessionProvider.dynamic.battleField.getVehicleHealthInfo(vInfo.vehicleID)
        vehicleHealth = 0
        if vInfo.isAlive():
            vehicleHealth = max(0, vehicleHealthInfo[0] if vehicleHealthInfo else vInfo.vehicleType.maxHealth)
        return {'vehicleID': vInfo.vehicleID,
         'vehicleType': vInfo.vehicleType.classTag,
         'vehicleName': vInfo.vehicleType.shortName,
         'hpMax': vInfo.vehicleType.maxHealth,
         'hpCurrent': vehicleHealth}
