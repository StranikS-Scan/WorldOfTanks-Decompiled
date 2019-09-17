# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inhangar/__init__.py
import constants
import nations
from account_helpers.AccountSettings import AccountSettings
from account_helpers.AccountSettings import STORAGE_VEHICLES_CAROUSEL_FILTER_1
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_data_provider import CarouselDataProvider
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import SessionCarouselFilter, EventCriteriesGroup, CriteriesGroup
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getStorageVehicleVo, isStorageSessionTimeout
from gui.prb_control.settings import VEHICLE_LEVELS
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES
from gui.shared.utils import makeSearchableString
from gui.shared.utils.requesters import REQ_CRITERIA

class _ShortNameVehiclesCriteriesGroup(CriteriesGroup):

    @staticmethod
    def isApplicableFor(vehicle):
        return True

    def update(self, filters):
        super(_ShortNameVehiclesCriteriesGroup, self).update(filters)
        selectedNationsIds = []
        for nation, nId in nations.INDICES.iteritems():
            if filters[nation]:
                selectedNationsIds.append(nId)

        if selectedNationsIds:
            self._criteria |= REQ_CRITERIA.NATIONS(selectedNationsIds)
        selectedVehiclesIds = []
        for vehicleType, _ in constants.VEHICLE_CLASS_INDICES.iteritems():
            if filters[vehicleType]:
                selectedVehiclesIds.append(vehicleType)

        if selectedVehiclesIds:
            self._criteria |= REQ_CRITERIA.VEHICLE.CLASSES(selectedVehiclesIds)
        selectedLevels = []
        for level in VEHICLE_LEVELS:
            if filters['level_%d' % level]:
                selectedLevels.append(level)

        if selectedLevels:
            self._criteria |= REQ_CRITERIA.VEHICLE.LEVELS(selectedLevels)
        if filters['elite'] and not filters['premium']:
            self._criteria |= REQ_CRITERIA.VEHICLE.ELITE | ~REQ_CRITERIA.VEHICLE.PREMIUM
        elif filters['elite'] and filters['premium']:
            self._criteria |= REQ_CRITERIA.VEHICLE.ELITE
        elif filters['premium']:
            self._criteria |= REQ_CRITERIA.VEHICLE.PREMIUM
        if filters['igr'] and constants.IS_KOREA:
            self._criteria |= REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR
        if not filters['rented']:
            self._criteria |= ~REQ_CRITERIA.VEHICLE.RENT
        if filters['bonus']:
            self._criteria |= REQ_CRITERIA.VEHICLE.HAS_XP_FACTOR
        if filters['favorite']:
            self._criteria |= REQ_CRITERIA.VEHICLE.FAVORITE
        if filters['searchNameVehicle']:
            searchableString = makeSearchableString(filters['searchNameVehicle'])
            self._criteria |= REQ_CRITERIA.VEHICLE.NAME_VEHICLE_WITH_SHORT(searchableString)


class StorageCarouselFilter(SessionCarouselFilter):

    def __init__(self, criteries=None):
        super(StorageCarouselFilter, self).__init__()
        self._clientSections = (STORAGE_VEHICLES_CAROUSEL_FILTER_1,)
        self._criteriesGroups = (criteries or tuple()) + (EventCriteriesGroup(), _ShortNameVehiclesCriteriesGroup())

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

    def __init__(self, carouselFilter, itemsCache, currentVehicle):
        super(StorageCarouselDataProvider, self).__init__(carouselFilter, itemsCache, currentVehicle)
        self._baseCriteria = REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.RENT

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
