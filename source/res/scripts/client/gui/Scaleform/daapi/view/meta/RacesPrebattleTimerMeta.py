# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RacesPrebattleTimerMeta.py
from gui.Scaleform.daapi.view.battle.shared.battle_timers import PreBattleTimer

class RacesPrebattleTimerMeta(PreBattleTimer):

    def onFirstLight(self):
        self._printOverrideError('onFirstLight')

    def onLastLights(self):
        self._printOverrideError('onLastLights')

    def as_setColorBlindS(self, enabled):
        return self.flashObject.as_setColorBlind(enabled) if self._isDAAPIInited() else None
