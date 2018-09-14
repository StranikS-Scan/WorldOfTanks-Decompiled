# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/QuestsPersonalWelcomeViewMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class QuestsPersonalWelcomeViewMeta(DAAPIModule):

    def success(self):
        self._printOverrideError('success')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
