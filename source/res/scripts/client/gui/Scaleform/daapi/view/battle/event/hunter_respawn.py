# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/hunter_respawn.py
import BigWorld
from gui.Scaleform.daapi.view.battle.event.boss_teleport import EventBossTeleportView
from gui.Scaleform.daapi.view.meta.EventHunterRespawnViewMeta import EventHunterRespawnViewMeta
from gui.battle_control import avatar_getter
from gui.wt_event.wt_event_helpers import getSpeed
from gui.shared.utils.graphics import isRendererPipelineDeferred

class EventHunterRespawnView(EventBossTeleportView, EventHunterRespawnViewMeta):

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
        applyTimerImmediately = isRendererPipelineDeferred() is False
        self.as_updateTimerS(timeLeft, timeTotal, applyTimerImmediately, replaySpeed=getSpeed())
