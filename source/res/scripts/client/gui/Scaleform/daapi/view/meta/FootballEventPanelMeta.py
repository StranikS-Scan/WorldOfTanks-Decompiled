# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FootballEventPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class FootballEventPanelMeta(BaseDAAPIComponent):

    def as_setFootballVehiclePanelDataS(self, visible, footballData):
        return self.flashObject.as_setFootballVehiclePanelData(visible, footballData) if self._isDAAPIInited() else None
