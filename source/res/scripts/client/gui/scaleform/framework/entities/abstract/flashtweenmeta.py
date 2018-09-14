# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/FlashTweenMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class FlashTweenMeta(BaseDAAPIModule):

    def moveOnPositionS(self, percent):
        if self._isDAAPIInited():
            return self.flashObject.moveOnPosition(percent)
