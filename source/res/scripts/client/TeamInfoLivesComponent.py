# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TeamInfoLivesComponent.py
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class TeamInfoLivesComponent(DynamicScriptComponent):

    def onAvatarReady(self):
        self.__updateTeamLives()
        self.__updateRespawnInfo(self.respawnInfo.keys() if self.respawnInfo else tuple())

    @property
    def _uiCtrl(self):
        return BigWorld.player().guiSessionProvider.dynamic.spawn

    def set_teamLives(self, prev):
        self.__updateTeamLives()
        if self._uiCtrl is not None and BigWorld.player().playerVehicleID in self.teamLives:
            self._uiCtrl.onTeamLivesSetted()
        return

    def set_respawnInfo(self, prev):
        self.__updateRespawnInfo([ k for k, v in self.respawnInfo.iteritems() if v != prev.get(k) ])

    def getLives(self, vehicleID):
        teamLives = dict(self.teamLives) if self.teamLives else {}
        return teamLives.get(vehicleID, 0)

    def getRespawnInfo(self, vehicleID):
        respawnInfo = dict(self.respawnInfo) if self.respawnInfo else {}
        return (respawnInfo.get(vehicleID, 0), self.respawnTime)

    def __updateTeamLives(self):
        if self._uiCtrl is not None:
            self._uiCtrl.onTeamLivesUpdated()
        return

    def __updateRespawnInfo(self, changedVehicleIDs):
        guiSessionProvider = dependency.instance(IBattleSessionProvider)
        for vehId in changedVehicleIDs:
            guiSessionProvider.setVehicleHealth(False, vehId, 0, 0, 0)

        if self._uiCtrl is not None:
            self._uiCtrl.onTeamRespawnInfoUpdated(changedVehicleIDs)
        return
