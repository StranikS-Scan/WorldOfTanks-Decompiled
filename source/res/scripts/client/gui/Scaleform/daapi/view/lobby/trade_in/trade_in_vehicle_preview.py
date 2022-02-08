# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trade_in/trade_in_vehicle_preview.py
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS

class TradeInVehiclePreview(VehiclePreview):

    def setBottomPanel(self):
        self.as_setBottomPanelS(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_TRADE_IN_LINKAGE)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(TradeInVehiclePreview, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_TRADE_IN_PY_ALIAS:
            viewPy.setBackAlias(self._backAlias)
            viewPy.setBackCallback(self._previewBackCb)
