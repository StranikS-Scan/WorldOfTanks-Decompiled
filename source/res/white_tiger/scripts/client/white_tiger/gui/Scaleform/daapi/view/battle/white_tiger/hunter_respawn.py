# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/white_tiger/hunter_respawn.py
import BigWorld
from gui.battle_control import avatar_getter
from gui.wt_event.wt_event_helpers import getSpeed
from white_tiger.gui.Scaleform.daapi.view.battle.white_tiger.boss_teleport import WhiteTigerBossTeleportView
from white_tiger.gui.Scaleform.daapi.view.meta.WTHunterRespawnViewMeta import WTHunterRespawnViewMeta

class WhiteTigerHunterRespawnView(WhiteTigerBossTeleportView, WTHunterRespawnViewMeta):

    def onRespawnPointClick(self, pointGuid):
        self._chooseSpawnPoint(pointGuid)

    def showSpawnPoints(self):
        self._blur.enable()
        vehicle = avatar_getter.getPlayerVehicle()
        respawnComponent = vehicle.dynamicComponents.get('VehicleRespawnComponent')
        if not respawnComponent:
            return
        timeLeft = respawnComponent.spawnTime - BigWorld.serverTime()
        timeTotal = respawnComponent.delay
        self.as_updateTimerS(timeLeft, timeTotal, replaySpeed=getSpeed())
