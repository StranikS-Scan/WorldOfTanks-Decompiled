# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TmenXpPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class TmenXpPanelMeta(BaseDAAPIComponent):

    def accelerateTmenXp(self, selected):
        self._printOverrideError('accelerateTmenXp')

    def as_setTankmenXpPanelS(self, visible, selected):
        if self._isDAAPIInited():
            return self.flashObject.as_setTankmenXpPanel(visible, selected)
