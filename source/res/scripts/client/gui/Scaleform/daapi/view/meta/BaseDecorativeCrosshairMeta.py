# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BaseDecorativeCrosshairMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.components_common import VehicleMechanicDAAPIComponent

class BaseDecorativeCrosshairMeta(VehicleMechanicDAAPIComponent):

    def as_setStateS(self, state, isInstantly=False):
        return self.flashObject.as_setState(state, isInstantly) if self._isDAAPIInited() else None

    def as_setVisibleS(self, value):
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None
