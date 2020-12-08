# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_break_decorations_view.py
import random
from collections import namedtuple, defaultdict
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewStatus
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_break_decorations_view_model import NewYearBreakDecorationsViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_parts_tip_element_model import NewYearPartsTipElementModel
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.impl.new_year.tooltips.toy_content import RegularToyContent, MegaToyContent
from gui.impl.new_year.views.new_year_break_filter_popover import NewYearBreakFilterPopover
from gui.impl.new_year.views.toy_presenter import BreakToyPresenter
from gui.server_events import events_dispatcher as se_events
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.utils import decorators
from helpers import dependency, uniprof
from new_year.craft_machine import MegaDeviceState
from new_year.ny_constants import SyncDataKeys, AnchorNames
from new_year.ny_processor import NewYearBreakToysProcessor
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import ICustomizableObjectsManager, INewYearController, INewYearCraftMachineController
_FilteredToysInfo = namedtuple('_FilteredToysInfo', ('toys', 'unseenToys', 'toyCount', 'totalToyCount'))
_ToysInfo = namedtuple('_ToysInfo', ('toyTypes', 'toyRanks'))
_ANIMATION_DELAY = 0.5

class BaseShardsTip(object):

    def __init__(self, tipsModel):
        super(BaseShardsTip, self).__init__()
        self._shardsCount = 0

    def setShardsCount(self, count):
        self._shardsCount = count

    def update(self, model):
        raise NotImplementedError

    @staticmethod
    def _updateModel(icon, shardsShortage, state, model):
        model.setDecorationTypeIcon(icon)
        model.setCurrentState(state)
        model.setShardsCountLeft(shardsShortage)


class CraftTip(BaseShardsTip):
    _craftCtrl = dependency.descriptor(INewYearCraftMachineController)

    def update(self, model):
        craftCost = self._craftCtrl.calculateSelectedToyCraftCost()
        megaDeviceState = self._craftCtrl.getActualMegaDeviceState()
        desiredToyType = self._craftCtrl.getSelectedToyType()
        shardsShortage = max(craftCost - self._shardsCount, 0)
        if megaDeviceState == MegaDeviceState.ALL_MEGA_TOYS_COLLECTED_ERROR:
            state = NewYearPartsTipElementModel.SHARDS_ALL_MEGA_TOYS_COLLECTED
        elif shardsShortage == 0:
            state = NewYearPartsTipElementModel.SHARDS_ENOUGH_TO_CREATE
        else:
            state = NewYearPartsTipElementModel.SHARDS_NOT_ENOUGH_TO_CREATE
        self._updateModel(icon=R.images.gui.maps.icons.new_year.decorationTypes.blue.dyn(desiredToyType)(), shardsShortage=shardsShortage, state=state, model=model)


class UpgradeTip(BaseShardsTip):

    def __init__(self, tipsModel, upgradeCost):
        self.__upgradeCost = upgradeCost
        super(UpgradeTip, self).__init__(tipsModel)

    def update(self, model):
        shardsShortage = max(self.__upgradeCost - self._shardsCount, 0)
        if shardsShortage == 0:
            state = NewYearPartsTipElementModel.SHARDS_ENOUGH_TO_UPGRADE
        else:
            state = NewYearPartsTipElementModel.SHARDS_NOT_ENOUGH_TO_UPGRADE
        self._updateModel(icon=R.images.gui.maps.icons.new_year.break_decorations_view.upgradeTip(), shardsShortage=shardsShortage, state=state, model=model)


class NewYearBreakDecorationsView(NewYearHistoryNavigation):
    _itemsCache = dependency.descriptor(IItemsCache)
    _customizableObjMgr = dependency.descriptor(ICustomizableObjectsManager)
    _nyController = dependency.descriptor(INewYearController)
    _craftCtrl = dependency.descriptor(INewYearCraftMachineController)
    __slots__ = ('__toysInfo', '__seenToys', '__ignoreSelectedAllEvents', '__accountIsNonPlayer', '__breakToysAnimation', '__shardsTip')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_break_decorations_view.NewYearBreakDecorationsView())
        settings.model = NewYearBreakDecorationsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NewYearBreakDecorationsView, self).__init__(settings)
        self.__toysInfo = _ToysInfo(None, None)
        self.__ignoreSelectedAllEvents = False
        self.__seenToys = defaultdict(int)
        self.__accountIsNonPlayer = False
        self.__breakToysAnimation = False
        self.__shardsTip = None
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

    @uniprof.regionDecorator(label='ny.shards', scope='enter')
    def _initialize(self, *args, **kwargs):
        super(NewYearBreakDecorationsView, self)._initialize()
        self.viewModel.onQuestsBtnClick += self.__onQuestsBtnClick
        self.viewModel.onCelebrityBtnClick += self.__onCelebrityBtnClick
        self.viewModel.onFilterResetBtnClick += self.__onFilterResetBtnClick
        self.viewModel.onSelectedAllChanged += self.__onSelectedAllChanged
        self.viewModel.onViewResized += self.__onViewResized
        self.viewModel.onSlotStatusIsNewChanged += self.__onSlotStatusIsNewChanged
        self.viewModel.onBreakDecorationsBtnClick += self.__onBreakDecorationsBtnClick
        self.viewModel.filterCounter.onResetBtnClick += self.__onResetBtnClick
        self.viewModel.onBreakAnimationComplete += self.__onBreakAnimationComplete
        self.viewModel.onBackBtnClick += self.__onBackToTalismans
        self._nyController.onDataUpdated += self.__onDataUpdated
        g_playerEvents.onAccountBecomeNonPlayer += self.__onAccountBecomeNonPlayer
        g_eventBus.addListener(events.NewYearEvent.ON_BREAK_TOYS_FILTER_APPLIED, self.__onFilterAppliedEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.slotsList.onSelectionChanged += self.__onSelectionChanged
        upgradeCost = kwargs.get('giftUpgradeCost', 0)
        useGiftUpgradeTip = upgradeCost > 0
        if useGiftUpgradeTip:
            self.__shardsTip = UpgradeTip(self.viewModel.shardsTip, upgradeCost)
        else:
            self.__shardsTip = CraftTip(self.viewModel.shardsTip)
        with self.viewModel.transaction() as model:
            shardsCount = self._itemsCache.items.festivity.getShardsCount()
            model.setShowBackBtn(useGiftUpgradeTip)
            model.setShardsCount(shardsCount)
            model.setDecorationSelectedAll(True)
            self.__shardsTip.setShardsCount(shardsCount)
            self.__shardsTip.update(model.shardsTip)
        self.__updateSlots(initSelected=True)
        self.__updateInfoBySelectedItems()

    @uniprof.regionDecorator(label='ny.shards', scope='exit')
    def _finalize(self):
        g_eventBus.removeListener(events.NewYearEvent.ON_BREAK_TOYS_FILTER_APPLIED, self.__onFilterAppliedEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self.viewModel.onQuestsBtnClick -= self.__onQuestsBtnClick
        self.viewModel.onCelebrityBtnClick -= self.__onCelebrityBtnClick
        self.viewModel.onFilterResetBtnClick -= self.__onFilterResetBtnClick
        self.viewModel.onSelectedAllChanged -= self.__onSelectedAllChanged
        self.viewModel.onViewResized -= self.__onViewResized
        self.viewModel.onSlotStatusIsNewChanged -= self.__onSlotStatusIsNewChanged
        self.viewModel.onBreakDecorationsBtnClick -= self.__onBreakDecorationsBtnClick
        self.viewModel.onBreakAnimationComplete -= self.__onBreakAnimationComplete
        self.viewModel.filterCounter.onResetBtnClick -= self.__onResetBtnClick
        self.viewModel.slotsList.onSelectionChanged -= self.__onSelectionChanged
        self.viewModel.onBackBtnClick -= self.__onBackToTalismans
        g_playerEvents.onAccountBecomeNonPlayer -= self.__onAccountBecomeNonPlayer
        self.__markToysAsSeen()
        super(NewYearBreakDecorationsView, self)._finalize()

    def _getInfoForHistory(self):
        return {'toysInfo': self.__toysInfo}

    def _restoreState(self, stateInfo):
        self.__toysInfo = stateInfo['toysInfo']

    @staticmethod
    def __keyFunc(toy):
        return toy.getSortPriority()

    def __updateSlots(self, initSelected=False):
        with self.viewModel.transaction() as viewModel:
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
            filteredToysInfo.toys.sort(key=self.__keyFunc)
            unseenToys = filteredToysInfo.unseenToys
            for toyId, seenCount in self.__seenToys.iteritems():
                if toyId in unseenToys:
                    unseenToys[toyId] -= seenCount

            for toy in filteredToysInfo.toys:
                slotViewModel = BreakToyPresenter(toy).asSlotViewModel()
                toyId = toy.getID()
                if toyId in unseenToys and unseenToys[toyId] > 0:
                    slotViewModel.setIsNew(True)
                    unseenToys[toyId] -= 1
                slots.addViewModel(slotViewModel, initSelected)

            if needToInvalidateSlots:
                slots.invalidate()
            if not viewModel.getDecorationSelectedAllEnable():
                viewModel.setDecorationSelectedAllEnable(True)
            viewModel.setDecorationSelectedAll(initSelected)

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
        se_events.showDailyQuests(subTab=DailyTabs.QUESTS)

    def __onCelebrityBtnClick(self):
        NewYearNavigation.switchByAnchorName(AnchorNames.CELEBRITY)

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
            self.__shardsTip.setShardsCount(shardsCount)
            self.__shardsTip.update(model.shardsTip)

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
            self.__shardsTip.update(self.viewModel.shardsTip)
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
            self.__updateSlots()

    def __onFilterAppliedEvent(self, event):
        ctx = event.ctx
        self.__toysInfo = _ToysInfo(ctx['toysTypes'], ctx['toysRanks'])
        self.__updateSlots()
        self.__updateShardsInfo()

    def __resetFilter(self):
        self.viewModel.filterCounter.setIsFilterApplied(False)
        self.__toysInfo = _ToysInfo(tuple(), tuple())
        self.__updateSlots()
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

    def __onViewResized(self, event):
        self.viewModel.slotsList.invalidate()

    def __onBackToTalismans(self):
        self.switchToTalismans()
