# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/meta/HBSPGPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HBSPGPanelMeta(BaseDAAPIComponent):

    def as_showS(self):
        return self.flashObject.as_show() if self._isDAAPIInited() else None

    def as_setSPGListS(self, spgList):
        return self.flashObject.as_setSPGList(spgList) if self._isDAAPIInited() else None

    def as_setSPGHpS(self, vehID, hpMax, hpCurrent):
        return self.flashObject.as_setSPGHp(vehID, hpMax, hpCurrent) if self._isDAAPIInited() else None

    def as_hideTitleS(self):
        return self.flashObject.as_hideTitle() if self._isDAAPIInited() else None
