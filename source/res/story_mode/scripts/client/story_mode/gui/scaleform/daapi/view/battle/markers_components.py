# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/markers_components.py
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.component_marker.markers_components import PolygonalZoneMinimapMarkerComponent
from gui.battle_control import minimap_utils

class SMPolygonalZoneMinimapMarkerComponent(PolygonalZoneMinimapMarkerComponent):

    def _getSize(self):
        bottomLeft, topRight = BigWorld.player().arena.arenaType.boundingBox
        arenaSize = topRight - bottomLeft
        vSide, hSide = arenaSize
        if vSide > hSide:
            xc = minimap_utils.MINIMAP_SIZE[0] / vSide * 2
            yc = minimap_utils.MINIMAP_SIZE[1] / vSide * 2
        else:
            xc = minimap_utils.MINIMAP_SIZE[0] / hSide * 2
            yc = minimap_utils.MINIMAP_SIZE[1] / hSide * 2
        return (xc, yc)
