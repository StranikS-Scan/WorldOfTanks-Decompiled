# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/lobby/hangar/carousel/data_provider.py
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES, Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA

class WhiteTigerCarouselDataProvider(HangarCarouselDataProvider):

    def getVehiclesIntCDs(self):
        vehicledIntCDs = []
        for vehicle in self._vehicles:
            vehicledIntCDs.append(vehicle.intCD)

        return vehicledIntCDs

    def _getAdditionalItemsIndexes(self):
        return []

    def _setBaseCriteria(self):
        self._baseCriteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EVENT_BATTLE

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (vehicle.getCustomState() == Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE,
         not vehicle.isInInventory,
         not vehicle.isEvent,
         not vehicle.isOnlyForEventBattles,
         not vehicle.isFavorite,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)

    def _isTelecomRentalsEnabled(self):
        return False
