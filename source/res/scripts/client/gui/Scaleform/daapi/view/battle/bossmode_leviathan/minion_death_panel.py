# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/bossmode_leviathan/minion_death_panel.py
import BigWorld
from helpers import dependency, i18n
from gui.Scaleform.daapi.view.meta.MinionDeathPanelMeta import MinionDeathPanelMeta
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from ReplayEvents import g_replayEvents

class MinionDeathPanel(MinionDeathPanelMeta):

    def __init__(self):
        super(MinionDeathPanel, self).__init__()
        self.__deadMinionsCount = 0
        self.__maxMinions = 0

    def _populate(self):
        super(MinionDeathPanel, self)._populate()
        self.__updateCurrentMinionDeathState()
        BigWorld.player().arena.onVehicleKilled += self.__onMinionDeath
        g_replayEvents.onTimeWarpFinish += self.__onReplayTimeWarpFinished

    def _dispose(self):
        g_replayEvents.onTimeWarpFinish -= self.__onReplayTimeWarpFinished
        BigWorld.player().arena.onVehicleKilled -= self.__onMinionDeath
        super(MinionDeathPanel, self)._dispose()

    def __submitGoalMessage(self, initialDead, maxCount):
        vo = {'initialDeaths': initialDead,
         'maxMinions': maxCount,
         'title': i18n.makeString(INGAME_GUI.HALLOWEEN_MINION_DEATH_PANEL_TITLE),
         'hintMsg': i18n.makeString(INGAME_GUI.HALLOWEEN_MINION_DEATH_PANEL_HINT),
         'countLabel': i18n.makeString(INGAME_GUI.HALLOWEEN_MINION_DEATH_PANEL_COUNTLABEL),
         'preposition': i18n.makeString(INGAME_GUI.HALLOWEEN_MINION_DEATH_PANEL_PREPOSITION)}
        self.as_initPanelS(vo)

    def __updateCurrentMinionDeathState(self):
        numOfMinions = 0
        currentDeadMinions = 0
        for vehInfo in BigWorld.player().arena.vehicles.itervalues():
            if vehInfo['team'] == 2:
                isLeviathanBoss = VEHICLE_TAGS.LEVIATHAN in vehInfo['vehicleType'].type.tags
                if not isLeviathanBoss:
                    numOfMinions += 1
                    if not vehInfo['isAlive']:
                        currentDeadMinions += 1

        if self.__maxMinions == 0:
            self.__submitGoalMessage(currentDeadMinions, numOfMinions)
        else:
            self.as_updateDeadCountS(currentDeadMinions, numOfMinions)
        self.__deadMinionsCount = currentDeadMinions
        self.__maxMinions = numOfMinions

    def __onMinionDeath(self, targetID, attackerID, equipmentID, reason):
        dyingEntity = BigWorld.entity(targetID)
        if dyingEntity is None:
            self.__updateCurrentMinionDeathState()
        elif dyingEntity is not None and dyingEntity.publicInfo['team'] == 2 and self.__deadMinionsCount < self.__maxMinions:
            isLeviathanBoss = VEHICLE_TAGS.LEVIATHAN in dyingEntity.typeDescriptor.type.tags
            if isLeviathanBoss:
                self.__deadMinionsCount = self.__maxMinions
            else:
                self.__deadMinionsCount += 1
            self.as_updateDeadCountS(self.__deadMinionsCount, self.__maxMinions)
        return

    def __onReplayTimeWarpFinished(self):
        self.__updateCurrentMinionDeathState()
