# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RetrainCrewWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class RetrainCrewWindowMeta(AbstractWindowView):

    def submit(self, operationId):
        self._printOverrideError('submit')

    def changeRetrainType(self, retrainTypeIndex):
        self._printOverrideError('changeRetrainType')

    def as_setCrewDataS(self, data):
        return self.flashObject.as_setCrewData(data) if self._isDAAPIInited() else None

    def as_setVehicleDataS(self, data):
        return self.flashObject.as_setVehicleData(data) if self._isDAAPIInited() else None

    def as_setCrewOperationDataS(self, data):
        return self.flashObject.as_setCrewOperationData(data) if self._isDAAPIInited() else None
