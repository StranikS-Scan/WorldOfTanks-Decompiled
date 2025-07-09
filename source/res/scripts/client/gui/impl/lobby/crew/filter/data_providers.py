# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/filter/data_providers.py
import operator
import random
import nations
from collections import OrderedDict, namedtuple
from typing import Optional
from Event import Event
from constants import MAX_VEHICLE_LEVEL
from gui import GUI_NATIONS_ORDER_INDICES, GUI_NATIONS_ORDER_INDEX
from gui.game_control import restore_contoller
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.filter_toggle_group_model import ToggleGroupType
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanKind, TankmanLocation
from gui.impl.lobby.crew.crew_helpers.sort_helpers import SortHeap
from gui.impl.lobby.crew.filter import VEHICLE_LOCATION_IN_HANGAR, GRADE_PREMIUM, GRADE_ELITE, GRADE_PRIMARY
from gui.impl.lobby.crew.utils import getDocGroupValues, getSecretWithoutRentCriteria, getPremiumWithoutRentCriteria
from gui.server_events import recruit_helper
from gui.server_events.recruit_helper import _BaseRecruitInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES, VEHICLE_TAGS, checkForTags
from gui.shared.utils.requesters import REQ_CRITERIA, RequestCriteria
from helpers import dependency
from items import tankmen
from skeletons.gui.shared import IItemsCache
from itertools import groupby

class FilterableItemsDataProvider(object):
    __slots__ = ('_state', '_initialItemsCount', '__itemsCount', '__vehSortHeap', '__items', 'onDataChanged')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, state):
        self.onDataChanged = Event()
        self._state = state
        self._initialItemsCount = None
        self.__itemsCount = None
        self.__vehSortHeap = None
        self.__items = None
        return

    def __getitem__(self, item):
        return self.items()[item]

    def clear(self):
        self._initialItemsCount = None
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
        if self._initialItemsCount is None:
            self._initialItemsCount = len(self._getInitialItems())
        return self._initialItemsCount

    @property
    def itemsCount(self):
        if self.__itemsCount is None:
            self.__itemsCount = len(self.items())
        return self.__itemsCount

    def reinit(self):
        self.__items = None
        self.__itemsCount = None
        self._initialItemsCount = None
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


class TankmanDataProviderBase(FilterableItemsDataProvider):
    SECONDS_IN_DAY = 86400
    __slots__ = ('_inventoryTankman', '_dismissedTankman', '_recruitTankman', '_uniqueTankman', '_groupedSortedList', '_headerIndexes')

    def __init__(self, state):
        super(TankmanDataProviderBase, self).__init__(state)
        self._inventoryTankman = None
        self._dismissedTankman = None
        self._recruitTankman = None
        self._uniqueTankman = None
        self._groupedSortedList = None
        self._headerIndexes = None
        return

    @property
    def stateValue(self):
        return self._state

    def getActualItemsAmount(self):
        return len(self.getTankmanSortedList()) if self._shouldUseSortedList() else self.itemsCount

    def _shouldUseSortedList(self):
        return False

    def clear(self):
        self._resetValues()
        super(TankmanDataProviderBase, self).clear()

    def reinit(self):
        self._resetValues()
        super(TankmanDataProviderBase, self).reinit()

    def getHeaderIndexes(self):
        if self._shouldSkipHeaders():
            return []
        elif self._headerIndexes is not None:
            return self._headerIndexes
        else:
            self.getTankmanSortedList()
            return self._headerIndexes

    def _shouldSkipHeaders(self):
        raise NotImplementedError()

    def getTankmanSortedList(self):
        raise NotImplementedError

    def _resetValues(self):
        self._inventoryTankman = None
        self._dismissedTankman = None
        self._recruitTankman = None
        self._uniqueTankman = None
        self._groupedSortedList = None
        self._headerIndexes = None
        return

    def _getCombinedTankman(self):
        return self._getInventoryTankman() + self._getRecruitsTankman()

    def _getInventoryTankman(self):
        if self._inventoryTankman is None:
            self._inventoryTankman = self.itemsCache.items.getInventoryTankmen().values()
        return self._inventoryTankman

    def _getDismissedTankman(self):
        if self._dismissedTankman is None:
            self._dismissedTankman = self.itemsCache.items.getDismissedTankmen().values()
        return self._dismissedTankman

    def _getRecruitsTankman(self):
        if self._recruitTankman is None:
            self._recruitTankman = recruit_helper.getAllRecruitsInfo()
        return self._recruitTankman

    def _getUniqueTankman(self):
        if self._uniqueTankman is None:
            self._uniqueTankman = []
            inventoryTankman = self._getInventoryTankman() or []
            recruitsTankman = self._getRecruitsTankman() or []
            self._uniqueTankman.extend((item for item in inventoryTankman if item.descriptor and item.descriptor.isUnique or item.isInSkin))
            self._uniqueTankman.extend((item for item in recruitsTankman if hasattr(item, 'isUnique') and item.isUnique()))
        return self._uniqueTankman

    def _getSortKeyCriteria(self):
        return REQ_CRITERIA.CUSTOM(self._getUnifiedSortKey)

    def _getUnifiedSortKey(self, item):
        return self._getExtraSortKey(item) + self._getBaseSortKey(item)

    def _getExtraSortKey(self, item):
        pass

    def _getBaseSortKey(self, item):
        if isinstance(item, Tankman):
            dismissedDays = 0
            if item.isDismissed:
                _, time = restore_contoller.getTankmenRestoreInfo(item)
                dismissedDays = time // self.SECONDS_IN_DAY
            tdescr = item.descriptor
            isInTank = int(item.isInTank)
            nationOrder = GUI_NATIONS_ORDER_INDICES[item.nationID]
            newSkills, progressToNext = item.getNewSkillCount(onlyFull=True)
            freeSkills = len(tdescr.freeSkills)
            totalSkillCount = len(tdescr.skills) + newSkills
            roleLevel = tdescr.roleLevel
            roleOrder = Tankman.TANKMEN_ROLES_ORDER[tdescr.role]
            vehicleLevel = item.vehicleNativeDescr.level if item.vehicleNativeDescr else 0
        else:
            dismissedDays = 0
            isInTank = 0
            nationOrder = GUI_NATIONS_ORDER_INDICES[item.defaultNation] if len(item.getNations()) == 1 else -1
            freeSkills = len(item.getFreeSkills())
            totalSkillCount = len(item.getEarnedSkills(multiplyNew=True)) + freeSkills
            _, progressToNext = item.getNewSkillCount(onlyFull=False)
            roleLevel = item.getRoleLevel()
            roleOrder = Tankman.TANKMEN_ROLES_ORDER[item.defaultRole] if len(item.getRoles()) == 1 else -1
            vehicleLevel = 0
        return (dismissedDays,
         isInTank,
         nationOrder,
         -totalSkillCount,
         -freeSkills,
         -progressToNext,
         -roleLevel,
         roleOrder,
         -vehicleLevel)

    def _buildFilterCriteria(self, combined=None, recruit=None, dismissed=None):
        raise NotImplementedError


class BarracksDataProvider(TankmanDataProviderBase):

    @property
    def newItemsCount(self):
        return recruit_helper.getNewRecruitsCounter()

    @property
    def stateValue(self):
        tankmanKinds = self._state[ToggleGroupType.TANKMANKIND.value]
        return next(iter(tankmanKinds), '') if isinstance(tankmanKinds, set) else tankmanKinds

    @property
    def initialItemsCount(self):
        if self._initialItemsCount is None:
            stateHandler = {TankmanKind.TANKMAN.value: self._getCombinedTankman,
             TankmanKind.UNIQUE.value: self._getUniqueTankman,
             TankmanKind.RECRUIT.value: self._getRecruitsTankman,
             TankmanKind.DISMISSED.value: self._getDismissedTankman}
            handler = stateHandler.get(self.stateValue)
            if handler is not None:
                self._initialItemsCount = len(handler())
            else:
                self._initialItemsCount = self.itemsCount
        return self._initialItemsCount

    def tankmanInBarracksCount(self):
        return sum((not tankman.isInTank for tankman in self._getInventoryTankman()))

    def recruitTankmanCount(self):
        return len(self._getRecruitsTankman())

    def _shouldUseSortedList(self):
        return self.stateValue in (TankmanKind.TANKMAN.value, TankmanKind.UNIQUE.value)

    def getTankmanSortedList(self):
        if self._groupedSortedList is not None:
            return self._groupedSortedList
        else:
            items = self.items()
            if not items:
                self._groupedSortedList = []
                self._headerIndexes = []
                return self._groupedSortedList
            title = {True: backport.text(R.strings.crew.tankmanList.tooltip.location.in_tank.title()),
             False: backport.text(R.strings.crew.tankmanList.tooltip.location.in_barracks.title())}
            self._groupedSortedList = []
            self._headerIndexes = []
            for isInTank, group in groupby(items, key=lambda t: bool(getattr(t, 'isInTank', False))):
                self._headerIndexes.append(len(self._groupedSortedList))
                self._groupedSortedList.append({'type': 'header',
                 'title': title[isInTank]})
                self._groupedSortedList.extend(group)

            return self._groupedSortedList

    def _getInitialFilterCriteria(self):
        if self.stateValue in (TankmanKind.TANKMAN.value, TankmanKind.UNIQUE.value):
            criteria = ~REQ_CRITERIA.COMBINED.VEHICLE_BATTLE_ROYALE()
            criteria |= ~REQ_CRITERIA.COMBINED.VEHICLE_HIDDEN_IN_HANGAR()
            criteria |= REQ_CRITERIA.COMBINED.IS_LOCK_CREW()
            return criteria
        return REQ_CRITERIA.EMPTY

    def _shouldSkipHeaders(self):
        return self.stateValue not in (TankmanKind.TANKMAN.value, TankmanKind.UNIQUE.value)

    def _itemsGetter(self, criteria, initial=False):
        state = {TankmanKind.TANKMAN.value: self._getCombinedTankman,
         TankmanKind.UNIQUE.value: self._getUniqueTankman,
         TankmanKind.RECRUIT.value: self._getRecruitsTankman,
         TankmanKind.DISMISSED.value: self._getDismissedTankman}
        getter = state.get(self.stateValue)
        items = getter() if getter else []
        self._groupedSortedList = None
        self._headerIndexes = None
        self._initialItemsCount = None
        if criteria:
            return [ item for item in items if criteria(item) ]
        else:
            return items

    def _getFiltersList(self):
        return [self._getFilterByLocation(),
         self._getFilterByNations(),
         self._getFilterByRoles(),
         self._getSearchCriteria(),
         self._getFilterByVehicleType(),
         self._getFilterByVehicleTier(),
         self._getFilterByVehicleGrade(),
         self._getFilterByVehicleCD()]

    def _buildFilterCriteria(self, combined=None, recruit=None, dismissed=None):
        stateHandler = {TankmanKind.TANKMAN.value: combined,
         TankmanKind.UNIQUE.value: combined,
         TankmanKind.RECRUIT.value: recruit,
         TankmanKind.DISMISSED.value: dismissed}
        handler = stateHandler.get(self.stateValue)
        return handler() if handler else None

    def _getSearchCriteria(self):
        search = self._state.searchString
        return None if not search else self._buildFilterCriteria(combined=lambda : REQ_CRITERIA.COMBINED.SPECIFIC_BY_NAME(search), recruit=lambda : REQ_CRITERIA.RECRUIT.SPECIFIC_BY_NAME(search), dismissed=lambda : REQ_CRITERIA.TANKMAN.SPECIFIC_BY_NAME_OR_SKIN(search))

    def _getFilterByRoles(self):
        roles = self._state[ToggleGroupType.TANKMANROLE.value]
        return None if not roles else self._buildFilterCriteria(combined=lambda : REQ_CRITERIA.COMBINED.ROLES(roles), recruit=lambda : REQ_CRITERIA.RECRUIT.ROLES(roles), dismissed=lambda : REQ_CRITERIA.TANKMAN.ROLES(roles))

    def _getFilterByNations(self):
        nation = self._state[ToggleGroupType.NATION.value]
        return None if not nation else self._buildFilterCriteria(combined=lambda : REQ_CRITERIA.COMBINED.NATION(nation), recruit=lambda : REQ_CRITERIA.RECRUIT.NATION(nation), dismissed=lambda : REQ_CRITERIA.TANKMAN.NATION(nation))

    def _getFilterByLocation(self):
        locations = self._state[ToggleGroupType.VEHICLEGRADE.value]
        return None if not locations & {TankmanLocation.INBARRACKS.value, TankmanLocation.INTANK.value} else self._buildFilterCriteria(combined=lambda : REQ_CRITERIA.COMBINED.LOCATION(locations), recruit=lambda : REQ_CRITERIA.RECRUIT.LOCATION(locations), dismissed=lambda : REQ_CRITERIA.TANKMAN.LOCATION(locations))

    def _getFilterByVehicleType(self):
        vehicleTypes = self._state[ToggleGroupType.VEHICLETYPE.value]
        return None if not vehicleTypes else self._buildFilterCriteria(combined=lambda : REQ_CRITERIA.COMBINED.VEHICLE_NATIVE_TYPES(vehicleTypes), recruit=lambda : REQ_CRITERIA.NONE, dismissed=lambda : REQ_CRITERIA.TANKMAN.VEHICLE_NATIVE_TYPES(vehicleTypes))

    def _getFilterByVehicleTier(self):
        vehicleTiers = {int(t) for t in self._state[ToggleGroupType.VEHICLETIER.value]}
        return None if not vehicleTiers else self._buildFilterCriteria(combined=lambda : REQ_CRITERIA.COMBINED.VEHICLE_NATIVE_LEVELS(vehicleTiers), recruit=lambda : REQ_CRITERIA.NONE, dismissed=lambda : REQ_CRITERIA.TANKMAN.VEHICLE_NATIVE_LEVELS(vehicleTiers))

    def _getFilterByVehicleGrade(self):
        grades = self._state[ToggleGroupType.VEHICLEGRADE.value]
        return None if not grades & {GRADE_PREMIUM, GRADE_ELITE, GRADE_PRIMARY} else self._buildFilterCriteria(combined=lambda : REQ_CRITERIA.COMBINED.VEHICLE_GRADE(grades), recruit=lambda : REQ_CRITERIA.NONE, dismissed=lambda : REQ_CRITERIA.TANKMAN.VEHICLE_GRADE(grades))

    def _getFilterByVehicleCD(self):
        vehicleCDs = self._state[ToggleGroupType.VEHICLECD.value]
        return None if not vehicleCDs else self._buildFilterCriteria(combined=lambda : REQ_CRITERIA.COMBINED.NATIVE_TANKS(vehicleCDs), recruit=lambda : REQ_CRITERIA.NONE, dismissed=lambda : REQ_CRITERIA.TANKMAN.NATIVE_TANKS(vehicleCDs))


class MemberChangeDataProvider(TankmanDataProviderBase):
    __slots__ = ('__tankman', '__vehicle', '__rolesOrder', '__role')
    GROUP_IN_VEHICLE = 'inVehicle'
    GROUP_IN_BARRACKS = 'inBarracks'
    GROUP_IN_TANK = 'inTank'

    def __init__(self, state, tankman=None, vehicle=None, role=None):
        super(MemberChangeDataProvider, self).__init__(state)
        self.__tankman = tankman
        self.__vehicle = vehicle
        self.role = role

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

    @property
    def stateValue(self):
        return self._state[ToggleGroupType.LOCATION.value]

    def items(self):
        items = super(MemberChangeDataProvider, self).items()
        return [self.__tankman] + items if self.__tankman and not self._isDismissedFilter() else items

    def _shouldUseSortedList(self):
        return not self._isDismissedFilter()

    def getTankmanSortedList(self):
        if self._groupedSortedList is not None:
            return self._groupedSortedList
        else:
            items = self.items()
            if not items or self._isDismissedFilter():
                self._groupedSortedList = items if items else []
                self._headerIndexes = []
                return self._groupedSortedList
            currentTankman = self.tankman
            currentVehicleCD = self.vehicle.intCD if self.vehicle else None

            def getGroupType(tman):
                if not isinstance(tman, Tankman) or not tman.isInTank:
                    return self.GROUP_IN_BARRACKS
                return self.GROUP_IN_VEHICLE if tman.vehicleDescr and tman.vehicleDescr.type.compactDescr == currentVehicleCD else self.GROUP_IN_TANK

            titleMap = {self.GROUP_IN_VEHICLE: R.strings.crew.tankmanList.tooltip.location.in_vehicle.title(),
             self.GROUP_IN_BARRACKS: R.strings.crew.tankmanList.tooltip.location.in_barracks.title(),
             self.GROUP_IN_TANK: R.strings.crew.tankmanList.tooltip.location.in_tank.title()}
            groups = {self.GROUP_IN_VEHICLE: [],
             self.GROUP_IN_BARRACKS: [],
             self.GROUP_IN_TANK: []}
            for tankman in items:
                groupType = getGroupType(tankman)
                groups[groupType].append(tankman)

            self._groupedSortedList = []
            self._headerIndexes = []
            for groupType in (self.GROUP_IN_VEHICLE, self.GROUP_IN_BARRACKS, self.GROUP_IN_TANK):
                group = groups[groupType]
                if not group:
                    continue
                self._headerIndexes.append(len(self._groupedSortedList))
                self._groupedSortedList.append({'type': 'header',
                 'title': backport.text(titleMap[groupType])})
                self._groupedSortedList.extend(group)

            if currentTankman:
                for i, t in enumerate(self._groupedSortedList):
                    if isinstance(t, Tankman) and t.invID == currentTankman.invID:
                        del self._groupedSortedList[i]
                        self._groupedSortedList.insert(self._headerIndexes[0] + 1, currentTankman)
                        break

            return self._groupedSortedList

    def reinit(self, tankman=None, role=None):
        self._resetValues()
        self.__tankman = tankman
        self.role = role
        super(MemberChangeDataProvider, self).reinit()

    def clear(self):
        self._resetValues()
        self.__vehicle = None
        self.__tankman = None
        self.role = None
        super(MemberChangeDataProvider, self).clear()
        return

    def _isDismissedFilter(self):
        return TankmanKind.DISMISSED.value in self._state[ToggleGroupType.TANKMANKIND.value]

    def _getInitialItems(self):
        items = super(MemberChangeDataProvider, self)._getInitialItems()
        return [self.__tankman] + items if self.__tankman else items

    def _shouldSkipHeaders(self):
        return self._isDismissedFilter()

    def _getInitialFilterCriteria(self):
        if self._isDismissedFilter():
            return self._getDismissedInitialFilterCriteria()
        state = self.stateValue
        if state & {TankmanKind.TANKMAN.value, TankmanKind.UNIQUE.value}:
            return self._getCombineInitialFilterCriteria()
        return self._getRecruitInitialFilterCriteria() if TankmanKind.RECRUIT.value in state else REQ_CRITERIA.EMPTY

    def _getDismissedInitialFilterCriteria(self):
        criteria = ~REQ_CRITERIA.TANKMAN.VEHICLE_BATTLE_ROYALE
        criteria |= ~REQ_CRITERIA.TANKMAN.VEHICLE_HIDDEN_IN_HANGAR
        criteria |= REQ_CRITERIA.TANKMAN.NATION([nations.NAMES[self.__vehicle.nationID]])
        criteria |= ~REQ_CRITERIA.CUSTOM(lambda tankman: checkForTags(self.itemsCache.items.getVehicle(tankman.vehicleInvID).tags, VEHICLE_TAGS.CREW_LOCKED) if tankman.isInTank else False)
        criteria |= REQ_CRITERIA.CUSTOM(lambda tankman: tankmen.tankmenGroupHasRole(tankman.descriptor.nationID, tankman.descriptor.gid, tankman.descriptor.isPremium, self.role))
        return criteria

    def _getCombineInitialFilterCriteria(self):
        criteria = ~REQ_CRITERIA.COMBINED.VEHICLE_BATTLE_ROYALE()
        criteria |= ~REQ_CRITERIA.COMBINED.VEHICLE_HIDDEN_IN_HANGAR()
        criteria |= REQ_CRITERIA.COMBINED.IS_LOCK_CREW()
        criteria |= REQ_CRITERIA.COMBINED.NATION([nations.NAMES[self.__vehicle.nationID]])
        return criteria

    def _getRecruitInitialFilterCriteria(self):
        criteria = REQ_CRITERIA.RECRUIT.ROLES([self.role])
        criteria |= REQ_CRITERIA.RECRUIT.NATION([nations.NAMES[self.__vehicle.nationID]])
        return criteria

    def _getFiltersList(self):
        return [self._getFilterByVehicleType(),
         self._getFilterByVehicleTier(),
         self._getFilterByRoles(),
         self._getFilterByLocations(),
         self._getFilterNotAllowRecruit()]

    def _buildFilterCriteria(self, combined=None, recruit=None, dismissed=None):
        if self._isDismissedFilter() and dismissed:
            return dismissed()
        else:
            priorityList = [(TankmanKind.RECRUIT.value, recruit), (TankmanKind.TANKMAN.value, combined), (TankmanKind.UNIQUE.value, combined)]
            state = self.stateValue
            for priority, handler in priorityList:
                if priority in state and handler:
                    return handler()

            return None

    def _getFilterByVehicleType(self):
        vehicleTypes = self._state[ToggleGroupType.VEHICLETYPE.value]
        return None if not vehicleTypes else self._buildFilterCriteria(combined=lambda : REQ_CRITERIA.COMBINED.VEHICLE_NATIVE_TYPES(vehicleTypes), recruit=lambda : REQ_CRITERIA.EMPTY, dismissed=lambda : REQ_CRITERIA.TANKMAN.VEHICLE_NATIVE_TYPES(vehicleTypes))

    def _getFilterByVehicleTier(self):
        vehicleTiers = {int(t) for t in self._state[ToggleGroupType.VEHICLETIER.value]}
        return None if not vehicleTiers else self._buildFilterCriteria(combined=lambda : REQ_CRITERIA.COMBINED.VEHICLE_NATIVE_LEVELS(vehicleTiers), recruit=lambda : REQ_CRITERIA.NONE, dismissed=lambda : REQ_CRITERIA.TANKMAN.VEHICLE_NATIVE_LEVELS(vehicleTiers))

    def _getFilterByRoles(self):
        roles = self._state[ToggleGroupType.TANKMANROLE.value]
        return None if not roles else self._buildFilterCriteria(combined=lambda : REQ_CRITERIA.COMBINED.ROLES(roles), recruit=lambda : REQ_CRITERIA.RECRUIT.ROLES(roles), dismissed=lambda : REQ_CRITERIA.TANKMAN.ROLES(roles))

    def _getFilterNotAllowRecruit(self):
        return REQ_CRITERIA.CUSTOM(lambda item: any((role == self.role for role in item.getRoles())) if isinstance(item, _BaseRecruitInfo) else True)

    def _getFilterByLocations(self):
        state = self.stateValue
        state = state - {TankmanKind.TANKMAN.value, TankmanKind.UNIQUE.value, TankmanKind.RECRUIT.value}
        return REQ_CRITERIA.COMBINED.LOCATION(state) if state else None

    def _getExtraSortKey(self, item):
        if isinstance(item, Tankman):
            sameVehicle = int(item.vehicleNativeDescr.type.compactDescr == self.__vehicle.intCD)
            return (-sameVehicle,)

    def _itemsGetter(self, criteria, initial=False):
        self._groupedSortedList = None
        self._headerIndexes = None
        if self._isDismissedFilter():
            return filter(criteria, self._getDismissedTankman())
        else:
            state = {TankmanKind.TANKMAN.value: self._getCombinedTankman,
             TankmanKind.UNIQUE.value: self._getUniqueTankman,
             TankmanKind.RECRUIT.value: self._getRecruitsTankman}
            currentState = self.stateValue
            items = []
            for kind, getter in state.items():
                if kind in currentState:
                    items += getter()

            if self.__tankman and self.__tankman in items:
                items.remove(self.__tankman)
            return filter(criteria, items) if criteria else items

    def __reorderRoles(self, requiredRole):
        roles = [requiredRole] + [ role for role in Tankman.TANKMEN_ROLES_ORDER if role != requiredRole ]
        self.__rolesOrder = OrderedDict([ (role, idx) for idx, role in enumerate(roles) ])


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
        return REQ_CRITERIA.EMPTY

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
