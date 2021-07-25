# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/popovers/vehicle_selector_popover_content.py
from enum import IntEnum
from constants import VEHICLE_CLASSES, MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL, VEHICLE_CLASS_MAP
from frameworks.wulf import ViewSettings
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_environment import ICarouselEnvironment
from gui.Scaleform.daapi.view.lobby.detachment.data_providers import SimplifiedVehiclesDataProvider
from gui.impl.lobby.detachment.popovers.popover_tracker_impl import PopoverTrackerImpl
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.impl.gen.view_models.views.lobby.detachment.common.drop_down_item_model import DropDownItemModel
from gui.impl.gen.view_models.views.lobby.detachment.popovers.vehicle_selector_list_item_model import VehicleSelectorListItemModel
from gui.impl.gen.view_models.views.lobby.detachment.popovers.vehicle_selector_popover_content_model import VehicleSelectorPopoverContentModel
from gui.impl.pub.view_impl import PopOverViewImpl
from gui.Scaleform.daapi.view.lobby.vehicle_selector_base import VehicleSelectorBase
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from gui.impl import backport
from gui.impl.auxiliary.detachmnet_convert_helper import isBarracksNotEmpty
from gui.impl.gen import R
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from nations import INDICES, ALL_NATIONS_INDEX
from skeletons.gui.shared import IItemsCache
from skeletons.gui.detachment import IDetachmentCache
defaultFilters = {'nation': -1,
 'vehicleType': 'none',
 'isMain': False,
 'hangar': False,
 'level': -1,
 'compatibleOnly': True}

class SortState(IntEnum):
    NO_SORTING = 0
    ASCENDING = 1
    DESCENDING = 2


SORTING_ORDER_BY_TYPE = {VehicleSelectorPopoverContentModel.SORTING_BY_TYPE: [VehicleSelectorPopoverContentModel.SORTING_BY_TYPE, VehicleSelectorPopoverContentModel.SORTING_BY_LEVEL, VehicleSelectorPopoverContentModel.SORTING_BY_NAME],
 VehicleSelectorPopoverContentModel.SORTING_BY_NAME: [VehicleSelectorPopoverContentModel.SORTING_BY_NAME, VehicleSelectorPopoverContentModel.SORTING_BY_LEVEL, VehicleSelectorPopoverContentModel.SORTING_BY_TYPE],
 VehicleSelectorPopoverContentModel.SORTING_BY_LEVEL: [VehicleSelectorPopoverContentModel.SORTING_BY_LEVEL, VehicleSelectorPopoverContentModel.SORTING_BY_TYPE, VehicleSelectorPopoverContentModel.SORTING_BY_NAME],
 VehicleSelectorPopoverContentModel.SORTING_BY_STATUS: [VehicleSelectorPopoverContentModel.SORTING_BY_STATUS,
                                                        VehicleSelectorPopoverContentModel.SORTING_BY_LEVEL,
                                                        VehicleSelectorPopoverContentModel.SORTING_BY_TYPE,
                                                        VehicleSelectorPopoverContentModel.SORTING_BY_NAME]}

class VehicleSelectorPopoverContent(PopoverTrackerImpl, PopOverViewImpl, ICarouselEnvironment, VehicleSelectorBase):
    __slots__ = ('__onVehicleSelected', '__dataProvider', '__detachment', '__defaultSortingSettings')
    __itemsCache = dependency.descriptor(IItemsCache)
    __detachmentCache = dependency.descriptor(IDetachmentCache)
    _sessionFilters = None

    def __init__(self, detachmentInvID=0, onLifecycleChange=None, onVehicleSelected=None, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.detachment.popovers.VehicleSelectorPopoverContent())
        settings.model = VehicleSelectorPopoverContentModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__onVehicleSelected = onVehicleSelected
        self.__detachment = self.__detachmentCache.getDetachment(detachmentInvID)
        self.__dataProvider = self._createDataProvider()
        self.__defaultSortingSettings = (VehicleSelectorPopoverContentModel.SORTING_BY_STATUS, SortState.DESCENDING)
        super(VehicleSelectorPopoverContent, self).__init__(settings, onLifecycleChange)

    def _createDataProvider(self):
        return SimplifiedVehiclesDataProvider()

    @property
    def viewModel(self):
        return super(VehicleSelectorPopoverContent, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(VehicleSelectorPopoverContent, self)._initialize()
        self.__addListeners()

    def _finalize(self):
        super(VehicleSelectorPopoverContent, self)._finalize()
        self.__onVehicleSelected = None
        self.__dataProvider.fini()
        self.__dataProvider = None
        self.__removeListeners()
        return

    def __initFilters(self, resetFilters=False):
        if resetFilters:
            VehicleSelectorPopoverContent._sessionFilters = dict(defaultFilters)
        sessionFilters = VehicleSelectorPopoverContent._sessionFilters
        vehicleType = VEHICLE_CLASS_MAP.get(self.__detachment.classID, defaultFilters['vehicleType'])
        sessionFilters['vehicleType'] = vehicleType
        filters = self._initFilter(nation=sessionFilters['nation'], vehicleType=sessionFilters['vehicleType'], isMain=sessionFilters['isMain'], level=sessionFilters['level'], compatibleOnly=sessionFilters['compatibleOnly'])
        availableNations = [ nationID for nationID in INDICES.itervalues() if isBarracksNotEmpty(nationID, excludeLockedCrew=False) ]
        availableNations.append(ALL_NATIONS_INDEX)
        filters['nationDP'] = [ nation for nation in filters['nationDP'] if nation['data'] in availableNations ]
        filters['hangar'] = sessionFilters['hangar']
        self._updateFilterWithDict(filters)

    def _onLoading(self, *args, **kwargs):
        super(VehicleSelectorPopoverContent, self)._onLoading()
        self.__initFilters(resetFilters=VehicleSelectorPopoverContent._sessionFilters is None)
        with self.viewModel.transaction() as vm:
            levels = vm.getLevels()
            levels.addViewModel(self.__createLevelFilterItem(-1, 'all', 'all'))
            for i in xrange(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1):
                levels.addViewModel(self.__createLevelFilterItem(i, 'c_' + str(i), str(i)))

            types = vm.getTypes()
            types.addViewModel(self.__createTypeFilterItem('none', 'all'))
            for vehClass in VEHICLE_CLASSES:
                types.addViewModel(self.__createTypeFilterItem(vehClass, vehClass))

            self.__updateSorting(vm, *self.__defaultSortingSettings)
            filters = self.getFilters()
            vm.setIsShowOnlyVehiclesInHangar(filters['hangar'])
            self.__updateList(vm)
        return

    def applyFilters(self, filters):
        VehicleSelectorPopoverContent._sessionFilters.update(filters)
        self._updateFilterWithDict(filters)

    def __addListeners(self):
        self.viewModel.onLevelChange += self.__onLevelChange
        self.viewModel.onTypeChange += self.__onTypeChange
        self.viewModel.onToggleShowOnlyVehiclesInHangar += self.__onToggleShowOnlyVehiclesInHangar
        self.viewModel.onVehicleSelect += self.__onVehicleSelect
        self.viewModel.onSortingChange += self.__onSortingChange
        self.viewModel.onFiltersReset += self.__onFiltersReset

    def __removeListeners(self):
        self.viewModel.onLevelChange -= self.__onLevelChange
        self.viewModel.onTypeChange -= self.__onTypeChange
        self.viewModel.onToggleShowOnlyVehiclesInHangar -= self.__onToggleShowOnlyVehiclesInHangar
        self.viewModel.onVehicleSelect -= self.__onVehicleSelect
        self.viewModel.onSortingChange -= self.__onSortingChange
        self.viewModel.onFiltersReset -= self.__onFiltersReset

    def __createLevelFilterItem(self, itemID, name, iconName):
        filters = self.getFilters()
        item = DropDownItemModel()
        item.setId(str(itemID))
        item.setTitle(backport.text(R.strings.menu.levels.dyn(name)()))
        item.setIcon(R.images.gui.maps.icons.filters.levels.dyn('level_' + iconName)())
        item.setIsSelected(filters['level'] == itemID)
        return item

    def __createTypeFilterItem(self, itemID, name):
        filters = self.getFilters()
        resName = replaceHyphenToUnderscore(name)
        item = DropDownItemModel()
        item.setId(itemID)
        item.setTitle(backport.text(R.strings.menu.carousel_tank_filter.dyn(resName)()))
        item.setIcon(R.images.gui.maps.icons.filters.tanks.dyn(resName)())
        item.setIsSelected(filters['vehicleType'] == itemID)
        return item

    def __onLevelChange(self, event):
        levelToSwitch = event.get('id')
        self.applyFilters({'level': int(levelToSwitch)})
        with self.viewModel.transaction() as vm:
            self.__updateFilter(vm.getLevels(), 'level')
            self.__updateList(vm)

    def __onTypeChange(self, event):
        typeToSwitch = event.get('id')
        self.applyFilters({'vehicleType': typeToSwitch})
        with self.viewModel.transaction() as vm:
            self.__updateFilter(vm.getTypes(), 'vehicleType')
            self.__updateList(vm)

    def __onToggleShowOnlyVehiclesInHangar(self):
        filters = self.getFilters()
        inHagarToSwitch = not filters['hangar']
        self.applyFilters({'hangar': inHagarToSwitch})
        with self.viewModel.transaction() as vm:
            vm.setIsShowOnlyVehiclesInHangar(inHagarToSwitch)
            self.__updateList(vm)

    def __onVehicleSelect(self, event):
        if self.__onVehicleSelected:
            self.__onVehicleSelected(event.get('id'))
        self.destroyWindow()

    def __onSortingChange(self, event):
        sortButtonId = event.get('id')
        with self.viewModel.transaction() as vm:
            if vm.getSelectedSortTab() == sortButtonId:
                currentState = vm.getSelectedSortTabState()
                newState = currentState + 1 if currentState < SortState.DESCENDING else SortState.ASCENDING
            else:
                newState = SortState.DESCENDING
            self.__updateSorting(vm, sortButtonId, newState)
            self.__updateList(vm)

    def __onFiltersReset(self):
        self.__initFilters(resetFilters=True)
        with self.viewModel.transaction() as vm:
            self.__updateSorting(vm, *self.__defaultSortingSettings)
            self.__updateList(vm)
            self.__updateFilter(vm.getLevels(), 'level')
            self.__updateFilter(vm.getTypes(), 'vehicleType')
            filters = self.getFilters()
            vm.setIsShowOnlyVehiclesInHangar(filters['hangar'])

    def __updateFilter(self, filtersList, filterName):
        filters = self.getFilters()
        for filterItemVM in filtersList:
            itemID = filterItemVM.getId()
            if filterName == 'level':
                itemID = int(itemID)
            filterItemVM.setIsSelected(filters[filterName] == itemID)

    def __updateSorting(self, vm, sortingType, sortingState):
        fields = SORTING_ORDER_BY_TYPE[sortingType]
        order = [sortingState == SortState.ASCENDING] * len(fields)
        self.__dataProvider.pySortOn(fields, order)
        vm.setSelectedSortTab(sortingType)
        vm.setSelectedSortTabState(sortingState)

    def __updateList(self, viewModel):
        vehicleListVM = viewModel.getVehicleList()
        vehicleListVM.clear()
        allVehicles = self.__itemsCache.items.getVehicles()
        vehicles = self._updateData(allVehicles, compatiblePredicate=lambda vo: True)
        self.__dataProvider.buildList(vehicles)
        for vehicleVM in self.__dataProvider.sortedCollection:
            vehicleListVM.addViewModel(vehicleVM)

        selectedVehCD = g_detachmentTankSetupVehicle.item.descriptor.type.compactDescr
        viewModel.setSelectedVehicle(selectedVehCD)
        vehicleListVM.invalidate()

    def _collectCriteria(self):
        criteria = super(VehicleSelectorPopoverContent, self)._collectCriteria()
        filters = self.getFilters()
        criteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE | ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
        criteria |= REQ_CRITERIA.INVENTORY ^ ~REQ_CRITERIA.VEHICLE.SECRET
        criteria |= REQ_CRITERIA.NATIONS([self.__detachment.nationID])
        if filters.get('hangar', False):
            criteria |= REQ_CRITERIA.INVENTORY
        return criteria

    def _makeVehicleVOAction(self, vehicle):
        vehicles = self.__detachment.getVehicleCDs()
        isLearned = vehicle.intCD in vehicles
        vehicleVM = VehicleSelectorListItemModel()
        vehicleVM.setId(vehicle.intCD)
        vehicleVM.setName(vehicle.userName)
        vehicleVM.setLevel(vehicle.level)
        vehicleVM.setType(replaceHyphenToUnderscore(vehicle.type))
        vehicleVM.setIcon(replaceHyphenToUnderscore(vehicle.nationName + '_' + vehicle.name.split(':')[1]))
        vehicleVM.setIsElite(vehicle.isElite)
        vehicleVM.setIsInHangar(vehicle.inventoryCount)
        vehicleVM.setIsLearnedForDetachment(isLearned)
        if isLearned:
            vehicleVM.setVehicleSlotPriority(self.__detachment.maxVehicleSlots - vehicles.index(vehicle.intCD))
        return vehicleVM
