# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/filter/data_providers.py
import operator
import random
from collections import OrderedDict, namedtuple
from typing import Optional
import nations
from Event import Event
from constants import MAX_VEHICLE_LEVEL
from gui import GUI_NATIONS_ORDER_INDICES, GUI_NATIONS_ORDER_INDEX
from gui.impl.gen.view_models.views.lobby.crew.common.filter_toggle_group_model import ToggleGroupType
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanLocation
from gui.impl.lobby.crew.crew_helpers.sort_helpers import SortHeap
from gui.impl.lobby.crew.filter import VEHICLE_LOCATION_IN_HANGAR, GRADE_PREMIUM, GRADE_ELITE, GRADE_PRIMARY
from gui.impl.lobby.crew.utils import getDocGroupValues, getSecretWithoutRentCriteria, getPremiumWithoutRentCriteria
from gui.server_events import recruit_helper
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import Tankman, getFullUserName
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES, VEHICLE_TAGS, checkForTags
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
from helpers import dependency
from items import tankmen
from skeletons.gui.shared import IItemsCache

class FilterableItemsDataProvider(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, state):
        self.onDataChanged = Event()
        self._state = state
        self.__initialItemsCount = None
        self.__itemsCount = None
        self.__vehSortHeap = None
        self.__items = None
        return

    def __getitem__(self, item):
        return self.items()[item]

    def clear(self):
        self.__initialItemsCount = None
        self.__itemsCount = None
        self.__vehSortHeap = None
        self.__items = None
        self.onDataChanged.clear()
        return

    def items(self):
        if self.__items is None:
            self.__items = self.__vehSortHeap.getSortedList() if self.__vehSortHeap else []
        return self.__items

    @property
    def initialItemsCount(self):
        if self.__initialItemsCount is None:
            self.__initialItemsCount = len(self._getInitialItems())
        return self.__initialItemsCount

    @property
    def itemsCount(self):
        if self.__itemsCount is None:
            self.__itemsCount = len(self.items())
        return self.__itemsCount

    def reinit(self):
        self.__items = None
        self.__itemsCount = None
        self.__initialItemsCount = None
        return

    def update(self):
        filteredItems = self._getFilteredItems()
        self._sort(filteredItems)
        self.__items = None
        self.__itemsCount = None
        self.onDataChanged()
        return

    def updateRoot(self, item):
        if self.__vehSortHeap:
            self.__vehSortHeap.updateRoot(item=item, keys=self._getSortKeyCriteria(), criteria=self._getConditionSortCriteria())

    def _getInitialFilterCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _getFilterCriteria(self):
        criteria = self._getInitialFilterCriteria()
        for extraCriteria in self._getFiltersList():
            if extraCriteria:
                criteria |= extraCriteria

        return criteria

    def _getSortCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _getInitialItems(self):
        criteria = self._getInitialFilterCriteria()
        return self._itemsGetter(criteria, initial=True)

    def _getFilteredItems(self):
        criteria = self._getFilterCriteria()
        return self._itemsGetter(criteria)

    def _getFiltersList(self):
        raise NotImplementedError

    def _sort(self, filteredItems):
        self.__vehSortHeap = SortHeap(items=filteredItems.values() if hasattr(filteredItems, 'values') else filteredItems, keys=self._getSortKeyCriteria(), criteria=self._getConditionSortCriteria())

    def _getSortKeyCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _getConditionSortCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _itemsGetter(self, criteria, initial=False):
        raise NotImplementedError


class CompoundDataProvider(object):

    def __init__(self, **dataProviders):
        self.onDataChanged = Event()
        msg = 'All data providers must be derived from FilterableItemsDataProvider'
        self.__dataProviders = dataProviders
        self.__updatingCount = 0

    def __getitem__(self, item):
        return self.__dataProviders[item]

    def __len__(self):
        return len(self.__dataProviders)

    def clear(self):
        for dataProvider in self.__dataProviders.itervalues():
            dataProvider.clear()

        self.__dataProviders = None
        self.onDataChanged.clear()
        return

    def reinit(self, *args, **kwargs):
        for dataProvider in self.__dataProviders.itervalues():
            dataProvider.reinit(*args, **kwargs)

    def update(self):
        self.__updatingCount += len(self)
        for dataProvider in self.__dataProviders.itervalues():
            dataProvider.update()

    def subscribe(self):
        for dataProvider in self.__dataProviders.itervalues():
            dataProvider.onDataChanged += self._onProviderDataChanged

    def unsubscribe(self):
        for dataProvider in self.__dataProviders.itervalues():
            dataProvider.onDataChanged -= self._onProviderDataChanged

    @property
    def itemsCount(self):
        return sum((provider.itemsCount for provider in self.__dataProviders.itervalues()))

    @property
    def initialItemsCount(self):
        return sum((provider.initialItemsCount for provider in self.__dataProviders.itervalues()))

    def _onProviderDataChanged(self):
        self.__updatingCount -= 1
        if self.__updatingCount == 0:
            self.onDataChanged()


class VehiclesDataProvider(FilterableItemsDataProvider):

    def __init__(self, state, tankman=None, vehicle=None):
        self.__tankman = tankman
        self.__vehicle = vehicle
        super(VehiclesDataProvider, self).__init__(state)

    def clear(self):
        self.__tankman = None
        self.__vehicle = None
        super(VehiclesDataProvider, self).clear()
        return

    def items(self):
        items = super(VehiclesDataProvider, self).items()
        if items and self.__vehicle and self.__vehicle not in items:
            items = [self.__vehicle] + items
        return items

    @property
    def tankman(self):
        return self.__tankman

    @property
    def vehicle(self):
        return self.__vehicle

    def reinit(self, tankman=None, vehicle=None):
        self.__tankman = tankman
        self.__vehicle = vehicle
        super(VehiclesDataProvider, self).reinit()

    def updateRoot(self, vehicle):
        self.__vehicle = vehicle
        super(VehiclesDataProvider, self).updateRoot(vehicle)

    def _getFiltersList(self):
        return [self._getFilterByVehicleTypeCriteria(),
         self._getFilterByVehicleTierCriteria(),
         self._getFilterByVehicleGradeCriteria(),
         self._getFilterByVehicleLocationCriteria(),
         self._getSearchCriteria()]

    def _getInitialFilterCriteria(self):
        criteria = REQ_CRITERIA.EMPTY
        criteria |= ~REQ_CRITERIA.VEHICLE.IS_CREW_LOCKED
        criteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
        criteria |= ~getSecretWithoutRentCriteria()
        criteria |= ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN
        criteria |= REQ_CRITERIA.VEHICLE.ACTIVE_OR_MAIN_IN_NATION_GROUP
        if self.tankman:
            criteria |= REQ_CRITERIA.VEHICLE.HAS_ROLE(self.tankman.descriptor.role)
            criteria |= REQ_CRITERIA.NATIONS([self.tankman.nationID])
        return criteria

    def _getFilterByVehicleTypeCriteria(self):
        vehicleTypes = self._state[ToggleGroupType.VEHICLETYPE.value]
        return REQ_CRITERIA.VEHICLE.CLASSES(tuple(vehicleTypes)) if vehicleTypes else None

    def _getFilterByVehicleTierCriteria(self):
        vehicleTiers = self._state[ToggleGroupType.VEHICLETIER.value]
        vehicleTiers = {int(t) for t in vehicleTiers}
        return REQ_CRITERIA.VEHICLE.LEVELS(vehicleTiers) if vehicleTiers else None

    def _getFilterByVehicleGradeCriteria(self):
        vehicleGrades = self._state[ToggleGroupType.VEHICLEGRADE.value]
        criteria = getPremiumWithoutRentCriteria()
        return criteria if GRADE_PREMIUM in vehicleGrades else ~criteria

    def _getFilterByVehicleLocationCriteria(self):
        vehicleLocations = self._state[ToggleGroupType.LOCATION.value]
        return REQ_CRITERIA.INVENTORY if VEHICLE_LOCATION_IN_HANGAR in vehicleLocations else None

    def _getSearchCriteria(self):
        return REQ_CRITERIA.VEHICLE.NAME_VEHICLE_WITH_SHORT(self._state.searchString.lower()) if self._state.searchString else None

    def _getSortKeyCriteria(self):
        criteria = REQ_CRITERIA.CUSTOM(lambda item: VEHICLE_TYPES_ORDER_INDICES[item.type])
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: MAX_VEHICLE_LEVEL - item.level)
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: item.searchableUserName)
        return criteria

    def _getConditionSortCriteria(self):
        criteria = REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD((self.vehicle.compactDescr,))
        criteria |= REQ_CRITERIA.INVENTORY
        criteria |= ~REQ_CRITERIA.INVENTORY
        return criteria

    def _itemsGetter(self, criteria, initial=False):
        return self.itemsCache.items.getVehicles(criteria)


class TankmenDataProvider(FilterableItemsDataProvider):

    def __init__(self, state):
        super(TankmenDataProvider, self).__init__(state)
        self.__inventoryTankmen = None
        self.__dismissedTankmen = None
        return

    def dissmissed(self):
        items = self._getDismissedTankmen()
        return self.__applyFilters(items)

    def clear(self):
        self.__inventoryTankmen = None
        self.__dismissedTankmen = None
        super(TankmenDataProvider, self).clear()
        return

    def regular(self):
        items = self._getInventoryTankmen()
        return self.__applyFilters(items)

    def tankmenInBarracksCount(self):
        return sum((1 for tankman in self._getInventoryTankmen() if not tankman.isInTank))

    def reinit(self):
        super(TankmenDataProvider, self).reinit()
        self.__inventoryTankmen = None
        self.__dismissedTankmen = None
        return

    def _getFiltersList(self):
        return [self._getFilterByVehicleTypeCriteria(),
         self._getFilterByVehicleTierCriteria(),
         self._getFilterByVehicleGradeCriteria(),
         self._getFilterByVehicleCDCriteria(),
         self._getFilterByNationCriteria(),
         self._getFilterByLocationCriteria(),
         self._getFilterByTankmanRoleCriteria(),
         self._getSearchCriteria()]

    def _getInitialFilterCriteria(self):
        return ~REQ_CRITERIA.TANKMAN.VEHICLE_BATTLE_ROYALE | ~REQ_CRITERIA.TANKMAN.VEHICLE_HIDDEN_IN_HANGAR

    def _getFilterByVehicleTypeCriteria(self):
        vehicleTypes = self._state[ToggleGroupType.VEHICLETYPE.value]
        return REQ_CRITERIA.TANKMAN.VEHICLE_NATIVE_TYPES(vehicleTypes) if vehicleTypes else None

    def _getFilterByVehicleTierCriteria(self):
        vehicleTiers = self._state[ToggleGroupType.VEHICLETIER.value]
        vehicleTiers = {int(t) for t in vehicleTiers}
        return REQ_CRITERIA.TANKMAN.VEHICLE_NATIVE_LEVELS(vehicleTiers) if vehicleTiers else None

    def _getFilterByVehicleGradeCriteria(self):
        grades = self._state[ToggleGroupType.VEHICLEGRADE.value]
        if not grades & {GRADE_PREMIUM, GRADE_ELITE, GRADE_PRIMARY}:
            return None
        else:
            criteria = REQ_CRITERIA.NONE
            if GRADE_PREMIUM in grades:
                criteria ^= REQ_CRITERIA.CUSTOM(lambda item: item.vehicleNativeDescr.type.isPremium)
            if GRADE_ELITE in grades:
                criteria ^= REQ_CRITERIA.CUSTOM(lambda item: getattr(item.getVehicle(), 'isElite', False) and not getattr(item.getVehicle(), 'isPremium', False))
            if GRADE_PRIMARY in grades:
                criteria ^= REQ_CRITERIA.CUSTOM(lambda item: getattr(item.getVehicle(), 'isFavorite', False))
            return criteria

    def _getFilterByVehicleCDCriteria(self):
        vehicleCDs = self._state[ToggleGroupType.VEHICLECD.value]
        return REQ_CRITERIA.TANKMAN.NATIVE_TANKS(vehicleCDs) if vehicleCDs else None

    def _getFilterByNationCriteria(self):
        value = self._state[ToggleGroupType.NATION.value]
        return REQ_CRITERIA.TANKMAN.NATION(value) if value else None

    def _getFilterByLocationCriteria(self):
        locations = self._state[ToggleGroupType.VEHICLEGRADE.value]
        if not locations & {TankmanLocation.INBARRACKS.value, TankmanLocation.INTANK.value}:
            return None
        else:
            criteria = REQ_CRITERIA.NONE
            if TankmanLocation.INBARRACKS.value in locations:
                criteria ^= ~REQ_CRITERIA.TANKMAN.IN_TANK
            if TankmanLocation.INTANK.value in locations:
                criteria ^= REQ_CRITERIA.TANKMAN.IN_TANK
            return criteria

    def _getFilterByTankmanRoleCriteria(self):
        roles = self._state[ToggleGroupType.TANKMANROLE.value]
        return REQ_CRITERIA.TANKMAN.ROLES(roles) if roles else None

    def _getSearchCriteria(self):
        return REQ_CRITERIA.TANKMAN.SPECIFIC_BY_NAME_OR_SKIN(self._state.searchString) if self._state.searchString else None

    def _getSortKeyCriteria(self):

        def key(item):
            tdescr = item.descriptor
            return (GUI_NATIONS_ORDER_INDICES[item.nationID],
             -tdescr.totalXP(freeSkillsAsCommon=True),
             Tankman.TANKMEN_ROLES_ORDER[tdescr.role],
             getFullUserName(item.nationID, tdescr.firstNameID, tdescr.lastNameID))

        criteria = REQ_CRITERIA.CUSTOM(key)
        return criteria

    def _getConditionSortCriteria(self):
        criteria = REQ_CRITERIA.TANKMAN.ACTIVE
        criteria |= REQ_CRITERIA.TANKMAN.DISMISSED
        return criteria

    def _itemsGetter(self, criteria, initial=False):
        tankmenKinds = self._state[ToggleGroupType.TANKMANKIND.value]
        if not tankmenKinds or initial:
            tankmenKinds = ['tankman', 'dismissed']
        items = []
        if 'tankman' in tankmenKinds:
            items += self._getInventoryTankmen()
        if 'dismissed' in tankmenKinds:
            items += self._getDismissedTankmen()
        items = filter(criteria, items)
        return items

    def _getInventoryTankmen(self):
        if self.__inventoryTankmen is None:
            self.__inventoryTankmen = self.itemsCache.items.getInventoryTankmen().values()
        return self.__inventoryTankmen

    def _getDismissedTankmen(self):
        if self.__dismissedTankmen is None:
            dismissedTankmen = self.itemsCache.items.getDismissedTankmen().values()
            self.__dismissedTankmen = sorted(dismissedTankmen, key=operator.attrgetter('dismissedAt'), reverse=True)
        return self.__dismissedTankmen

    def __applyFilters(self, items):
        criteria = self._getFilterCriteria()
        return filter(criteria, items)


class RecruitsDataProvider(FilterableItemsDataProvider):

    @property
    def newItemsCount(self):
        return recruit_helper.getNewRecruitsCounter()

    def _getFiltersList(self):
        return [self._getFilterByRoles(),
         self._getFilterByNations(),
         self._getFilterByLocationCriteria(),
         self._getSearchCriteria()]

    def _getFilterByRoles(self):
        roles = self._state[ToggleGroupType.TANKMANROLE.value]
        return REQ_CRITERIA.RECRUIT.ROLES(roles) if roles else None

    def _getFilterByNations(self):
        value = self._state[ToggleGroupType.NATION.value]
        return REQ_CRITERIA.RECRUIT.NATION(value) if value else None

    def _getFilterByLocationCriteria(self):
        locations = self._state[ToggleGroupType.LOCATION.value]
        if not locations or TankmanLocation.INBARRACKS.value in locations:
            return None
        else:
            return REQ_CRITERIA.NONE if {TankmanLocation.INTANK.value, TankmanLocation.DISMISSED.value} & locations else None

    def _getSearchCriteria(self):
        return REQ_CRITERIA.RECRUIT.SPECIFIC_BY_NAME(self._state.searchString) if self._state.searchString else None

    def _getSortKeyCriteria(self):
        rolesOrder = Tankman.TANKMEN_ROLES_ORDER
        nationsOrder = GUI_NATIONS_ORDER_INDICES
        criteria = REQ_CRITERIA.CUSTOM(lambda item: (-len(item.getFreeSkills()), -len(item.getEarnedSkills(multiplyNew=True))))
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: -item.getFreeXP())
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: nationsOrder[item.defaultNation] if len(item.getNations()) == 1 else nations.NONE_INDEX)
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: rolesOrder[item.defaultRole] if len(item.getRoles()) == 1 else len(rolesOrder))
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: item.getFullUserName())
        return criteria

    def _getConditionSortCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _itemsGetter(self, criteria, initial=False):
        tankmenKinds = self._state[ToggleGroupType.TANKMANKIND.value]
        if not tankmenKinds or initial:
            tankmenKinds = ['recruit']
        items = []
        if 'recruit' in tankmenKinds:
            items += recruit_helper.getAllRecruitsInfo(sortByExpireTime=True)
        return filter(criteria, items)


class TankmenChangeDataProvider(TankmenDataProvider):
    __slots__ = ('__tankman', '__vehicle', '__rolesOrder', '__role')

    def __init__(self, state, tankman=None, vehicle=None, role=None):
        self.__tankman = tankman
        self.__vehicle = vehicle
        self.role = role
        super(TankmenChangeDataProvider, self).__init__(state)

    def items(self):
        items = super(TankmenChangeDataProvider, self).items()
        return [self.__tankman] + items if items and self.__tankman else items

    def clear(self):
        self.__tankman = None
        self.__vehicle = None
        self.role = None
        super(TankmenChangeDataProvider, self).clear()
        return

    @property
    def role(self):
        return self.__role

    @role.setter
    def role(self, role):
        self.__role = role
        self.__reorderRoles(role)

    @property
    def tankman(self):
        return self.__tankman

    @property
    def vehicle(self):
        return self.__vehicle

    def reinit(self, tankman=None, role=None):
        self.__tankman = tankman
        self.role = role
        super(TankmenChangeDataProvider, self).reinit()

    def _getInitialFilterCriteria(self):
        criteria = super(TankmenChangeDataProvider, self)._getInitialFilterCriteria()
        criteria |= REQ_CRITERIA.TANKMAN.NATION(nations.NAMES[self.__vehicle.nationID])
        criteria |= ~REQ_CRITERIA.CUSTOM(lambda tankman: checkForTags(self.itemsCache.items.getVehicle(tankman.vehicleInvID).tags, VEHICLE_TAGS.CREW_LOCKED) if tankman.isInTank else False)
        criteria |= REQ_CRITERIA.CUSTOM(lambda tankman: tankmen.tankmenGroupHasRole(tankman.descriptor.nationID, tankman.descriptor.gid, tankman.descriptor.isPremium, self.role))
        return criteria

    def _getFilterByLocationCriteria(self):
        locations = self._state[ToggleGroupType.LOCATION.value]
        locations = locations - {'tankman', 'recruit'}
        if not locations:
            return None
        else:
            criteria = REQ_CRITERIA.NONE
            if TankmanLocation.INBARRACKS.value in locations:
                criteria ^= ~REQ_CRITERIA.TANKMAN.IN_TANK
            if TankmanLocation.INTANK.value in locations:
                criteria ^= REQ_CRITERIA.TANKMAN.IN_TANK
            return criteria

    def _getSortKeyCriteria(self):
        criteria = REQ_CRITERIA.CUSTOM(lambda item: self.__rolesOrder[item.role])
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: -int(item.vehicleNativeDescr.type.compactDescr == self.__vehicle.intCD))
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: -int(item.vehicleNativeType == self.__vehicle.type))
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: VEHICLE_TYPES_ORDER_INDICES[item.vehicleNativeType])
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: -item.descriptor.totalXP(freeSkillsAsCommon=True))
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: item.fullUserName)
        return criteria

    def _getInitialItems(self):
        items = super(TankmenChangeDataProvider, self)._getInitialItems()
        return [self.__tankman] + items if self.__tankman else items

    def _itemsGetter(self, criteria, initial=False):
        tankmenKinds = self._state[ToggleGroupType.TANKMANKIND.value]
        if 'tankman' in self._state[ToggleGroupType.LOCATION.value]:
            tankmenKinds = tankmenKinds | {'tankman'}
        if 'recruit' in self._state[ToggleGroupType.LOCATION.value]:
            tankmenKinds = tankmenKinds | {'recruit'}
        if not tankmenKinds or initial:
            tankmenKinds = ['tankman']
        items = []
        if 'dismissed' in tankmenKinds:
            items += self._getDismissedTankmen()
        elif 'tankman' in tankmenKinds:
            items += self._getInventoryTankmen()
        items = filter(criteria, items)
        if self.__tankman and self.__tankman in items:
            items.remove(self.__tankman)
        return items

    def __reorderRoles(self, requiredRole):
        roles = [requiredRole] + [ role for role in Tankman.TANKMEN_ROLES_ORDER if role != requiredRole ]
        self.__rolesOrder = OrderedDict([ (role, idx) for idx, role in enumerate(roles) ])


class RecruitsChangeDataProvider(RecruitsDataProvider):
    __slots__ = ('__tankman', '__vehicle', '__role')

    def __init__(self, state, tankman=None, vehicle=None, role=None):
        self.__tankman = tankman
        self.__vehicle = vehicle
        self.__role = role
        super(RecruitsChangeDataProvider, self).__init__(state)

    @property
    def tankman(self):
        return self.__tankman

    @property
    def vehicle(self):
        return self.__vehicle

    @property
    def role(self):
        return self.__role

    def clear(self):
        self.__tankman = None
        self.__vehicle = None
        self.__role = None
        super(RecruitsChangeDataProvider, self).clear()
        return

    def reinit(self, tankman=None, role=None):
        self.__tankman = tankman
        self.__role = role
        super(RecruitsChangeDataProvider, self).reinit()

    def _getInitialFilterCriteria(self):
        criteria = super(RecruitsChangeDataProvider, self)._getInitialFilterCriteria()
        criteria |= REQ_CRITERIA.RECRUIT.ROLES([self.__role])
        criteria |= REQ_CRITERIA.RECRUIT.NATION([nations.NAMES[self.__vehicle.nationID]])
        return criteria

    def _getSortKeyCriteria(self):
        rolesOrder = Tankman.TANKMEN_ROLES_ORDER
        criteria = REQ_CRITERIA.CUSTOM(lambda item: rolesOrder[item.defaultRole] if len(item.getRoles()) == 1 else len(rolesOrder))
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: (-len(item.getFreeSkills()), -len(item.getEarnedSkills(multiplyNew=True))))
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: -item.getFreeXP())
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: item.getFullUserName())
        return criteria

    def _itemsGetter(self, criteria, initial=False):
        if 'dismissed' in self._state[ToggleGroupType.TANKMANKIND.value]:
            return []
        tankmenKinds = {'recruit', 'tankman'} & self._state[ToggleGroupType.LOCATION.value]
        if not tankmenKinds or initial:
            tankmenKinds = {'recruit'}
        items = []
        if 'recruit' in tankmenKinds:
            items += recruit_helper.getAllRecruitsInfo(sortByExpireTime=True)
        return filter(criteria, items)


class CrewSkinsDataProvider(FilterableItemsDataProvider):

    def __init__(self, state, tankman):
        self.__tankman = tankman
        super(CrewSkinsDataProvider, self).__init__(state)

    def clear(self):
        self.__tankman = None
        super(CrewSkinsDataProvider, self).clear()
        return

    def reinit(self, tankman=None):
        self.__tankman = tankman
        super(CrewSkinsDataProvider, self).reinit()

    def _getInitialFilterCriteria(self):
        criteria = REQ_CRITERIA.CREW_ITEM.IN_ACCOUNT
        if self.__tankman.isInSkin:
            criteria |= self._removeCurrentItemCriteria()
        return criteria

    def _getFiltersList(self):
        return [self._getFilterByPersonalDataTypeCriteria()]

    def _removeCurrentItemCriteria(self):
        return ~REQ_CRITERIA.CUSTOM(lambda item: item.descriptor.id == self.__tankman.skinID)

    def _getFilterByPersonalDataTypeCriteria(self):
        value = self._state[ToggleGroupType.PERSONALDATATYPE.value]
        if 'suitableSkin' not in value:
            return None
        else:
            tmanDescr = self.__tankman.descriptor
            if tmanDescr.isUnique:
                return REQ_CRITERIA.NONE
            validator = tankmen.g_cache.crewSkins().validateCrewSkin
            return REQ_CRITERIA.CUSTOM(lambda item: validator(tmanDescr, item.getID())[0] and item.getFreeCount())

    def _getSortKeyCriteria(self):
        criteria = REQ_CRITERIA.CUSTOM(lambda item: GUI_NATIONS_ORDER_INDEX.get(item.getNation(), len(GUI_NATIONS_ORDER_INDEX)))
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: -item.getRarity())
        criteria |= REQ_CRITERIA.CUSTOM(lambda item: -item.getID())
        return criteria

    def _getConditionSortCriteria(self):
        validator = tankmen.g_cache.crewSkins().validateCrewSkin
        criteria = REQ_CRITERIA.CUSTOM(lambda item: -int(validator(self.__tankman.descriptor, item.getID())[0] and item.getFreeCount()))
        return criteria

    def _itemsGetter(self, criteria, initial=False):
        dataTypes = self._state[ToggleGroupType.PERSONALDATATYPE.value]
        if not dataTypes or initial:
            dataTypes = {'suitableSkin'}
        return self.itemsCache.items.getItems(GUI_ITEM_TYPE.CREW_SKINS, criteria) if 'suitableSkin' in dataTypes else []


class DocumentsDataProvider(FilterableItemsDataProvider):
    Document = namedtuple('Document', ['icon', 'firstName', 'lastName'])

    def __init__(self, state, tankman):
        self.__tankman = tankman
        self.__seed = random.random()
        super(DocumentsDataProvider, self).__init__(state)

    @property
    def tankman(self):
        return self.__tankman

    def clear(self):
        self.__tankman = None
        self.__seed = None
        super(DocumentsDataProvider, self).clear()
        return

    def reinit(self, tankman=None):
        self.__tankman = tankman
        super(DocumentsDataProvider, self).reinit()

    def _getInitialFilterCriteria(self):
        criteria = super(DocumentsDataProvider, self)._getInitialFilterCriteria()
        if not self.__tankman.isInSkin:
            criteria |= self._removeCurrentItemCriteria()
        return criteria

    def _getFiltersList(self):
        return []

    def _removeCurrentItemCriteria(self):
        return ~REQ_CRITERIA.CUSTOM(lambda doc: bool(self.tankman.descriptor.iconID == doc.icon.id))

    def _getSortKeyCriteria(self):
        return REQ_CRITERIA.CUSTOM(lambda doc: -doc.icon.id)

    def _getConditionSortCriteria(self):
        return REQ_CRITERIA.EMPTY

    def _itemsGetter(self, criteria, initial=False):
        dataTypes = self._state[ToggleGroupType.PERSONALDATATYPE.value]
        if not dataTypes or initial:
            dataTypes = ['document']
        if 'document' not in dataTypes:
            return []
        config = tankmen.getNationConfig(self.tankman.nationID)
        icons = getDocGroupValues(self.tankman, config, operator.attrgetter('iconsList'), config.getExtensionLessIcon, False)
        firstnames = getDocGroupValues(self.tankman, config, operator.attrgetter('firstNamesList'), config.getFirstName)
        lastnames = getDocGroupValues(self.tankman, config, operator.attrgetter('lastNamesList'), config.getLastName)
        random.seed(self.__seed)
        items = [ self.Document(icon, random.choice(firstnames), random.choice(lastnames)) for icon in icons ]
        return filter(criteria, items)
