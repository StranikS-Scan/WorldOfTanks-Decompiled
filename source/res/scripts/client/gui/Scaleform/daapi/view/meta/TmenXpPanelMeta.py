# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TmenXpPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class TmenXpPanelMeta(BaseDAAPIComponent):

    def accelerateTmenXp(self, selected):
        self._printOverrideError('accelerateTmenXp')

    def as_setTankmenXpPanelS(self, visible, selected, enabled, label):
        return self.flashObject.as_setTankmenXpPanel(visible, selected, enabled, label) if self._isDAAPIInited() else None

    def as_setAccelerateCheckboxTooltipS(self, tooltip):
        return self.flashObject.as_setAccelerateCheckboxTooltip(tooltip) if self._isDAAPIInited() else None
