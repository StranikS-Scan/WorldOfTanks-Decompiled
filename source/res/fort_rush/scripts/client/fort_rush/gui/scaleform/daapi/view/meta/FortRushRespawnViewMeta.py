# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/meta/FortRushRespawnViewMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FortRushRespawnViewMeta(BaseDAAPIComponent):

    def onRespawnPointClick(self, id):
        self._printOverrideError('onRespawnPointClick')

    def onBattleButtonClicked(self, value):
        self._printOverrideError('onBattleButtonClicked')

    def as_setTimerS(self, value):
        return self.flashObject.as_setTimer(value) if self._isDAAPIInited() else None
