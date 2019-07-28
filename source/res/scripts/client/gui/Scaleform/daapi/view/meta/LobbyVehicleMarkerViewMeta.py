# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyVehicleMarkerViewMeta.py
from gui.Scaleform.framework.entities.View import View

class LobbyVehicleMarkerViewMeta(View):

    def as_createMarkerS(self, vType, vName, id):
        return self.flashObject.as_createMarker(vType, vName, id) if self._isDAAPIInited() else None

    def as_removeMarkerS(self, id):
        return self.flashObject.as_removeMarker(id) if self._isDAAPIInited() else None
