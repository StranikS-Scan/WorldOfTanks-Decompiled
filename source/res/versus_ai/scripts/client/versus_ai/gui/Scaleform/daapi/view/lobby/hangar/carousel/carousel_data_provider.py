# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/gui/Scaleform/daapi/view/lobby/hangar/carousel/carousel_data_provider.py
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass.carousel_data_provider import BattlePassCarouselDataProvider
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES

class VersusAICarouselDataProvider(BattlePassCarouselDataProvider):

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (cls._isSuitableForQueue(vehicle),
         not vehicle.isInInventory,
         not vehicle.isEvent,
         not vehicle.isOnlyForBattleRoyaleBattles,
         not vehicle.isFavorite,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)

    def _getVehicleStats(self, _):
        return {}
