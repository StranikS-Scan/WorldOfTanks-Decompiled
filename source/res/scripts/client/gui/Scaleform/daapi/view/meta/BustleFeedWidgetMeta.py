# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BustleFeedWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class BustleFeedWidgetMeta(VehicleMechanicWidget):

    def as_setProgressS(self, progress, time):
        return self.flashObject.as_setProgress(progress, time) if self._isDAAPIInited() else None

    def as_setLockS(self, isLocked):
        return self.flashObject.as_setLock(isLocked) if self._isDAAPIInited() else None

    def as_setAvailabilityS(self, isDisable):
        return self.flashObject.as_setAvailability(isDisable) if self._isDAAPIInited() else None

    def as_setCommandS(self, command):
        return self.flashObject.as_setCommand(command) if self._isDAAPIInited() else None
