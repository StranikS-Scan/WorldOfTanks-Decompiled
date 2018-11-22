# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PrebattleTimerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PrebattleTimerMeta(BaseDAAPIComponent):

    def onShowFlag(self):
        self._printOverrideError('onShowFlag')

    def onHideFlag(self):
        self._printOverrideError('onHideFlag')

    def as_setTimerS(self, totalTime):
        return self.flashObject.as_setTimer(totalTime) if self._isDAAPIInited() else None

    def as_setMessageS(self, msg):
        return self.flashObject.as_setMessage(msg) if self._isDAAPIInited() else None

    def as_hideAllS(self, useAnim):
        return self.flashObject.as_hideAll(useAnim) if self._isDAAPIInited() else None

    def as_setWinConditionTextS(self, winCondition):
        return self.flashObject.as_setWinConditionText(winCondition) if self._isDAAPIInited() else None

    def as_setQuestHintS(self, questHint):
        return self.flashObject.as_setQuestHint(questHint) if self._isDAAPIInited() else None
