# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventStatsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventStatsMeta(BaseDAAPIComponent):

    def as_setTeamMissionsProgressS(self, data):
        return self.flashObject.as_setTeamMissionsProgress(data) if self._isDAAPIInited() else None

    def as_setTeamMissionsVehiclesS(self, data):
        return self.flashObject.as_setTeamMissionsVehicles(data) if self._isDAAPIInited() else None
