# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/FlashTweenMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FlashTweenMeta(DAAPIModule):

    def moveOnPositionS(self, percent):
        if self._isDAAPIInited():
            return self.flashObject.moveOnPosition(percent)
