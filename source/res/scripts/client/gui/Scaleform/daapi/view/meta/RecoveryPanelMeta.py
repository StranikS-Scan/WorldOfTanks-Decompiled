# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RecoveryPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class RecoveryPanelMeta(BaseDAAPIComponent):

    def as_updateTimerS(self, time):
        return self.flashObject.as_updateTimer(time) if self._isDAAPIInited() else None

    def as_displayHintS(self, display, animate):
        return self.flashObject.as_displayHint(display, animate) if self._isDAAPIInited() else None

    def as_displayCooldownS(self, display, animate):
        return self.flashObject.as_displayCooldown(display, animate) if self._isDAAPIInited() else None

    def as_setupTextsS(self, hint1, hint2, button):
        return self.flashObject.as_setupTexts(hint1, hint2, button) if self._isDAAPIInited() else None

    def as_updateTextsS(self, button):
        return self.flashObject.as_updateTexts(button) if self._isDAAPIInited() else None
