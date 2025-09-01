# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ChargeShotWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class ChargeShotWidgetMeta(VehicleMechanicWidget):

    def as_setUpdateProgressS(self, stack, progressValue):
        return self.flashObject.as_setUpdateProgress(stack, progressValue) if self._isDAAPIInited() else None

    def as_setShootBlockS(self, value):
        return self.flashObject.as_setShootBlock(value) if self._isDAAPIInited() else None

    def as_setDamageS(self, value):
        return self.flashObject.as_setDamage(value) if self._isDAAPIInited() else None

    def as_showShootBlockAnimationS(self):
        return self.flashObject.as_showShootBlockAnimation() if self._isDAAPIInited() else None
