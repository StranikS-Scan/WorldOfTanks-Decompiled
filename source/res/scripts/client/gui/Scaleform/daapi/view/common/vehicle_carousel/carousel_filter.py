# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/vehicle_carousel/carousel_filter.py
import constants
import nations
from account_helpers.AccountSettings import AccountSettings, CAROUSEL_FILTER_1, CAROUSEL_FILTER_2
from account_helpers.AccountSettings import CAROUSEL_FILTER_CLIENT_1
from gui.prb_control.settings import VEHICLE_LEVELS
from gui.shared.utils import makeSearchableString
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

def _filterDict(dictionary, keys):
    return {key:value for key, value in dictionary.iteritems() if key in keys}


class _CarouselFilter(object):

    def __init__(self):
        self._filters = {}
        self._serverSections = ()
        self._clientSections = ()
        self._criteriesGroups = ()

    @property
    def criteria(self):
        criteria = REQ_CRITERIA.EMPTY
        for group in self._criteriesGroups:
            criteria |= group.criteria

        return criteria

    def apply(self, vehicle):
        for group in self._criteriesGroups:
            if group.isApplicableFor(vehicle):
                return group.apply(vehicle)

    def getFilters(self, keys=None):
        if keys is not None:
            filters = _filterDict(self._filters, keys)
        else:
            filters = self._filters.copy()
        return filters

    def get(self, key):
        return self._filters[key]

    def isDefault(self, keys=None):
        defaultFilters = AccountSettings.getFilterDefaults(self._serverSections)
        for section in self._clientSections:
            defaultFilters.update(AccountSettings.getFilterDefault(section))

        if keys is None:
            keys = defaultFilters.keys()
        for key in keys:
            if self._filters[key] != defaultFilters[key]:
                return False

        return True

    def reset(self, keys=None, exceptions=None, save=True):
        defaultFilters = AccountSettings.getFilterDefaults(self._serverSections)
        for section in self._clientSections:
            defaultFilters.update(AccountSettings.getFilterDefault(section))

        keys = keys or defaultFilters.keys()
        exceptions = exceptions or []
        keys = [ key for key in keys if key not in exceptions ]
        defaultFilters = _filterDict(defaultFilters, keys)
        self.update(defaultFilters, save)

    def switch(self, key, save=True):
        self.update({key: not self._filters[key]}, save)

    def update(self, params, save=True):
        for key, value in params.iteritems():
            self._filters[key] = value

        for group in self._criteriesGroups:
            group.update(self._filters)

        if save:
            self.save()

    def save(self):
        raise NotImplementedError

    def load(self):
        raise NotImplementedError


class CriteriesGroup(object):

    def __init__(self):
        self._criteria = None
        return

    @property
    def criteria(self):
        return self._criteria

    def apply(self, vehicle):
        return self._criteria(vehicle)

    def update(self, filters):
        self._criteria = REQ_CRITERIA.EMPTY

    @staticmethod
    def isApplicableFor(vehicle):
        raise NotImplementedError


class CarouselFilter(_CarouselFilter):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(CarouselFilter, self).__init__()
        self._serverSections = (CAROUSEL_FILTER_1, CAROUSEL_FILTER_2)
        self._clientSections = (CAROUSEL_FILTER_CLIENT_1,)
        self._criteriesGroups = (EventCriteriesGroup(), BasicCriteriesGroup())

    def save(self):
        self.settingsCore.serverSettings.setSections(self._serverSections, self._filters)
        for section in self._clientSections:
            AccountSettings.setFilter(section, self._filters)

    def load(self):
        defaultFilters = AccountSettings.getFilterDefaults(self._serverSections)
        savedFilters = self.settingsCore.serverSettings.getSections(self._serverSections, defaultFilters)
        for section in self._clientSections:
            defaultFilters.update(AccountSettings.getFilterDefault(section))
            savedFilters.update(AccountSettings.getFilter(section))

        self._filters = defaultFilters
        for key, value in defaultFilters.iteritems():
            savedFilters[key] = type(value)(savedFilters[key])

        self.update(savedFilters, save=False)


class BasicCriteriesGroup(CriteriesGroup):

    @staticmethod
    def isApplicableFor(vehicle):
        return True

    def update(self, filters):
        super(BasicCriteriesGroup, self).update(filters)
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
            self._criteria |= REQ_CRITERIA.VEHICLE.NAME_VEHICLE(makeSearchableString(filters['searchNameVehicle']))


class EventCriteriesGroup(CriteriesGroup):

    def update(self, filters):
        super(EventCriteriesGroup, self).update(filters)
        if not filters['event']:
            self._criteria |= ~REQ_CRITERIA.VEHICLE.EVENT

    @staticmethod
    def isApplicableFor(vehicle):
        return vehicle.isEvent
