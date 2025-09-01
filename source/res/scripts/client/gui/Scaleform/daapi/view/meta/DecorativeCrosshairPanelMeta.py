# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DecorativeCrosshairPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.panels_common import VehicleMechanicsPanel

class DecorativeCrosshairPanelMeta(VehicleMechanicsPanel):

    def as_addDecorCrosshairS(self, type):
        return self.flashObject.as_addDecorCrosshair(type) if self._isDAAPIInited() else None

    def as_setVisibleS(self, value):
        return self.flashObject.as_setVisible(value) if self._isDAAPIInited() else None

    def as_updateLayoutS(self, x, y):
        return self.flashObject.as_updateLayout(x, y) if self._isDAAPIInited() else None

    def as_updateCrosshairTypeS(self, type):
        return self.flashObject.as_updateCrosshairType(type) if self._isDAAPIInited() else None
