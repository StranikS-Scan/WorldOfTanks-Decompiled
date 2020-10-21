# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseBattleQueueMeta.py
from gui.Scaleform.framework.entities.View import View

class BaseBattleQueueMeta(View):

    def exitClick(self):
        self._printOverrideError('exitClick')

    def onEscape(self):
        self._printOverrideError('onEscape')

    def as_setTimerS(self, textLabel, timeLabel):
        return self.flashObject.as_setTimer(textLabel, timeLabel) if self._isDAAPIInited() else None

    def as_showExitS(self, vis):
        return self.flashObject.as_showExit(vis) if self._isDAAPIInited() else None
