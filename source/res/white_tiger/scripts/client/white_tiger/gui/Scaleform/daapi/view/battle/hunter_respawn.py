# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/hunter_respawn.py
import BigWorld
from gui.battle_control import avatar_getter
from gui.shared.utils.graphics import isLowPreset
from white_tiger.gui.Scaleform.daapi.view.meta.WhiteTigerHunterRespawnViewMeta import WhiteTigerHunterRespawnViewMeta
from white_tiger.gui.wt_event_helpers import getSpeed
from white_tiger.gui.Scaleform.daapi.view.battle.boss_teleport import WhiteTigerBossTeleportView

class WhiteTigerHunterRespawnView(WhiteTigerBossTeleportView, WhiteTigerHunterRespawnViewMeta):

    def onRespawnPointClick(self, pointGuid):
        self._chooseSpawnPoint(pointGuid)

    def showSpawnPoints(self):
        self._blur.enable()
        vehicle = avatar_getter.getPlayerVehicle()
        respawnComponent = vehicle.dynamicComponents.get('WTMapPointSelectorComponent')
        if not respawnComponent:
            return
        timeLeft = respawnComponent.endTime - BigWorld.serverTime()
        timeTotal = respawnComponent.duration
        applyTimerImmediately = isLowPreset()
        self.as_updateTimerS(timeLeft, timeTotal, applyTimerImmediately, replaySpeed=getSpeed())
