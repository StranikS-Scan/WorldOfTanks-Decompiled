# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileTechniqueMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileTechniqueMeta(DAAPIModule):

    def as_responseVehicleDossierS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_responseVehicleDossier(data)
