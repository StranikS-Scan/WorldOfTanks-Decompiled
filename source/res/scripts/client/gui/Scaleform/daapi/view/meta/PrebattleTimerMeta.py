# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PrebattleTimerMeta.py
from gui.Scaleform.daapi.view.battle.shared.prebattle_timers.timer_base import PreBattleTimerBase

class PrebattleTimerMeta(PreBattleTimerBase):

    def onShowInfo(self):
        self._printOverrideError('onShowInfo')

    def onHideInfo(self):
        self._printOverrideError('onHideInfo')

    def as_addInfoS(self, linkage, data):
        return self.flashObject.as_addInfo(linkage, data) if self._isDAAPIInited() else None

    def as_setInfoHintS(self, hint):
        return self.flashObject.as_setInfoHint(hint) if self._isDAAPIInited() else None
