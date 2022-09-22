# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AreaMarker.py
import typing
from gui.shared.gui_items.marker_items import MarkerItem
from helpers import dependency
from script_component.DynamicScriptComponent import DynamicScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.area_marker_ctrl import AreaMarkersController

class AreaMarker(DynamicScriptComponent):

    def __init__(self):
        super(AreaMarker, self).__init__()
        sessionProvider = dependency.instance(IBattleSessionProvider)
        ctrl = sessionProvider.shared.areaMarker
        style = MarkerItem.__members__[self.style]
        marker = ctrl.createMarker(self.entity.matrix, style)
        marker.setEntity(self.entity)
        self.markerID = ctrl.addMarker(marker)

    def onDestroy(self):
        super(AreaMarker, self).onDestroy()
        sessionProvider = dependency.instance(IBattleSessionProvider)
        ctrl = sessionProvider.shared.areaMarker
        ctrl.removeMarker(self.markerID)
        self.markerID = None
        return
