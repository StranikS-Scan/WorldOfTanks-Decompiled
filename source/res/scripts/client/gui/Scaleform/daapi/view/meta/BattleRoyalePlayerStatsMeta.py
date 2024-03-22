# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleRoyalePlayerStatsMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleRoyalePlayerStatsMeta(BaseDAAPIComponent):

    def as_setInitDataS(self, title):
        return self.flashObject.as_setInitData(title) if self._isDAAPIInited() else None

    def as_setDataS(self, value):
        return self.flashObject.as_setData(value) if self._isDAAPIInited() else None
