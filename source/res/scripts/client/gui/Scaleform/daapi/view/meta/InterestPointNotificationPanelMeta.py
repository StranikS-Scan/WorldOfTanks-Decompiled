# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/InterestPointNotificationPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class InterestPointNotificationPanelMeta(BaseDAAPIComponent):

    def as_setCapturingStateS(self, notificationText, isPlayerTeam, timeLeft, timeTotal, replaySpeed=1):
        return self.flashObject.as_setCapturingState(notificationText, isPlayerTeam, timeLeft, timeTotal, replaySpeed) if self._isDAAPIInited() else None

    def as_setCapturedStateS(self, notificationText, isPlayerTeam, showTime, replaySpeed=1):
        return self.flashObject.as_setCapturedState(notificationText, isPlayerTeam, showTime, replaySpeed) if self._isDAAPIInited() else None

    def as_setCooldownStateS(self, timeLeft, timeTotal, replaySpeed=1):
        return self.flashObject.as_setCooldownState(timeLeft, timeTotal, replaySpeed) if self._isDAAPIInited() else None

    def as_setIsPostmortemS(self, isPostmortem):
        return self.flashObject.as_setIsPostmortem(isPostmortem) if self._isDAAPIInited() else None
