# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SupportWeaponWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class SupportWeaponWidgetMeta(VehicleMechanicWidget):

    def as_setActiveProgressS(self, progress):
        return self.flashObject.as_setActiveProgress(progress) if self._isDAAPIInited() else None

    def as_setPreparingProgressS(self, progress):
        return self.flashObject.as_setPreparingProgress(progress) if self._isDAAPIInited() else None

    def as_shootDoneS(self):
        return self.flashObject.as_shootDone() if self._isDAAPIInited() else None
