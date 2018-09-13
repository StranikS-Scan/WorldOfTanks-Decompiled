# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortBuildingProcessWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortBuildingProcessWindowMeta(DAAPIModule):

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
