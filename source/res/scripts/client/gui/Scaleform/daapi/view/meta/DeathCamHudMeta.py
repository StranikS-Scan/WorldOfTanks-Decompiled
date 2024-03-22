# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DeathCamHudMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DeathCamHudMeta(BaseDAAPIComponent):

    def onAnimationFinished(self):
        self._printOverrideError('onAnimationFinished')

    def as_setTextsS(self, cameraText, skipText):
        return self.flashObject.as_setTexts(cameraText, skipText) if self._isDAAPIInited() else None

    def as_showBarsS(self):
        return self.flashObject.as_showBars() if self._isDAAPIInited() else None

    def as_hideBarsS(self, isActive):
        return self.flashObject.as_hideBars(isActive) if self._isDAAPIInited() else None
