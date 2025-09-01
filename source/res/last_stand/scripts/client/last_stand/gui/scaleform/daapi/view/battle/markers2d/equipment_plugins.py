# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/markers2d/equipment_plugins.py
from gui.Scaleform.daapi.view.battle.shared.markers2d.plugins import EquipmentsMarkerPlugin
from gui.Scaleform.daapi.view.battle.shared.markers2d import settings

class LSEquipmentsMarkerPlugin(EquipmentsMarkerPlugin):
    LS_EQUIPMENT_MARKER_LINKAGE = 'LSFortConsumablesMarkerUI'
    LS_MARKERS = ('LSEventDeathZoneUI',)

    def _getMarkerLinkage(self, item):
        return self.LS_EQUIPMENT_MARKER_LINKAGE if item.getMarker() in self.LS_MARKERS else settings.MARKER_SYMBOL_NAME.EQUIPMENT_MARKER
