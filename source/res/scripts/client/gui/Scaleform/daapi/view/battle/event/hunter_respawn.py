# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/hunter_respawn.py
import BigWorld
from cgf_components.wt_helpers import getPlayerLives
from gui.Scaleform.daapi.view.battle.event.boss_teleport import EventBossTeleportView
from gui.Scaleform.daapi.view.meta.EventHunterRespawnViewMeta import EventHunterRespawnViewMeta
from gui.wt_event.wt_event_helpers import getSpeed
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getIconResourceName

class EventHunterRespawnView(EventBossTeleportView, EventHunterRespawnViewMeta):

    def onRespawnPointClick(self, pointGuid):
        self._chooseSpawnPoint(pointGuid)

    def showSpawnPoints(self):
        self._blur.enable()
        timeLeft = 0
        timeTotal = 0
        respawnComponent = BigWorld.player().dynamicComponents.get('respawnComponent')
        if respawnComponent:
            timeLeft = respawnComponent.endTime - BigWorld.serverTime()
            timeTotal = respawnComponent.duration
        self.as_updateTimerS(timeLeft, timeTotal, replaySpeed=getSpeed())
        self.as_setLifesCountS(getPlayerLives())
        vTypeVO = self._sessionProvider.getCtx().getVehicleInfo(BigWorld.player().playerVehicleID).vehicleType
        iconName = getIconResourceName(vTypeVO.iconName)
        icon = R.images.gui.maps.icons.wtevent.hunterRespawn.dyn(iconName)
        if icon.exists():
            self.as_setIconS(backport.image(icon()))
