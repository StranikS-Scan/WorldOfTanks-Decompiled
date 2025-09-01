# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/WTRespawnTimeInfo.py
import Event
from script_component.DynamicScriptComponent import DynamicScriptComponent

class WTRespawnTimeInfo(DynamicScriptComponent):

    def __init__(self, *_, **__):
        super(WTRespawnTimeInfo, self).__init__(*_, **__)
        self.onTeamLivesUpdated = Event.SafeEvent()
        self.onRespawnInfoUpdated = Event.Event()

    def onDestroy(self):
        self.onTeamLivesUpdated.clear()
        super(WTRespawnTimeInfo, self).onDestroy()

    def _onAvatarReady(self):
        self.onTeamLivesUpdated()
        self.onRespawnInfoUpdated(self.__getRespawnInfoIDs())

    def set_respawnInfo(self, prev):
        self.onRespawnInfoUpdated(self.__getRespawnInfoIDs())

    def getRespawnInfo(self, vehicleID):
        for entry in self.respawnInfo:
            if entry['vehicleID'] != vehicleID:
                continue
            return (entry.spawnTime, entry.delay)

    def __getRespawnInfoIDs(self):
        if self.respawnInfo is None:
            return []
        else:
            return [ entry['vehicleID'] for entry in self.respawnInfo ]
