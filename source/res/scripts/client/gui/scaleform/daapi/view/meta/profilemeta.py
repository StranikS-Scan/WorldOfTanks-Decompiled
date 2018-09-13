# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileMeta(DAAPIModule):

    def onCloseProfile(self):
        self._printOverrideError('onCloseProfile')

    def as_updateS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_update(data)
