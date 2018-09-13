# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationListButtonMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class NotificationListButtonMeta(DAAPIModule):

    def handleClick(self):
        self._printOverrideError('handleClick')

    def as_setStateS(self, isBlinking):
        if self._isDAAPIInited():
            return self.flashObject.as_setState(isBlinking)
