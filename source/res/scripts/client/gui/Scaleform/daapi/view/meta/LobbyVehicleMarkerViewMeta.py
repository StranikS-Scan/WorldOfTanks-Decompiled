# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyVehicleMarkerViewMeta.py
from gui.Scaleform.framework.entities.View import View

class LobbyVehicleMarkerViewMeta(View):

    def as_createVehMarkerS(self, vType, vName):
        return self.flashObject.as_createVehMarker(vType, vName) if self._isDAAPIInited() else None

    def as_createEventMarkerS(self, id, count, text):
        return self.flashObject.as_createEventMarker(id, count, text) if self._isDAAPIInited() else None

    def as_updateEventMarkerCountS(self, id, value):
        return self.flashObject.as_updateEventMarkerCount(id, value) if self._isDAAPIInited() else None

    def as_updateEventMarkerTextS(self, id, value):
        return self.flashObject.as_updateEventMarkerText(id, value) if self._isDAAPIInited() else None

    def as_setEventMarkerLockedS(self, id, value):
        return self.flashObject.as_setEventMarkerLocked(id, value) if self._isDAAPIInited() else None

    def as_removeVehMarkerS(self):
        return self.flashObject.as_removeVehMarker() if self._isDAAPIInited() else None

    def as_removeEventMarkerS(self, id):
        return self.flashObject.as_removeEventMarker(id) if self._isDAAPIInited() else None
