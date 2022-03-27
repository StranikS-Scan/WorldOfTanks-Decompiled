# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/MannerReminderMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class MannerReminderMeta(BaseDAAPIComponent):

    def as_setMannersS(self, manners):
        return self.flashObject.as_setManners(manners) if self._isDAAPIInited() else None

    def as_setEnabledS(self, enabled):
        return self.flashObject.as_setEnabled(enabled) if self._isDAAPIInited() else None
