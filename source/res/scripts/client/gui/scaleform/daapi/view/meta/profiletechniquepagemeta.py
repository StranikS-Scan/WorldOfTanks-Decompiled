# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileTechniquePageMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileTechniquePageMeta(DAAPIModule):

    def setIsInHangarSelected(self, value):
        self._printOverrideError('setIsInHangarSelected')

    def as_setSelectedVehicleIntCDS(self, index):
        if self._isDAAPIInited():
            return self.flashObject.as_setSelectedVehicleIntCD(index)
