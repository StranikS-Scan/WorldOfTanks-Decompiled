# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/GunStacksIndicatorsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class GunStacksIndicatorsMeta(BaseDAAPIComponent):

    def as_setVisibleS(self, value):
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None

    def as_setBonusS(self, value):
        return self.flashObject.as_setBonus(value) if self._isDAAPIInited() else None

    def as_setProgressS(self, idx, percent):
        return self.flashObject.as_setProgress(idx, percent) if self._isDAAPIInited() else None

    def as_setProgressAsPercentS(self, idx, percent):
        return self.flashObject.as_setProgressAsPercent(idx, percent) if self._isDAAPIInited() else None
