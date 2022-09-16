# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/Comp7PrebattleTimerMeta.py
from gui.Scaleform.daapi.view.battle.shared.battle_timers import PreBattleTimer

class Comp7PrebattleTimerMeta(PreBattleTimer):

    def onReadyBtnClick(self):
        self._printOverrideError('onReadyBtnClick')

    def as_hideInfoS(self):
        return self.flashObject.as_hideInfo() if self._isDAAPIInited() else None
