# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleHintPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class BattleHintPanelMeta(BaseDAAPIComponent):

    def onPlaySound(self, soundType):
        self._printOverrideError('onPlaySound')

    def as_setDataS(self, key, messageLeft, messageRight, offsetX, offsetY):
        return self.flashObject.as_setData(key, messageLeft, messageRight, offsetX, offsetY) if self._isDAAPIInited() else None
