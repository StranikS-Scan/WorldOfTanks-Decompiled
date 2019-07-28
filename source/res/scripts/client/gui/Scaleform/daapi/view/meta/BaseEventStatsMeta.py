# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseEventStatsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BaseEventStatsMeta(BaseDAAPIComponent):

    def as_setPersonalMissionsProgressS(self, data):
        return self.flashObject.as_setPersonalMissionsProgress(data) if self._isDAAPIInited() else None

    def as_setTeamMissionsVehiclesS(self, data):
        return self.flashObject.as_setTeamMissionsVehicles(data) if self._isDAAPIInited() else None
