# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/meta/HWBossIndicatorProgressMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HWBossIndicatorProgressMeta(BaseDAAPIComponent):

    def as_setValueS(self, value):
        return self.flashObject.as_setValue(value) if self._isDAAPIInited() else None

    def as_setIndicatorEnabledS(self, isEnabled):
        return self.flashObject.as_setIndicatorEnabled(isEnabled) if self._isDAAPIInited() else None

    def as_setAlphaS(self, alpha):
        return self.flashObject.as_setAlpha(alpha) if self._isDAAPIInited() else None
