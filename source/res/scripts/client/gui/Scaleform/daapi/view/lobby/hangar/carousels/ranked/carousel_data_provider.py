# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/ranked/carousel_data_provider.py
from gui.impl.gen import R
from gui.impl import backport
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TYPES_ORDER_INDICES
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedCarouselDataProvider(HangarCarouselDataProvider):
    rankedController = dependency.descriptor(IRankedBattlesController)

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (cls._isSuitableForQueue(vehicle),
         not vehicle.isInInventory,
         not vehicle.isEvent,
         not vehicle.isFavorite,
         not cls.rankedController.hasVehicleRankedBonus(vehicle.intCD),
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)

    def _buildVehicle(self, vehicle):
        result = super(RankedCarouselDataProvider, self)._buildVehicle(vehicle)
        state, _ = vehicle.getState()
        result['hasRankedBonus'] = self.rankedController.hasVehicleRankedBonus(vehicle.intCD)
        if state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE:
            result['lockedTooltip'] = makeTooltip(backport.text(R.strings.ranked_battles.rankedBattlesCarousel.lockedTooltip.header()), backport.text(R.strings.ranked_battles.rankedBattlesCarousel.lockedTooltip.body()))
            result['clickEnabled'] = True
            result['hasRankedBonus'] = False
        return result
