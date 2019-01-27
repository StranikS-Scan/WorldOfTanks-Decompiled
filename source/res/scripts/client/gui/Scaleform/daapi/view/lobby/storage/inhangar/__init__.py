# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inhangar/__init__.py
from account_helpers.AccountSettings import AccountSettings
from account_helpers.AccountSettings import STORAGE_VEHICLES_CAROUSEL_FILTER_1
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import CarouselDataProvider
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import SessionCarouselFilter
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getStorageVehicleVo, isStorageSessionTimeout
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES

class StorageCarouselFilter(SessionCarouselFilter):

    def __init__(self, criteries=None):
        super(StorageCarouselFilter, self).__init__()
        self._clientSections = (STORAGE_VEHICLES_CAROUSEL_FILTER_1,)
        self._criteriesGroups = (criteries or tuple()) + self._criteriesGroups

    def load(self):
        if isStorageSessionTimeout():
            defaultFilters = dict()
            for section in self._clientSections:
                defaultFilters.update(AccountSettings.getSessionSettingsDefault(section))

            self._filters = defaultFilters
            self.update(defaultFilters, save=False)
        else:
            super(StorageCarouselFilter, self).load()


class StorageCarouselDataProvider(CarouselDataProvider):

    def _buildVehicle(self, item):
        return getStorageVehicleVo(item)

    def _getVehicleStats(self, vehicle):
        return {}

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        return (not vehicle.isInInventory,
         not vehicle.isEvent,
         GUI_NATIONS_ORDER_INDEX[vehicle.nationName],
         VEHICLE_TYPES_ORDER_INDICES[vehicle.type],
         vehicle.level,
         tuple(vehicle.buyPrices.itemPrice.price.iterallitems(byWeight=True)),
         vehicle.userName)
