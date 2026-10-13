# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/meta/NitroIndicatorMeta.py
from gui.Scaleform.daapi.view.meta.RocketAcceleratorIndicatorMeta import RocketAcceleratorIndicatorMeta

class NitroIndicatorMeta(RocketAcceleratorIndicatorMeta):

    def as_setKeyS(self, key):
        return self.flashObject.as_setKey(key) if self._isDAAPIInited() else None

    def as_setTooltipS(self, tooltip):
        return self.flashObject.as_setTooltip(tooltip) if self._isDAAPIInited() else None
