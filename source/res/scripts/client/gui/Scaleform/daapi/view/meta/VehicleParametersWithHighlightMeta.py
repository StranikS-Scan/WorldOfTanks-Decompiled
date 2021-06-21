# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleParametersWithHighlightMeta.py
from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehicleParameters

class VehicleParametersWithHighlightMeta(VehicleParameters):

    def as_showChangesS(self):
        return self.flashObject.as_showChanges() if self._isDAAPIInited() else None
