# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TeamInfoLivesComponent.py
import BigWorld
import Event
from helpers import isPlayerAvatar
from script_component.DynamicScriptComponent import DynamicScriptComponent

class TeamInfoLivesComponent(DynamicScriptComponent):

    def __init__(self, *_, **__):
        super(TeamInfoLivesComponent, self).__init__(*_, **__)
        self.onTeamLivesUpdated = Event.SafeEvent()

    def onDestroy(self):
        self.onTeamLivesUpdated.clear()
        super(TeamInfoLivesComponent, self).onDestroy()

    def _onAvatarReady(self):
        self.onTeamLivesUpdated()

    def set_teamLives(self, prev):
        if self._isAvatarReady:
            self.onTeamLivesUpdated()

    def getLives(self, vehicleID):
        return self.getVehicleLives(vehicleID).get('lives', 0)

    def getLockedLives(self, vehicleID):
        return self.getVehicleLives(vehicleID).get('lockedLives', 0)

    def getUsedLives(self, vehicleID):
        return self.getVehicleLives(vehicleID).get('usedLives', 0)

    def getVehicleLives(self, vehicleID):
        for vl in self.teamLives:
            if vl['vehicleID'] == vehicleID:
                return dict(vl)

        return {}

    @classmethod
    def getInstance(cls):
        if not isPlayerAvatar():
            return None
        else:
            player = BigWorld.player()
            if not player:
                return None
            return None if not player.arena or not player.arena.teamInfo else getattr(player.arena.teamInfo, 'teamLivesComponent', None)
