# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortDemountBuildingWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortDemountBuildingWindowMeta(DAAPIModule):

    def applyDemount(self):
        self._printOverrideError('applyDemount')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
