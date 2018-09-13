# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileSectionMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileSectionMeta(DAAPIModule):

    def setActive(self, value):
        self._printOverrideError('setActive')

    def requestData(self, data):
        self._printOverrideError('requestData')

    def requestDossier(self, type):
        self._printOverrideError('requestDossier')

    def as_updateS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_update(data)

    def as_setInitDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setInitData(data)

    def as_responseDossierS(self, type, data):
        if self._isDAAPIInited():
            return self.flashObject.as_responseDossier(type, data)
