# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TargetDesignatorMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class TargetDesignatorMeta(VehicleMechanicWidget):

    def as_setPreparingProgressS(self, progress):
        return self.flashObject.as_setPreparingProgress(progress) if self._isDAAPIInited() else None
