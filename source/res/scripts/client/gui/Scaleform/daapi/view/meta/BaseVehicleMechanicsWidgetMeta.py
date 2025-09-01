# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseVehicleMechanicsWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.components_common import VehicleMechanicDAAPIComponent

class BaseVehicleMechanicsWidgetMeta(VehicleMechanicDAAPIComponent):

    def as_setStateS(self, state, isInstantly=False):
        return self.flashObject.as_setState(state, isInstantly) if self._isDAAPIInited() else None

    def as_setHotKeysS(self, keyCodes):
        return self.flashObject.as_setHotKeys(keyCodes) if self._isDAAPIInited() else None

    def as_setVisibleS(self, visible):
        return self.flashObject.as_setVisible(visible) if self._isDAAPIInited() else None

    def as_setCrosshairTypeS(self, value):
        return self.flashObject.as_setCrosshairType(value) if self._isDAAPIInited() else None

    def as_setTimeS(self, time):
        return self.flashObject.as_setTime(time) if self._isDAAPIInited() else None
