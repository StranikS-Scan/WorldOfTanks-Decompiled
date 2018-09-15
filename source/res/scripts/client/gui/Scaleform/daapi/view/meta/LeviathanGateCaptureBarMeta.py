# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LeviathanGateCaptureBarMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class LeviathanGateCaptureBarMeta(BaseDAAPIComponent):

    def as_isColorBlindS(self, isTrue):
        return self.flashObject.as_isColorBlind(isTrue) if self._isDAAPIInited() else None

    def as_showS(self):
        return self.flashObject.as_show() if self._isDAAPIInited() else None

    def as_hideS(self):
        return self.flashObject.as_hide() if self._isDAAPIInited() else None

    def as_setCommentS(self, comment):
        return self.flashObject.as_setComment(comment) if self._isDAAPIInited() else None

    def as_updateTimeDisplayS(self, formattedTimeString):
        return self.flashObject.as_updateTimeDisplay(formattedTimeString) if self._isDAAPIInited() else None

    def as_updateHealthS(self, val):
        return self.flashObject.as_updateHealth(val) if self._isDAAPIInited() else None

    def as_setLeviathanHealthS(self, maxHealth, currentHealth):
        return self.flashObject.as_setLeviathanHealth(maxHealth, currentHealth) if self._isDAAPIInited() else None
