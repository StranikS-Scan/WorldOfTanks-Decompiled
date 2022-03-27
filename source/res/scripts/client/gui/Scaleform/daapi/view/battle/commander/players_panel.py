# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/players_panel.py
from gui.Scaleform.daapi.view.battle.classic.players_panel import PlayersPanel
from gui.battle_control import avatar_getter

class RTSPlayersPanel(PlayersPanel):

    def switchToOtherPlayer(self, vehicleID):
        if self.guiSessionProvider.getArenaDP().isPlayerCommander():
            return
        super(RTSPlayersPanel, self).switchToOtherPlayer(vehicleID)

    def updateVehicleHealth(self, vehicleID, newHealth, maxHealth):
        rtsCommander = self.guiSessionProvider.dynamic.rtsCommander
        vehicles = rtsCommander.vehicles.values(lambda v: v.isControllable)
        if rtsCommander is not None and vehicleID in vehicles and avatar_getter.isPlayerCommander():
            return
        else:
            super(RTSPlayersPanel, self).updateVehicleHealth(vehicleID, newHealth, maxHealth)
            return
