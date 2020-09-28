# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WTEventEntryPointMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class WTEventEntryPointMeta(BaseDAAPIComponent):

    def onEntryClick(self):
        self._printOverrideError('onEntryClick')

    def as_setAnimationEnabledS(self, isEnabled):
        return self.flashObject.as_setAnimationEnabled(isEnabled) if self._isDAAPIInited() else None

    def as_setEndDateS(self, endDate):
        return self.flashObject.as_setEndDate(endDate) if self._isDAAPIInited() else None
