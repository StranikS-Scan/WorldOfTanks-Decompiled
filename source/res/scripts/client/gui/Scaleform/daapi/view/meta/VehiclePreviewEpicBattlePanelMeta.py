# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehiclePreviewEpicBattlePanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class VehiclePreviewEpicBattlePanelMeta(BaseDAAPIComponent):

    def as_setDataS(self, title, description):
        return self.flashObject.as_setData(title, description) if self._isDAAPIInited() else None
