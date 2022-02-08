# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/style_buying_preview.py
import typing
from gui.Scaleform.daapi.view.lobby.vehicle_preview.style_preview import VehicleStylePreview
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
if typing.TYPE_CHECKING:
    from typing import Dict
    from gui.shared.gui_items.customization.c11n_items import Style

class VehicleStyleBuyingPreview(VehicleStylePreview):

    def __init__(self, ctx=None):
        super(VehicleStyleBuyingPreview, self).__init__(ctx)
        self.__style = ctx.get('style')
        self.__price = ctx.get('price')
        self.__level = ctx.get('styleLevel')
        self.__buyParams = ctx.get('buyParams')

    def setBottomPanel(self, linkage=None):
        self.as_setBottomPanelS(linkage)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(VehicleStyleBuyingPreview, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_STYLE_BUYING_PY_ALIAS:
            viewPy.setStyleInfo(self.__style, self.__price, self.__level)
            viewPy.setBuyParams(self.__buyParams)

    def _populate(self):
        self.setBottomPanel(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_STYLE_BUYING_LINKAGE)
        super(VehicleStyleBuyingPreview, self)._populate()
