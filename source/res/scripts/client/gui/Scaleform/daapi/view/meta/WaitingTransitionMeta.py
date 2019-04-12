# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WaitingTransitionMeta.py
from gui.Scaleform.daapi.view.meta.DAAPISimpleContainerMeta import DAAPISimpleContainerMeta

class WaitingTransitionMeta(DAAPISimpleContainerMeta):

    def as_setTransitionTextS(self, text):
        return self.flashObject.as_setTransitionText(text) if self._isDAAPIInited() else None

    def as_updateStageS(self, width, height, scale):
        return self.flashObject.as_updateStage(width, height, scale) if self._isDAAPIInited() else None

    def as_showBGS(self):
        return self.flashObject.as_showBG() if self._isDAAPIInited() else None

    def as_hideBGS(self):
        return self.flashObject.as_hideBG() if self._isDAAPIInited() else None
