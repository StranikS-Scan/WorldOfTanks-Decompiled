# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DemountBuildingWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class DemountBuildingWindowMeta(DAAPIModule):

    def applyDemount(self):
        self._printOverrideError('applyDemount')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
