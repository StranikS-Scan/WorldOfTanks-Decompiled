# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBuildingProcessWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortBuildingProcessWindowMeta(AbstractWindowView):

    def requestBuildingInfo(self, uid):
        self._printOverrideError('requestBuildingInfo')

    def applyBuildingProcess(self, uid):
        self._printOverrideError('applyBuildingProcess')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_responseBuildingInfoS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_responseBuildingInfo(data)
