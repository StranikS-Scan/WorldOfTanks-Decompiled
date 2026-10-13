# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/markers2d/equipment_plugins.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import EquipmentsMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings

class HalloweenEquipmentsMarkerPlugin(EquipmentsMarkerPlugin):
    HW_EQUIPMENT_MARKER_LINKAGE = 'HWFortConsumablesMarkerUI'
    HW_MARKERS = ('EventDeathZoneUI', 'EventDeathZoneIgniteUI', 'EventDeathZoneStunUI', 'EventDeathZoneDamageOvertimeUI')

    def _getMarkerLinkage(self, item):
        return self.HW_EQUIPMENT_MARKER_LINKAGE if item.getMarker() in self.HW_MARKERS else settings.MARKER_SYMBOL_NAME.EQUIPMENT_MARKER
