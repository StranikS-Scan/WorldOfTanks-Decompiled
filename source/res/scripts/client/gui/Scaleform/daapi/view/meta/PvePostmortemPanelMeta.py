# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PvePostmortemPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.postmortem_panel import PostmortemPanel

class PvePostmortemPanelMeta(PostmortemPanel):

    def as_setHintTitleS(self, value):
        return self.flashObject.as_setHintTitle(value) if self._isDAAPIInited() else None

    def as_setHintDescrS(self, value):
        return self.flashObject.as_setHintDescr(value) if self._isDAAPIInited() else None

    def as_setTimerS(self, totalTime, currentTime):
        return self.flashObject.as_setTimer(totalTime, currentTime) if self._isDAAPIInited() else None

    def as_setCanExitS(self, canExit):
        return self.flashObject.as_setCanExit(canExit) if self._isDAAPIInited() else None

    def as_showLockedLivesS(self):
        return self.flashObject.as_showLockedLives() if self._isDAAPIInited() else None

    def as_hidePanelS(self):
        return self.flashObject.as_hidePanel() if self._isDAAPIInited() else None
