# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HBRoleNotificationMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HBRoleNotificationMeta(BaseDAAPIComponent):

    def as_showS(self, roleImage, roleName, message):
        return self.flashObject.as_show(roleImage, roleName, message) if self._isDAAPIInited() else None
