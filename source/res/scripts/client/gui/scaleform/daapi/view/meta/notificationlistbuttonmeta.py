# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationListButtonMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class NotificationListButtonMeta(BaseDAAPIComponent):

    def handleClick(self):
        self._printOverrideError('handleClick')

    def as_setStateS(self, isBlinking):
        if self._isDAAPIInited():
            return self.flashObject.as_setState(isBlinking)
