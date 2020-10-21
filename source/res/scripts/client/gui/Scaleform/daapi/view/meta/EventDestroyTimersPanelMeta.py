# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EventDestroyTimersPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.timers_panel import TimersPanel

class EventDestroyTimersPanelMeta(TimersPanel):

    def setComponentsOverlay(self, isRibbonsPanelOverlay, isBuffsPanelOverlay):
        self._printOverrideError('setComponentsOverlay')

    def as_setWarningTextS(self, text, vis):
        return self.flashObject.as_setWarningText(text, vis) if self._isDAAPIInited() else None

    def as_setFillingInProgressS(self, current, total, isActive, visible):
        return self.flashObject.as_setFillingInProgress(current, total, isActive, visible) if self._isDAAPIInited() else None

    def as_setGotoPointTimerS(self, timeLeft, timeMax, message, visible):
        return self.flashObject.as_setGotoPointTimer(timeLeft, timeMax, message, visible) if self._isDAAPIInited() else None

    def as_setWaitForAlliesS(self, visible):
        return self.flashObject.as_setWaitForAllies(visible) if self._isDAAPIInited() else None

    def as_hideAllNotificationsS(self):
        return self.flashObject.as_hideAllNotifications() if self._isDAAPIInited() else None
