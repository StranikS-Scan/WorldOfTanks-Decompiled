# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WidgetsPanelMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.panels_common import VehicleMechanicsPanel

class WidgetsPanelMeta(VehicleMechanicsPanel):

    def as_addWidgetS(self, widgetType):
        return self.flashObject.as_addWidget(widgetType) if self._isDAAPIInited() else None

    def as_updateLayoutS(self, x, y):
        return self.flashObject.as_updateLayout(x, y) if self._isDAAPIInited() else None

    def as_updateCrosshairTypeS(self, crosshairType):
        return self.flashObject.as_updateCrosshairType(crosshairType) if self._isDAAPIInited() else None

    def as_setVisibleS(self, visible):
        return self.flashObject.as_setVisible(visible) if self._isDAAPIInited() else None

    def as_isPlayerS(self, value):
        return self.flashObject.as_isPlayer(value) if self._isDAAPIInited() else None

    def as_isReplayS(self, value):
        return self.flashObject.as_isReplay(value) if self._isDAAPIInited() else None
