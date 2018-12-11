# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_break_decorations_view.py
import random
from collections import namedtuple, defaultdict
from frameworks.wulf import ViewFlags
from frameworks.wulf.gui_constants import ViewStatus
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.views.new_year_break_decorations_view_model import NewYearBreakDecorationsViewModel
from gui.impl.gen.view_models.new_year.views.new_year_parts_tip_element_model import NewYearPartsTipElementModel
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.impl.new_year.tooltips.toy_content import ToyContent
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates
from gui.impl.new_year.views.new_year_break_filter_popover import NewYearBreakFilterPopover
from gui.impl.new_year.views.toy_presenter import BreakToyPresenter
from gui.impl.wrappers.background_blur import WGUIBackgroundBlurSupportImpl
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import ICustomizableObjectsManager, INewYearController
from gui.shared.utils import decorators
from items.components.ny_constants import ToyTypes, ToySettings
from new_year.ny_processor import NewYearBreakToysProcessor
from new_year.ny_constants import SyncDataKeys
from gui.server_events import events_dispatcher as se_events
from gui.shared.sort_key import SortKey
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from PlayerEvents import g_playerEvents
_FilteredToysInfo = namedtuple('_FilteredToysInfo', ('toys', 'unseenToys', 'toyCount', 'totalToyCount'))
_ToysInfo = namedtuple('_ToysInfo', ('toyTypes', 'toyRanks'))
_SLOT_TYPE_ORDER = {v:i for i, v in enumerate((ToyTypes.TOP,
 ToyTypes.GARLAND,
 ToyTypes.BALL,
 ToyTypes.FLOOR,
 ToyTypes.TABLE,
 ToyTypes.KITCHEN,
 ToyTypes.SCULPTURE,
 ToyTypes.DECORATION,
 ToyTypes.TREES,
 ToyTypes.GROUND_LIGHT))}
_TOY_SETTING_ORDER = {v:i for i, v in enumerate((ToySettings.NEW_YEAR,
 ToySettings.CHRISTMAS,
 ToySettings.ORIENTAL,
 ToySettings.FAIRYTALE))}
_ANIMATION_DELAY = 0.5

class _ToysToBreakSortKey(SortKey):
    __slots__ = ('toy',)

    def __init__(self, toy):
        super(_ToysToBreakSortKey, self).__init__()
        self.toy = toy

    def _cmp(self, other):
        toy1 = self.toy
        toy2 = other.toy
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


class NewYearBreakDecorationsView(NewYearNavigation):
    _itemsCache = dependency.descriptor(IItemsCache)
    _customizableObjMgr = dependency.descriptor(ICustomizableObjectsManager)
    _nyController = dependency.descriptor(INewYearController)
    __slots__ = ('__blur', '__toysInfo', '__craftInfo', '__seenToys', '__ignoreSelectedAllEvents', '__accountIsNonPlayer', '__breakToysAnimation')

    def __init__(self, layoutID, toyType=None, craftInfo=None, blur3dScene=False, blurUI=False):
        super(NewYearBreakDecorationsView, self).__init__(R.views.newYearBreakDecorationsView, ViewFlags.LOBBY_SUB_VIEW, NewYearBreakDecorationsViewModel, layoutID)
        self.__blur = WGUIBackgroundBlurSupportImpl(blur3dScene, blurUI)
        self.__toysInfo = _ToysInfo((toyType,) if toyType is not None else None, None)
        self.__craftInfo = craftInfo
        self.__ignoreSelectedAllEvents = False
        self.__seenToys = defaultdict(int)
        self.__accountIsNonPlayer = False
        self.__breakToysAnimation = False
        return

    @property
    def viewModel(self):
        return super(NewYearBreakDecorationsView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.newYearToyTooltipContent:
            toyID = event.getArgument('toyID')
            return ToyContent(toyID)
        return NewYearPartsTooltipContent() if contentID == R.views.newYearPartsTooltipContent else None

    def createPopOverContent(self, event):
        return NewYearBreakFilterPopover(self.__toysInfo) if event.contentID == R.views.newYearBreakFilterPopover else None

    def _initialize(self, *args, **kwargs):
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: NewYearSoundEvents.DEBRIS,
         NewYearSoundConfigKeys.EXIT_EVENT: NewYearSoundEvents.DEBRIS_EXIT,
         NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.DEBRIS}
        super(NewYearBreakDecorationsView, self)._initialize(soundConfig)
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick
        self.viewModel.onBackBtnClick += self.__onBackBtnClick
        self.viewModel.onQuestsBtnClick += self.__onQuestsBtnClick
        self.viewModel.onFilterResetBtnClick += self.__onFilterResetBtnClick
        self.viewModel.onSelectedAllChanged += self.__onSelectedAllChanged
        self.viewModel.onSlotStatusIsNewChanged += self.__onSlotStatusIsNewChanged
        self.viewModel.onBreakDecorationsBtnClick += self.__onBreakDecorationsBtnClick
        self.viewModel.filterCounter.onResetBtnClick += self.__onResetBtnClick
        self.viewModel.onBreakAnimationComplete += self.__onBreakAnimationComplete
        self.viewModel.onCraftBtnClick += self.__onCraftBtnClick
        self._nyController.onDataUpdated += self.__onDataUpdated
        g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer
        g_eventBus.addListener(events.NewYearEvent.ON_BREAK_TOYS_FILTER_APPLIED, self.__onFilterAppliedEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__blur.enable()
        self.viewModel.slotsList.onSelectionChanged += self.__onSelectionChanged
        with self.viewModel.transaction() as model:
            shardsCount = self._itemsCache.items.festivity.getShardsCount()
            model.setPartsCount(shardsCount)
            model.setExpectedPartsCount(0)
            model.partsTip.setDecorationTypeIcon(R.images.gui.maps.icons.new_year.decorationTypes.blue.random)
            model.partsTip.setCurrentState(NewYearPartsTipElementModel.DECORATION_NOT_SELECTED)
            model.setBackViewName(self._getBackPageName())
            if self.__craftInfo is not None:
                if self.__craftInfo.desiredToy != -1:
                    desiredToyType = ToyTypes.ALL[self.__craftInfo.desiredToy]
                    toyIcon = R.images.gui.maps.icons.new_year.decorationTypes.blue.dyn(desiredToyType)
                    model.partsTip.setDecorationTypeIcon(toyIcon)
                self.__updateCraftCounters(model, self.__craftInfo.craftCost, shardsCount)
            self.__updateSlots(model)
        return

    def _finalize(self):
        g_eventBus.removeListener(events.NewYearEvent.ON_BREAK_TOYS_FILTER_APPLIED, self.__onFilterAppliedEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        self.viewModel.onBackBtnClick -= self.__onBackBtnClick
        self.viewModel.onQuestsBtnClick -= self.__onQuestsBtnClick
        self.viewModel.onFilterResetBtnClick -= self.__onFilterResetBtnClick
        self.viewModel.onSelectedAllChanged -= self.__onSelectedAllChanged
        self.viewModel.onSlotStatusIsNewChanged -= self.__onSlotStatusIsNewChanged
        self.viewModel.onBreakDecorationsBtnClick -= self.__onBreakDecorationsBtnClick
        self.viewModel.onBreakAnimationComplete -= self.__onBreakAnimationComplete
        self.viewModel.onCraftBtnClick -= self.__onCraftBtnClick
        self.viewModel.filterCounter.onResetBtnClick -= self.__onResetBtnClick
        self.viewModel.slotsList.onSelectionChanged -= self.__onSelectionChanged
        g_playerEvents.onAccountBecomeNonPlayer -= self.__onAccountBecomeNonPlayer
        self.__blur.disable()
        self.__markToysAsSeen()
        super(NewYearBreakDecorationsView, self)._finalize()

    def _getInfoForHistory(self):
        return {'craftInfo': self.__craftInfo,
         'toysInfo': self.__toysInfo,
         'blur': self.__blur}

    def _restoreState(self, stateInfo):
        self.__craftInfo = stateInfo['craftInfo']
        self.__toysInfo = stateInfo['toysInfo']
        self.__blur = stateInfo['blur']

    def __updateSlots(self, viewModel):
        slots = viewModel.slotsList.getItems()
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

        for idx, toy in enumerate(filteredToysInfo.toys):
            slot = BreakToyPresenter(toy).asSlotModel(idx)
            toyId = toy.getID()
            if toyId in unseenToys and unseenToys[toyId] > 0:
                slot.setIsNew(True)
                unseenToys[toyId] -= 1
            slots.addViewModel(slot)

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
            viewModel.partsTip.setCurrentState(NewYearPartsTipElementModel.PARTS_NOT_ENOUGH)
            viewModel.partsTip.setPartsCountLeft(craftCost - shardsCount)
        else:
            viewModel.partsTip.setCurrentState(NewYearPartsTipElementModel.PARTS_ENOUGH)

    def __onCloseBtnClick(self, _):
        self._goToMainView()

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

    def __onBackBtnClick(self, _):
        self._goBack()

    def __onAlbumBtnClick(self, _):
        self._goToAlbumView()

    def __onQuestsBtnClick(self, _):
        se_events.showMissions()

    def __onCraftBtnClick(self, _):
        self._goToCraftView()

    def __onFilterResetBtnClick(self, _):
        self.__resetFilter()

    def __onSelectedAllChanged(self, args):
        isSelected = args.get('value')
        if self.__ignoreSelectedAllEvents:
            self.__ignoreSelectedAllEvents = False
            return
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
    def __onBreakDecorationsBtnClick(self, _):
        self.__breakToysAnimation = True
        toysToBreakIDs = [ item.getToyID() for item in self.viewModel.slotsList.getSelectedItems() ]
        toysToBreak = defaultdict(int)
        for toyID in toysToBreakIDs:
            toysToBreak[toyID] += 1

        result = yield NewYearBreakToysProcessor(toysToBreak, self.viewModel.getExpectedPartsCount()).request()
        if result.success and self.viewStatus != ViewStatus.UNDEFINED:
            for toyID, toyCount in toysToBreak.iteritems():
                if toyID in self.__seenToys:
                    self.__seenToys[toyID] -= toyCount
                    if self.__seenToys[toyID] <= 0:
                        del self.__seenToys[toyID]

        if not result.success and result.userMsg and result.sysMsgType == SystemMessages.SM_TYPE.Error:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def __onBreakAnimationComplete(self, _):
        self.__updateShardsInfo()
        self.__breakToysAnimation = False

    def __onResetBtnClick(self, _):
        self.__resetFilter()

    def __updateInfoBySelectedItems(self):
        toys = self._itemsCache.items.festivity.getToys()
        selectedItems = self.viewModel.slotsList.getSelectedItems()
        with self.viewModel.transaction() as model:
            expectedShards = 0
            for item in selectedItems:
                toy = toys[item.getToyID()]
                expectedShards += toy.getShards()

            model.setExpectedPartsCount(expectedShards)
            model.setSelectedDecorationsCount(len(selectedItems))

    def __updateShardsCount(self, _=None):
        shardsCount = self._itemsCache.items.festivity.getShardsCount()
        with self.viewModel.transaction() as model:
            model.setPartsCount(shardsCount)
            if self.__craftInfo is not None:
                self.__updateCraftCounters(model, self.__craftInfo.craftCost, shardsCount)
        return

    def __updateShardsInfo(self, _=None):
        self.__updateShardsCount()
        with self.viewModel.transaction() as model:
            model.setExpectedPartsCount(0)
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
                for idx, item in enumerate(items):
                    item.setIdx(idx)

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
