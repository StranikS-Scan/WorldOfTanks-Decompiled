# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PanelVehiclesMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class PanelVehiclesMeta(BaseDAAPIComponent):

    def as_setCountLivesS(self, countLives):
        return self.flashObject.as_setCountLives(countLives) if self._isDAAPIInited() else None
