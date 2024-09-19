# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventMiniBossWidgetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventMiniBossWidgetMeta(BaseDAAPIComponent):

    def as_setMiniBossWidgetDataS(self, miniBossName, hpCurrent, hpMax, isEnemy):
        return self.flashObject.as_setMiniBossWidgetData(miniBossName, hpCurrent, hpMax, isEnemy) if self._isDAAPIInited() else None

    def as_updateMiniBossHpS(self, newHealth):
        return self.flashObject.as_updateMiniBossHp(newHealth) if self._isDAAPIInited() else None

    def as_resetMiniBossWidgetS(self):
        return self.flashObject.as_resetMiniBossWidget() if self._isDAAPIInited() else None
