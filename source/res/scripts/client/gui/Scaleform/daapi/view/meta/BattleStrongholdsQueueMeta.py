# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleStrongholdsQueueMeta.py
from gui.Scaleform.framework.entities.View import View

class BattleStrongholdsQueueMeta(View):

    def exitClick(self):
        self._printOverrideError('exitClick')

    def onEscape(self):
        self._printOverrideError('onEscape')

    def as_setTimerS(self, textLabel, timeLabel):
        return self.flashObject.as_setTimer(textLabel, timeLabel) if self._isDAAPIInited() else None

    def as_setTypeInfoS(self, data):
        return self.flashObject.as_setTypeInfo(data) if self._isDAAPIInited() else None

    def as_setLeaguesS(self, data):
        return self.flashObject.as_setLeagues(data) if self._isDAAPIInited() else None

    def as_showExitS(self, vis):
        return self.flashObject.as_showExit(vis) if self._isDAAPIInited() else None

    def as_showWaitingS(self, description):
        return self.flashObject.as_showWaiting(description) if self._isDAAPIInited() else None

    def as_hideWaitingS(self):
        return self.flashObject.as_hideWaiting() if self._isDAAPIInited() else None
