# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/death_cam_hud.py
from gui.Scaleform.daapi.view.meta.DeathCamHudMeta import DeathCamHudMeta
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import GameEvent, DeathCamEvent

class DeathCamHud(DeathCamHudMeta):

    def onAnimationFinished(self):
        self.fireEvent(GameEvent(DeathCamEvent.DEATH_CAM_HIDDEN), scope=EVENT_BUS_SCOPE.BATTLE)
