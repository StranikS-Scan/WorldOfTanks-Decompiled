# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AnimatedBackgroundScreenMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class AnimatedBackgroundScreenMeta(BaseDAAPIComponent):

    def as_setImageDataS(self, backgroundImgPath, fogImgPath, animate):
        return self.flashObject.as_setImageData(backgroundImgPath, fogImgPath, animate) if self._isDAAPIInited() else None
