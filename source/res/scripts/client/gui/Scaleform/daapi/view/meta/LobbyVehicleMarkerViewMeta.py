# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyVehicleMarkerViewMeta.py
from gui.Scaleform.framework.entities.View import View

class LobbyVehicleMarkerViewMeta(View):

    def as_createMarkerS(self, vType, vName):
        return self.flashObject.as_createMarker(vType, vName) if self._isDAAPIInited() else None

    def as_removeMarkerS(self):
        return self.flashObject.as_removeMarker() if self._isDAAPIInited() else None
