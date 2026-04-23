# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/meta/HBEnemiesPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HBEnemiesPanelMeta(BaseDAAPIComponent):

    def as_getEnemyInfoDPS(self):
        return self.flashObject.as_getEnemyInfoDP() if self._isDAAPIInited() else None

    def as_setEnemyHpS(self, vehID, hpMax, hpCurrent):
        return self.flashObject.as_setEnemyHp(vehID, hpMax, hpCurrent) if self._isDAAPIInited() else None

    def as_setChatCommandS(self, vehID, chatCommand, chatCommandFlags):
        return self.flashObject.as_setChatCommand(vehID, chatCommand, chatCommandFlags) if self._isDAAPIInited() else None

    def as_setChatCommandsVisibilityS(self, value):
        return self.flashObject.as_setChatCommandsVisibility(value) if self._isDAAPIInited() else None
