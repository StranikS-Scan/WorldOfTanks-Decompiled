# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PveBossIndicatorProgressMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PveBossIndicatorProgressMeta(BaseDAAPIComponent):

    def as_setValueS(self, value):
        return self.flashObject.as_setValue(value) if self._isDAAPIInited() else None

    def as_setIndicatorEnabledS(self, isEnabled):
        return self.flashObject.as_setIndicatorEnabled(isEnabled) if self._isDAAPIInited() else None
