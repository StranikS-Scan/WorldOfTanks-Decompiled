# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/players_panel.py
import BigWorld
from gui.battle_control.controllers.players_panel_ctrl import IPlayersPanelListener, isBossBot
from gui.Scaleform.daapi.view.meta.EventPlayersPanelMeta import EventPlayersPanelMeta
from gui.wt_event.wt_event_helpers import isBoss

class EventPlayersPanel(EventPlayersPanelMeta, IPlayersPanelListener):

    def _populate(self):
        super(EventPlayersPanel, self)._populate()
        self.as_setIsBossS(self.__isBossPlayer())

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        if newHealth < 0:
            newHealth = 0
        if isBossBot(vehicleID):
            self.as_updateBossBotHpS(vehicleID, maxHealth, newHealth)
        else:
            super(EventPlayersPanel, self).updateVehicleHealth(vehicleID, newHealth, maxHealth)

    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        for vehicleID in deadEnemies | deadAllies:
            if not isBossBot(vehicleID):
                continue
            arenaDP = self.sessionProvider.getArenaDP()
            vInfo = arenaDP.getVehicleInfo(vehicleID)
            self.as_updateBossBotHpS(vehicleID, vInfo.vehicleType.maxHealth, 0)

    def updateSpottedStatus(self, vehicleID, spottedState):
        if isBossBot(vehicleID):
            self.as_setBossBotSpottedS(vehicleID, spottedState)

    def updateCamp(self, campID, vInfos):
        for vInfo in vInfos:
            botInfo = {'typeVehicle': vInfo.vehicleType.classTag,
             'hpMax': vInfo.vehicleType.maxHealth,
             'hpCurrent': vInfo.vehicleType.maxHealth,
             'vehID': vInfo.vehicleID,
             'vehicleIcon': vInfo.vehicleType.iconName,
             'campIndex': campID}
            self.as_setBossBotInfoS(botInfo)

    def destroyCamp(self, campID):
        self.as_clearBossBotCampS(campID)

    def _handleNextMode(self, _):
        pass

    def __isBossPlayer(self):
        vInfo = self.sessionProvider.getCtx().getVehicleInfo(BigWorld.player().playerVehicleID)
        tags = vInfo.vehicleType.tags
        return isBoss(tags)
