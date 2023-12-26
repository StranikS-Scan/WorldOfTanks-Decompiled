# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/showcase_style_buying_preview.py
import typing
from CurrentVehicle import g_currentPreviewVehicle
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.lobby.vehicle_preview.style_preview import VehicleStylePreview
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Optional
    from gui.shared.gui_items.customization.c11n_items import Style

class VehicleShowcaseStyleBuyingPreview(VehicleStylePreview):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(VehicleShowcaseStyleBuyingPreview, self).__init__(ctx)
        self.__style = ctx.get('style')
        self.__price = ctx.get('price')
        self.__originalPrice = ctx.get('originalPrice')
        self.__discountPercent = ctx.get('discountPercent')
        self.__endTime = ctx.get('endTime')
        self.__buyParams = ctx.get('buyParams')
        self.__obtainingMethod = ctx.get('obtainingMethod')

    def setBottomPanel(self, linkage=None):
        self.as_setBottomPanelS(linkage)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(VehicleShowcaseStyleBuyingPreview, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_SHOWCASE_STYLE_BUYING_PY_ALIAS:
            viewPy.setData(self.__style, self.__price, self.__endTime, self.__originalPrice, self.__buyParams, self.__discountPercent, self.__obtainingMethod)
            viewPy.update()

    def _populate(self):
        self.setBottomPanel(VEHPREVIEW_CONSTANTS.BOTTOM_PANEL_SHOWCASE_STYLE_BUYING_LINKAGE)
        super(VehicleShowcaseStyleBuyingPreview, self)._populate()

    def _getAdditionalInfoVO(self):
        vpAdditionalInfoVO = super(VehicleShowcaseStyleBuyingPreview, self)._getAdditionalInfoVO()
        if self._styleIsUnique():
            vpAdditionalInfoVO['vehicleInfoDesc'] = self.__getVehicleInfoDescVO()
        return vpAdditionalInfoVO

    def _styleIsUnique(self):
        suitableVehicles = self.__itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.FOR_ITEM(self.__style))
        return len(suitableVehicles) == 1

    @staticmethod
    def __getVehicleInfoDescVO():
        vehicle = g_currentPreviewVehicle.item
        vehicleType = '{}_elite'.format(vehicle.type) if vehicle.isElite or vehicle.isPremium else vehicle.type
        return {'nationFlag': backport.image(R.images.gui.maps.icons.filters.nations.dyn(vehicle.nationName)()),
         'level': backport.text(R.strings.menu.header.level.num(vehicle.level)()),
         'typeImageSrc': backport.image(R.images.gui.maps.icons.filters.tanks.dyn(vehicleType.replace('-', '_'))()),
         'isElite': vehicle.isElite or vehicle.isPremium,
         'name': vehicle.descriptor.type.shortUserString}
