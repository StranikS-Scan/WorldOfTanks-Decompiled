# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyVehicleMarkerViewMeta.py
from gui.Scaleform.framework.entities.View import View

class LobbyVehicleMarkerViewMeta(View):

    def onMarkerClick(self, id):
        self._printOverrideError('onMarkerClick')

    def as_createMarkerS(self, id, vType, vName):
        return self.flashObject.as_createMarker(id, vType, vName) if self._isDAAPIInited() else None

    def as_createPlatoonMarkerS(self, id, vType, pName):
        return self.flashObject.as_createPlatoonMarker(id, vType, pName) if self._isDAAPIInited() else None

    def as_createCustomMarkerS(self, id, icon, text):
        return self.flashObject.as_createCustomMarker(id, icon, text) if self._isDAAPIInited() else None

    def as_createHBMarkerS(self, id, vType, vName, pName, pClan):
        return self.flashObject.as_createHBMarker(id, vType, vName, pName, pClan) if self._isDAAPIInited() else None

    def as_removeMarkerS(self, id):
        return self.flashObject.as_removeMarker(id) if self._isDAAPIInited() else None
