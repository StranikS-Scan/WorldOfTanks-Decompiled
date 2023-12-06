# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/ranked/carousel_data_provider.py
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass.carousel_data_provider import BattlePassCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.carousel_helpers import getUnsuitable2queueTooltip
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TYPES_ORDER_INDICES
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedCarouselDataProvider(BattlePassCarouselDataProvider):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    @staticmethod
    def _isSuitableForQueue(vehicle):
        return True

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (not cls._isSuitableForQueue(vehicle),
         not vehicle.isInInventory,
         not vehicle.isEvent,
         not vehicle.isOnlyForBattleRoyaleBattles,
         not vehicle.isFavorite,
         not cls.__rankedController.hasVehicleRankedBonus(vehicle.intCD),
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)

    def _getBeforeAdditionalItemsIndexes(self):
        return []

    def _buildVehicle(self, vehicle):
        result = super(RankedCarouselDataProvider, self)._buildVehicle(vehicle)
        labelStyle = text_styles.premiumVehicleName if vehicle.isPremium else text_styles.vehicleName
        result['hasRankedBonus'] = self.__rankedController.hasVehicleRankedBonus(vehicle.intCD)
        result['label'] = labelStyle(vehicle.shortUserName if vehicle.isPremiumIGR else vehicle.userName)
        state, _ = vehicle.getState()
        suitResult = self.__rankedController.isSuitableVehicle(vehicle)
        resShortCut = R.strings.ranked_battles.rankedBattlesCarousel.lockedTooltip
        if suitResult is not None:
            if state == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE:
                result['lockedTooltip'] = getUnsuitable2queueTooltip(suitResult, resShortCut)
            result['clickEnabled'] = True
            result['hasRankedBonus'] = False
        return result
