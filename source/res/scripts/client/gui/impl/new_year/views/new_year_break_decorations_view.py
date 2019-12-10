# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_break_decorations_view.py
import random
from collections import namedtuple, defaultdict
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewStatus
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_break_decorations_view_model import NewYearBreakDecorationsViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_parts_tip_element_model import NewYearPartsTipElementModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.impl.new_year.tooltips.toy_content import RegularToyContent, MegaToyContent
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates
from gui.impl.new_year.views.new_year_break_filter_popover import NewYearBreakFilterPopover
from gui.impl.new_year.views.toy_presenter import BreakToyPresenter
from helpers import dependency
from new_year.craft_machine import CraftSettingsNames, mapToyParamsFromCraftUiToSrv, RANDOM_TOY_PARAM, MegaDeviceState
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import ICustomizableObjectsManager, INewYearController, ICraftMachineSettingsStorage
from gui.shared.utils import decorators
from items.components.ny_constants import ToyTypes, ToySettings, RANDOM_VALUE
from new_year.ny_processor import NewYearBreakToysProcessor
from new_year.ny_constants import SyncDataKeys
from gui.server_events import events_dispatcher as se_events
from gui.shared.sort_key import SortKey
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from PlayerEvents import g_playerEvents
_FilteredToysInfo = namedtuple('_FilteredToysInfo', ('toys', 'unseenToys', 'toyCount', 'totalToyCount'))
_ToysInfo = namedtuple('_ToysInfo', ('toyTypes', 'toyRanks'))
_SLOT_TYPE_ORDER = {v:i for i, v in enumerate((ToyTypes.MEGA_FIR,
 ToyTypes.MEGA_TABLEFUL,
 ToyTypes.MEGA_INSTALLATION,
 ToyTypes.MEGA_ILLUMINATION,
 ToyTypes.TOP,
 ToyTypes.GARLAND,
 ToyTypes.BALL,
 ToyTypes.FLOOR,
 ToyTypes.TABLE,
 ToyTypes.KITCHEN,
 ToyTypes.SCULPTURE,
 ToyTypes.DECORATION,
 ToyTypes.TREES,
 ToyTypes.GROUND_LIGHT,
 ToyTypes.TENT,
 ToyTypes.SNOW_ITEM,
 ToyTypes.PYRO))}
_TOY_SETTING_ORDER = {v:i for i, v in enumerate((ToySettings.NEW_YEAR,
 ToySettings.CHRISTMAS,
 ToySettings.ORIENTAL,
 ToySettings.FAIRYTALE,
 ToySettings.MEGA_TOYS))}
_ANIMATION_DELAY = 0.5

class _ToysToBreakSortKey(SortKey):
    __slots__ = ('toy',)

    def __init__(self, toy):
        super(_ToysToBreakSortKey, self).__init__()
        self.toy = toy

    def _cmp(self, other):
        toy1 = self.toy
        toy2 = other.toy
        toyMega1 = 0 if toy1.isMega() else 1
        toyMega2 = 0 if toy2.isMega() else 1
        if toyMega1 != toyMega2:
            return cmp(toyMega1, toyMega2)
        toyLevel1 = toy1.getRank()
        toyLevel2 = toy2.getRank()
        if toyLevel1 != toyLevel2:
            return cmp(toyLevel2, toyLevel1)
        slotOrder1 = _SLOT_TYPE_ORDER[toy1.getToyType()]
        slotOrder2 = _SLOT_TYPE_ORDER[toy2.getToyType()]
        if slotOrder1 != slotOrder2:
            return cmp(slotOrder1, slotOrder2)
        toySetting1 = _TOY_SETTING_ORDER[toy1.getSetting()]
        toySetting2 = _TOY_SETTING_ORDER[toy2.getSetting()]
        return cmp(toySetting1, toySetting2)


class NewYearBreakDecorationsView(NewYearHistoryNavigation):
    _itemsCache = dependency.descriptor(IItemsCache)
    _customizableObjMgr = dependency.descriptor(ICustomizableObjectsManager)
    _nyController = dependency.descriptor(INewYearController)
    _craftSettings = dependency.descriptor(ICraftMachineSettingsStorage)
    _lobbyCtx = dependency.descriptor(ILobbyContext)
    __slots__ = ('__toysInfo', '__seenToys', '__ignoreSelectedAllEvents', '__accountIsNonPlayer', '__breakToysAnimation', '__uniqueMegaToysCount', '__isMegaDeviceTurnedOn')

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_break_decorations_view.NewYearBreakDecorationsView())
        settings.model = NewYearBreakDecorationsViewModel()
        super(NewYearBreakDecorationsView, self).__init__(settings)
        self.__toysInfo = _ToysInfo(None, None)
        self.__ignoreSelectedAllEvents = False
        self.__seenToys = defaultdict(int)
        self.__accountIsNonPlayer = False
        self.__breakToysAnimation = False
        self.__uniqueMegaToysCount = 0
        self.__isMegaDeviceTurnedOn = False
        return

    @property
    def viewModel(self):
        return super(NewYearBreakDecorationsView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.new_year.tooltips.ny_regular_toy_tooltip_content.NyRegularToyTooltipContent():
            toyID = event.getArgument('toyID')
            return RegularToyContent(toyID)
        if event.contentID == R.views.lobby.new_year.tooltips.ny_mega_toy_tooltip_content.NyMegaToyTooltipContent():
            toyID = event.getArgument('toyID')
            return MegaToyContent(toyID)
        return NewYearPartsTooltipContent() if contentID == R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent() else None

    def createPopOverContent(self, event):
        return NewYearBreakFilterPopover(self.__toysInfo) if event.contentID == R.views.lobby.new_year.views.new_year_break_filter_popover.NewYearBreakFilterPopover() else None

    def _initialize(self, *args, **kwargs):
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: NewYearSoundEvents.DEBRIS,
         NewYearSoundConfigKeys.EXIT_EVENT: NewYearSoundEvents.DEBRIS_EXIT,
         NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.DEBRIS}
        super(NewYearBreakDecorationsView, self)._initialize(soundConfig)
        self.viewModel.onQuestsBtnClick += self.__onQuestsBtnClick
        self.viewModel.onFilterResetBtnClick += self.__onFilterResetBtnClick
        self.viewModel.onSelectedAllChanged += self.__onSelectedAllChanged
        self.viewModel.onViewResized += self.__onViewResized
        self.viewModel.onSlotStatusIsNewChanged += self.__onSlotStatusIsNewChanged
        self.viewModel.onBreakDecorationsBtnClick += self.__onBreakDecorationsBtnClick
        self.viewModel.filterCounter.onResetBtnClick += self.__onResetBtnClick
        self.viewModel.onBreakAnimationComplete += self.__onBreakAnimationComplete
        self._nyController.onDataUpdated += self.__onDataUpdated
        g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer
        g_eventBus.addListener(events.NewYearEvent.ON_BREAK_TOYS_FILTER_APPLIED, self.__onFilterAppliedEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.slotsList.onSelectionChanged += self.__onSelectionChanged
        self.__uniqueMegaToysCount = self._nyController.getUniqueMegaToysCount()
        self.__isMegaDeviceTurnedOn = self._craftSettings.getValue(CraftSettingsNames.MEGA_DEVICE_TURNED_ON, False)
        with self.viewModel.transaction() as model:
            shardsCount = self._itemsCache.items.festivity.getShardsCount()
            model.setShardsCount(shardsCount)
            model.setDecorationSelectedAll(True)
            desiredToyType = self.__getDesiredToyType()
            toyIcon = R.images.gui.maps.icons.new_year.decorationTypes.blue.dyn(desiredToyType)()
            model.shardsTip.setDecorationTypeIcon(toyIcon)
            self.__updateCraftCost(model, shardsCount)
            self.__updateSlots(model, initSelected=True)
            self.__updateInfoBySelectedItems()

    def _finalize(self):
        g_eventBus.removeListener(events.NewYearEvent.ON_BREAK_TOYS_FILTER_APPLIED, self.__onFilterAppliedEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self.viewModel.onQuestsBtnClick -= self.__onQuestsBtnClick
        self.viewModel.onFilterResetBtnClick -= self.__onFilterResetBtnClick
        self.viewModel.onSelectedAllChanged -= self.__onSelectedAllChanged
        self.viewModel.onViewResized -= self.__onViewResized
        self.viewModel.onSlotStatusIsNewChanged -= self.__onSlotStatusIsNewChanged
        self.viewModel.onBreakDecorationsBtnClick -= self.__onBreakDecorationsBtnClick
        self.viewModel.onBreakAnimationComplete -= self.__onBreakAnimationComplete
        self.viewModel.filterCounter.onResetBtnClick -= self.__onResetBtnClick
        self.viewModel.slotsList.onSelectionChanged -= self.__onSelectionChanged
        g_playerEvents.onAccountBecomeNonPlayer -= self.__onAccountBecomeNonPlayer
        self.__markToysAsSeen()
        super(NewYearBreakDecorationsView, self)._finalize()

    def _getInfoForHistory(self):
        return {'toysInfo': self.__toysInfo}

    def _restoreState(self, stateInfo):
        self.__toysInfo = stateInfo['toysInfo']

    def __updateSlots(self, viewModel, initSelected=False):
        slots = viewModel.slotsList
        needToInvalidateSlots = viewModel.slotsList.getItemsLength() > 0
        if needToInvalidateSlots:
            selectedIndices = viewModel.slotsList.getSelectedIndices()
            selectedIndices.clear()
            selectedIndices.invalidate()
            slots.clear()
        toyTypes = self.__toysInfo.toyTypes
        toyRanks = self.__toysInfo.toyRanks
        filteredToysInfo = self.__filterToys(toyTypes, toyRanks)
        self.__updateFilterCounters(viewModel, filteredToysInfo, True if toyTypes or toyRanks else False)
        if filteredToysInfo.totalToyCount == 0:
            if needToInvalidateSlots:
                slots.invalidate()
            viewModel.setShowDummy(True)
            viewModel.setDecorationSelectedAllEnable(False)
            return
        if filteredToysInfo.toyCount == 0:
            if needToInvalidateSlots:
                slots.invalidate()
            viewModel.setShowNotFoundPage(True)
            viewModel.setDecorationSelectedAllEnable(False)
            return
        if viewModel.getShowDummy():
            viewModel.setShowDummy(False)
            needToInvalidateSlots = True
        if viewModel.getShowNotFoundPage():
            viewModel.setShowNotFoundPage(False)
            needToInvalidateSlots = True
        filteredToysInfo.toys.sort(key=_ToysToBreakSortKey)
        unseenToys = filteredToysInfo.unseenToys
        for toyId, seenCount in self.__seenToys.iteritems():
            if toyId in unseenToys:
                unseenToys[toyId] -= seenCount

        for toy in filteredToysInfo.toys:
            slot = BreakToyPresenter(toy).asSlotModel()
            toyId = toy.getID()
            if toyId in unseenToys and unseenToys[toyId] > 0:
                slot.setIsNew(True)
                unseenToys[toyId] -= 1
            slots.addViewModel(slot, initSelected)

        if needToInvalidateSlots:
            slots.invalidate()
        if not viewModel.getDecorationSelectedAllEnable():
            self.viewModel.setDecorationSelectedAllEnable(True)
        if viewModel.getDecorationSelectedAll():
            viewModel.setDecorationSelectedAll(False)

    def __filterToys(self, toyTypes=None, toyRanks=None, countersOnly=False):
        toys = self._itemsCache.items.festivity.getToys()
        filteredToys = []
        unseenToys = defaultdict(int)
        if not toys:
            return _FilteredToysInfo(filteredToys, 0, 0, 0)
        totalToyCount = 0
        filteredToyCount = 0
        for toy in toys.itervalues():
            totalToyCount += toy.getCount()
            if toyTypes and toy.getToyType() not in toyTypes:
                continue
            if toyRanks and toy.getRank() not in toyRanks:
                continue
            unseenToys[toy.getID()] = toy.getUnseenCount()
            for _ in xrange(toy.getCount()):
                if not countersOnly:
                    filteredToys.append(toy)
                filteredToyCount += 1

        return _FilteredToysInfo(filteredToys, unseenToys, filteredToyCount, totalToyCount)

    @staticmethod
    def __updateFilterCounters(viewModel, filteredToysInfo, isFilterApplied=True):
        viewModel.filterCounter.setCurrentCount(filteredToysInfo.toyCount)
        viewModel.filterCounter.setTotalCount(filteredToysInfo.totalToyCount)
        viewModel.filterCounter.setIsFilterApplied(isFilterApplied)

    @staticmethod
    def __updateCraftCounters(viewModel, craftCost, shardsCount):
        if shardsCount < craftCost:
            viewModel.shardsTip.setCurrentState(NewYearPartsTipElementModel.SHARDS_NOT_ENOUGH)
            viewModel.shardsTip.setShardsCountLeft(craftCost - shardsCount)
        else:
            viewModel.shardsTip.setCurrentState(NewYearPartsTipElementModel.SHARDS_ENOUGH)

    def __onSelectionChanged(self, _=None):
        self.__updateInfoBySelectedItems()
        slots = self.viewModel.slotsList
        isAllItemsSelected = len(slots.getSelectedIndices()) == slots.getItemsLength()
        if isAllItemsSelected:
            if not self.viewModel.getDecorationSelectedAll():
                self.viewModel.setDecorationSelectedAll(True)
                self.__ignoreSelectedAllEvents = True
        elif self.viewModel.getDecorationSelectedAll():
            self.viewModel.setDecorationSelectedAll(False)
            self.__ignoreSelectedAllEvents = True

    def __onAlbumBtnClick(self):
        self._goToAlbumView()

    def __onQuestsBtnClick(self):
        se_events.showMissions()

    def __onFilterResetBtnClick(self):
        self.__resetFilter()

    def __onSelectedAllChanged(self, args):
        isSelected = args.get('selected')
        with self.viewModel.transaction() as model:
            selectedIndices = model.slotsList.getSelectedIndices()
            selectedIndices.clear()
            if isSelected:
                for index, _ in enumerate(model.slotsList.getItems()):
                    selectedIndices.addNumber(index)

            selectedIndices.invalidate()
        self.__updateInfoBySelectedItems()

    def __onSlotStatusIsNewChanged(self, args):
        slotItem = self.viewModel.slotsList.getItem(args.get('idx'))
        if slotItem is not None:
            slotItem.setIsNew(False)
            self.__seenToys[slotItem.getToyID()] += 1
        return

    @decorators.process('newYear/breakDecorationsWaiting')
    def __onBreakDecorationsBtnClick(self):
        self.__breakToysAnimation = True
        toysToBreakIDs = tuple((item.getToyID() for item in self.viewModel.slotsList.getSelectedItems()))
        toysToBreak = defaultdict(int)
        for toyID in toysToBreakIDs:
            toysToBreak[toyID] += 1

        result = yield NewYearBreakToysProcessor(toysToBreak=toysToBreak, expectedShardsCount=self.viewModel.getExpectedShardsCount(), parent=self, needConfirm=True).request()
        if result.success and self.viewStatus != ViewStatus.UNDEFINED:
            for toyID, toyCount in toysToBreak.iteritems():
                if toyID in self.__seenToys:
                    self.__seenToys[toyID] -= toyCount
                    if self.__seenToys[toyID] <= 0:
                        del self.__seenToys[toyID]

        if not result.success and result.userMsg and result.sysMsgType == SystemMessages.SM_TYPE.Error:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def __onBreakAnimationComplete(self, _=None):
        self.__updateShardsInfo()
        self.__breakToysAnimation = False

    def __onResetBtnClick(self):
        self.__resetFilter()

    def __updateInfoBySelectedItems(self):
        toys = self._itemsCache.items.festivity.getToys()
        selectedItems = self.viewModel.slotsList.getSelectedItems()
        with self.viewModel.transaction() as model:
            expectedShards = 0
            for item in selectedItems:
                toy = toys[item.getToyID()]
                expectedShards += toy.getShards()

            model.setExpectedShardsCount(expectedShards)
            model.setSelectedDecorationsCount(len(selectedItems))

    def __updateShardsCount(self, _=None):
        shardsCount = self._itemsCache.items.festivity.getShardsCount()
        with self.viewModel.transaction() as model:
            model.setShardsCount(shardsCount)
            self.__updateCraftCost(model, shardsCount)

    def __updateShardsInfo(self, _=None):
        self.__updateShardsCount()
        with self.viewModel.transaction() as model:
            model.setExpectedShardsCount(0)
            items = model.slotsList.getItems()
            selectedIndices = model.slotsList.getSelectedIndices()
            storedIndices = [] if self.viewModel.getDecorationSelectedAll() else [ i for i in selectedIndices ]
            selectedIndices.clear()
            selectedIndices.invalidate()
            if self.viewModel.getDecorationSelectedAll():
                self.viewModel.setDecorationSelectedAll(False)
                items.clear()
            else:
                items.removeValues(storedIndices)
            items.invalidate()
            toyTypes = self.__toysInfo.toyTypes
            toyRanks = self.__toysInfo.toyRanks
            filteredToysInfo = self.__filterToys(toyTypes, toyRanks, countersOnly=True)
            self.__updateFilterCounters(model, filteredToysInfo, True if toyTypes or toyRanks else False)
            if filteredToysInfo.totalToyCount == 0:
                model.setShowDummy(True)
                self.viewModel.setDecorationSelectedAllEnable(False)
            elif filteredToysInfo.toyCount == 0:
                model.setShowNotFoundPage(True)
                self.viewModel.setDecorationSelectedAllEnable(False)
            model.setSelectedDecorationsCount(0)
            model.setCurrentBreakDecorations(0)
            model.setTotalRegisterDecorations(0)

    def __onDataUpdated(self, keys):
        fragmentsChanged = SyncDataKeys.TOY_FRAGMENTS in keys
        toysChanged = SyncDataKeys.INVENTORY_TOYS in keys
        if toysChanged:
            uniqueMegaToysCount = self._nyController.getUniqueMegaToysCount()
            if uniqueMegaToysCount != self.__uniqueMegaToysCount:
                self.__uniqueMegaToysCount = uniqueMegaToysCount
                self.__onMegaToysChanged()
        if fragmentsChanged and toysChanged and self.__breakToysAnimation:
            with self.viewModel.transaction() as model:
                for item in model.slotsList.getSelectedItems():
                    item.setBreakDuration(_ANIMATION_DELAY + random.random() * _ANIMATION_DELAY)

            if self.viewModel.getTotalRegisterDecorations() == 0:
                self.__updateShardsInfo()
                self.__breakToysAnimation = False
            return
        if fragmentsChanged:
            self.__updateShardsCount()
        if toysChanged:
            with self.viewModel.transaction() as model:
                self.__updateSlots(model)

    def __onFilterAppliedEvent(self, event):
        ctx = event.ctx
        self.__toysInfo = _ToysInfo(ctx['toysTypes'], ctx['toysRanks'])
        with self.viewModel.transaction() as model:
            self.__updateSlots(model)
        self.__updateShardsInfo()

    def __resetFilter(self):
        self.viewModel.filterCounter.setIsFilterApplied(False)
        with self.viewModel.transaction() as model:
            self.__toysInfo = _ToysInfo(tuple(), tuple())
            self.__updateSlots(model)
        self.__updateShardsInfo()

    def __markToysAsSeen(self):
        if self.__accountIsNonPlayer:
            return
        if not self.__seenToys:
            return
        seenToysSrvFormat = []
        for k, v in self.__seenToys.iteritems():
            seenToysSrvFormat.append(k)
            seenToysSrvFormat.append(v)

        self._nyController.sendSeenToys(seenToysSrvFormat)
        self.__seenToys.clear()

    def __onAccountBecomeNonPlayer(self):
        self.__accountIsNonPlayer = True

    def __getCraftCost(self):
        craftCost = self._craftSettings.getValue(CraftSettingsNames.CRAFT_COST, None)
        if craftCost is None:
            craftCost = self.__calculateCraftCost(RANDOM_VALUE, RANDOM_VALUE, RANDOM_VALUE)
        return craftCost

    def __calculateCraftCost(self, toyType, toySetting, toyRank):
        craftCostConfig = self._lobbyCtx.getServerSettings().getNewYearCraftCostConfig()
        craftCost = craftCostConfig.calculateCraftCost(toyType, toySetting, toyRank)
        return craftCost

    def __calculateMegaCraftCost(self):
        craftCostConfig = self._lobbyCtx.getServerSettings().getNewYearCraftCostConfig()
        craftCost = craftCostConfig.calculateMegaCraftCost(self.__uniqueMegaToysCount)
        return craftCost

    def __updateCraftCost(self, model, shardsCount):
        if self.__getMegaDeviceState() == MegaDeviceState.ALL_MEGA_TOYS_COLLECTED_ERROR:
            model.shardsTip.setCurrentState(NewYearPartsTipElementModel.DECORATION_NOT_SELECTED)
            return
        craftCost = self.__getCraftCost()
        self.__updateCraftCounters(model, craftCost, shardsCount)

    def __getDesiredToyType(self):
        if self.__getMegaDeviceState() in MegaDeviceState.ACTIVATED:
            return ToyTypes.MEGA_COMMON
        else:
            savedRegularToyTypeID = self._craftSettings.getValue(CraftSettingsNames.TOY_TYPE_ID, None)
            if savedRegularToyTypeID is None:
                return RANDOM_TOY_PARAM
            desiredRegularToyTypeID, _, _ = mapToyParamsFromCraftUiToSrv(toyTypeIdx=savedRegularToyTypeID)
            return RANDOM_TOY_PARAM if desiredRegularToyTypeID == RANDOM_VALUE else ToyTypes.ALL[desiredRegularToyTypeID]

    def __onMegaToysChanged(self):
        newCraftCost = self.__calculateMegaCraftCost()
        self._craftSettings.setValue(CraftSettingsNames.CRAFT_COST, newCraftCost)
        shardsCount = self._itemsCache.items.festivity.getShardsCount()
        with self.viewModel.transaction() as model:
            self.__updateCraftCounters(model, newCraftCost, shardsCount)

    def __getMegaDeviceState(self):
        state = MegaDeviceState.INACTIVE
        if self.__isMegaDeviceTurnedOn:
            if self.__uniqueMegaToysCount < len(ToyTypes.MEGA):
                state = MegaDeviceState.ACTIVE
            else:
                state = MegaDeviceState.ALL_MEGA_TOYS_COLLECTED_ERROR
        return state

    def __onViewResized(self, event):
        self.viewModel.slotsList.invalidate()
