# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventBossProgressWidgetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class EventBossProgressWidgetMeta(BaseDAAPIComponent):

    def as_setWidgetDataS(self, data):
        return self.flashObject.as_setWidgetData(data) if self._isDAAPIInited() else None

    def as_updateHpS(self, hpCurrent):
        return self.flashObject.as_updateHp(hpCurrent) if self._isDAAPIInited() else None

    def as_updateKillsS(self, kills):
        return self.flashObject.as_updateKills(kills) if self._isDAAPIInited() else None

    def as_setHpRatioS(self, value):
        return self.flashObject.as_setHpRatio(value) if self._isDAAPIInited() else None
