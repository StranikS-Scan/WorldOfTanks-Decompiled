# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/BattleRoyaleObserverInfoComponent.py
import BigWorld
import Event

class BattleRoyaleObserverInfoComponent(BigWorld.DynamicScriptComponent):
    onTeamsMayRespawnChanged = Event.Event()

    def set_teamsMayRespawn(self, prev):
        self.onTeamsMayRespawnChanged(self.teamsMayRespawn)
