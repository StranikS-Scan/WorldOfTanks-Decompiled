# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_carousel/carousel_filter.py
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
    """ Filter dict leaving only acceptable keys.
    
    :param dictionary: dictionary to be filtered
    :param keys: list of acceptable keys
    :return a new dict with only acceptable keys
    """
    return {key:value for key, value in dictionary.iteritems() if key in keys}


class _CarouselFilter(object):
    """ Base class for tank carousel filters.
    """

    def __init__(self):
        self._filters = {}
        self._serverSections = ()
        self._clientSections = ()
        self._criteriesGroups = ()

    def apply(self, vehicle):
        """ Apply filter to the vehicle.
        
        :return an instance of RequestCriteria.
        """
        for group in self._criteriesGroups:
            if group.isApplicableFor(vehicle):
                return group.apply(vehicle)

    def getFilters(self, keys=None):
        """ Get filters and their params.
        
        :param keys: if specified, gathers only filters listed in this parameter.
        :return a dict.
        """
        if keys is not None:
            filters = _filterDict(self._filters, keys)
        else:
            filters = self._filters.copy()
        return filters

    def get(self, key):
        """ Get value of single filter.
        
        :param key: filter name
        :return: bool, filter's value
        """
        return self._filters[key]

    def isDefault(self, keys=None):
        """ Check whether filters are in default state or not.
        
        :param keys: if specified, check only the filters listed in this parameter.
        :return: True if filters are in default state, False otherwise.
        """
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
        """ Reset filters to their default state.
        
        :param keys: if specified, resets only the filters listed in this parameter.
        :param exceptions: if specified, excludes given filters from reseting.
        :param save: flag that determines whether filters should be saved immediately.
        """
        defaultFilters = AccountSettings.getFilterDefaults(self._serverSections)
        for section in self._clientSections:
            defaultFilters.update(AccountSettings.getFilterDefault(section))

        keys = keys or defaultFilters.keys()
        exceptions = exceptions or []
        keys = [ key for key in keys if key not in exceptions ]
        defaultFilters = _filterDict(defaultFilters, keys)
        self.update(defaultFilters, save)

    def switch(self, key, save=True):
        """ Switch the state of boolean filter (True -> False).
        
        :param key: key of the filter.
        :param save: flag that determines whether filters should be saved immediately.
        """
        self.update({key: not self._filters[key]}, save)

    def update(self, params, save=True):
        """ Update values of the specified filters.
        
        :param params: dict containing new parameters of filters.
        :param save: flag that determines whether filters should be saved immediately.
        """
        for key, value in params.iteritems():
            assert key in self._filters
            self._filters[key] = value

        for group in self._criteriesGroups:
            group.update(self._filters)

        if save:
            self.save()

    def save(self):
        """ Save filters to server.
        """
        raise NotImplementedError

    def load(self):
        """ Load filters from server.
        """
        raise NotImplementedError


class CriteriesGroup(object):
    """ There are types of vehicles that have unique filtering rules, these filtering
    rules for group of vehicles are represented as this class.
    """

    def __init__(self):
        self._criteria = None
        return

    def apply(self, vehicle):
        """ Check if vehicle satisfies this group's criteria.
        
        :param vehicle: instance of gui_items.Vehicle
        :return: True if vehicle satisfies criteria, False otherwise.
        """
        return self._criteria(vehicle)

    def update(self, filters):
        """ Reconstruct criteria in order to keep it up to date.
        
        :param filters: dict containing filters ({filter_name: flag})
        """
        self._criteria = REQ_CRITERIA.EMPTY

    @staticmethod
    def isApplicableFor(vehicle):
        """ Check if this group is applicable for the vehicle.
        
        :param vehicle: instance of gui_items.Vehicle
        :return: True if group is applicable for vehicle, False otherwise.
        """
        raise NotImplementedError


class CarouselFilter(_CarouselFilter):
    """ Class represents facility for filtering carousel vehicles
    """
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
    """ This is a group of last resort that should be applied for the regular vehicles.
    """

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
        for vehicleType, vId in constants.VEHICLE_CLASS_INDICES.iteritems():
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
    """ This group is especially for event vehicles.
    """

    def update(self, filters):
        super(EventCriteriesGroup, self).update(filters)
        if not filters['event']:
            self._criteria |= ~REQ_CRITERIA.VEHICLE.EVENT

    @staticmethod
    def isApplicableFor(vehicle):
        return vehicle.isEvent
