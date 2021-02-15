# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleRoyaleHangarWidgetMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleRoyaleHangarWidgetMeta(BaseDAAPIComponent):

    def onClick(self):
        self._printOverrideError('onClick')

    def onChangeServerClick(self):
        self._printOverrideError('onChangeServerClick')

    def as_setDataS(self, data):
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None
