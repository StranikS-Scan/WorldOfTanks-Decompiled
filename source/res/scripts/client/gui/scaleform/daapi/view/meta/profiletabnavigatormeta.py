# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileTabNavigatorMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileTabNavigatorMeta(DAAPIModule):

    def as_setInitDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setInitData(data)
