# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/NotificationListButtonMeta.py
"""
This file was generated using the wgpygen.
Please, don't edit this file manually.
"""
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class NotificationListButtonMeta(BaseDAAPIComponent):

    def handleClick(self):
        self._printOverrideError('handleClick')

    def as_setStateS(self, isBlinking, counterValue):
        return self.flashObject.as_setState(isBlinking, counterValue) if self._isDAAPIInited() else None
