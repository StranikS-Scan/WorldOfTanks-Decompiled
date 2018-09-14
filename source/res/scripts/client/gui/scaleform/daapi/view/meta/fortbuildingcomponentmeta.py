# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBuildingComponentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FortBuildingComponentMeta(BaseDAAPIComponent):

    def onTransportingRequest(self, exportFrom, importTo):
        self._printOverrideError('onTransportingRequest')

    def requestBuildingProcess(self, direction, position):
        self._printOverrideError('requestBuildingProcess')

    def upgradeVisitedBuilding(self, uid):
        self._printOverrideError('upgradeVisitedBuilding')

    def requestBuildingToolTipData(self, uid, type):
        self._printOverrideError('requestBuildingToolTipData')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setBuildingDataS(self, data):
        return self.flashObject.as_setBuildingData(data) if self._isDAAPIInited() else None

    def as_setBuildingToolTipDataS(self, uid, type, header, value):
        return self.flashObject.as_setBuildingToolTipData(uid, type, header, value) if self._isDAAPIInited() else None

    def as_refreshTransportingS(self):
        return self.flashObject.as_refreshTransporting() if self._isDAAPIInited() else None
