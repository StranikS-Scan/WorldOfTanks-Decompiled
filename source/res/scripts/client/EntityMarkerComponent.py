# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EntityMarkerComponent.py
import typing
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from historical_battles_common.hb_constants_extension import ARENA_GUI_TYPE
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.area_marker_ctrl import AreaMarkersController

class EntityMarkerComponent(DynamicScriptComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EntityMarkerComponent, self).__init__()
        self.markerID = None
        arenaGuiType = BigWorld.player().arenaGuiType
        self.__isEnabled = arenaGuiType != ARENA_GUI_TYPE.HISTORICAL_BATTLES
        return

    def onDestroy(self):
        super(EntityMarkerComponent, self).onDestroy()
        if self.markerID is None:
            return
        else:
            ctrl = self.sessionProvider.shared.areaMarker
            ctrl.removeMarker(self.markerID)
            self.markerID = None
            return

    def _onAvatarReady(self):
        super(EntityMarkerComponent, self)._onAvatarReady()
        if not self.__isEnabled:
            return
        ctrl = self.sessionProvider.shared.areaMarker
        marker = ctrl.createMarker(self.entity.matrix, self.style)
        marker.setEntity(self.entity)
        self.markerID = ctrl.addMarker(marker)
