# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/royale/carousel_data_provider.py
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TYPES_ORDER_INDICES
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters import REQ_CRITERIA

class RoyaleCarouselDataProvider(HangarCarouselDataProvider):

    def __init__(self, carouselFilter, itemsCache, currentVehicle):
        super(RoyaleCarouselDataProvider, self).__init__(carouselFilter, itemsCache, currentVehicle)
        self._criteriaForHiddenVehicles = ()

    def _setBaseCriteria(self):
        self._baseCriteria = REQ_CRITERIA.INVENTORY

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (vehicle.getCustomState() == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE,
         not vehicle.isInInventory,
         not vehicle.isEvent,
         not vehicle.isOnlyForBattleRoyaleBattles,
         not vehicle.isFavorite,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)

    def _buildVehicle(self, vehicle):
        result = super(RoyaleCarouselDataProvider, self)._buildVehicle(vehicle)
        state, _ = vehicle.getState()
        if state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE:
            result['lockedTooltip'] = makeTooltip(backport.text(R.strings.battle_royale.battleRoyaleCarousel.lockedToolTip.header()), backport.text(R.strings.battle_royale.battleRoyaleCarousel.lockedToolTip.body()))
            result['clickEnabled'] = True
        return result
