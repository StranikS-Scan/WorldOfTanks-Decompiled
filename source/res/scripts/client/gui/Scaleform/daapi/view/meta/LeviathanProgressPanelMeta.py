# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LeviathanProgressPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class LeviathanProgressPanelMeta(BaseDAAPIComponent):

    def as_updateLeviathanProgressS(self, progress):
        return self.flashObject.as_updateLeviathanProgress(progress) if self._isDAAPIInited() else None

    def as_updateLeviathanHealthS(self, percent):
        return self.flashObject.as_updateLeviathanHealth(percent) if self._isDAAPIInited() else None

    def as_setLeviathanHealthS(self, currHealth, maxHealth):
        return self.flashObject.as_setLeviathanHealth(currHealth, maxHealth) if self._isDAAPIInited() else None

    def as_isColorBlindS(self, isTrue):
        return self.flashObject.as_isColorBlind(isTrue) if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None
