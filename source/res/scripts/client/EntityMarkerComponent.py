# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EntityMarkerComponent.py
import typing
from script_component.DynamicScriptComponent import DynamicScriptComponent
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.area_marker_ctrl import AreaMarkersController

class EntityMarkerComponent(DynamicScriptComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EntityMarkerComponent, self).__init__()
        ctrl = self.sessionProvider.shared.areaMarker
        marker = ctrl.createMarker(self.entity.matrix, self.style)
        marker.setEntity(self.entity)
        self.markerID = ctrl.addMarker(marker)

    def onDestroy(self):
        super(EntityMarkerComponent, self).onDestroy()
        ctrl = self.sessionProvider.shared.areaMarker
        ctrl.removeMarker(self.markerID)
        self.markerID = None
        return
