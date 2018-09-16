# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FootballFadeOverlayMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FootballFadeOverlayMeta(BaseDAAPIComponent):

    def as_setFadeS(self, isFadeIn, delayFade):
        return self.flashObject.as_setFade(isFadeIn, delayFade) if self._isDAAPIInited() else None
