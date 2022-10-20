# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/HWBattleLoadingMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HWBattleLoadingMeta(BaseDAAPIComponent):

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_updateProgressS(self, percent):
        return self.flashObject.as_updateProgress(percent) if self._isDAAPIInited() else None
