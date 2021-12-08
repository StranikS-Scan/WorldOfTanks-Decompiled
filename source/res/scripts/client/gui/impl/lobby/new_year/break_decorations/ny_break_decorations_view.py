# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/break_decorations/ny_break_decorations_view.py
from collections import namedtuple, defaultdict
import typing
import json
from PlayerEvents import g_playerEvents
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.break_decorations.ny_break_decorations_view_model import NyBreakDecorationsViewModel, ShowState
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.impl.lobby.new_year.break_decorations.ny_break_shards_tip import CraftTip
from gui.impl.lobby.new_year.popovers.ny_break_filter_popover import NyBreakFilterPopoverView
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.lobby.new_year.tooltips.ny_decoration_state_tooltip import NyDecorationStateTooltip
from gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from gui.impl.lobby.new_year.tooltips.ny_mega_decoration_tooltip import NyMegaDecorationTooltip
from gui.impl.lobby.new_year.tooltips.ny_shards_tooltip import NyShardsTooltip
from gui.impl.new_year.navigation import NewYearNavigation
from gui.server_events import events_dispatcher as se_events
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.utils import decorators
from new_year.ny_constants import SyncDataKeys, AnchorNames
from new_year.ny_processor import NewYearBreakToysProcessor
if typing.TYPE_CHECKING:
    from gui.impl.lobby.new_year.break_decorations.ny_break_shards_tip import BaseShardsTip
_FilteredToysInfo = namedtuple('_FilteredToysInfo', ('toys', 'unseenToys', 'toyCount', 'totalToyCount'))
SelectedToyFilters = namedtuple('SelectedToyFilters', ('toyTypes', 'collectionTypes', 'atmosphereBonuses'))
_ANIMATION_DELAY = 0.5
_SlotInfo = typing.NamedTuple('_SlotInfo', [('id', int), ('hasPure', bool)])

class NyBreakDecorationsView(HistorySubModelPresenter):
    __slots__ = ('__selectedToyFilters', '__seenToys', '__accountIsNonPlayer', '__isBreakToysProcess', '__shardsTip', '__toySlots', '__selectedIndicesSlots')

    def __init__(self, viewModel, parentView, *args, **kwargs):
        super(NyBreakDecorationsView, self).__init__(viewModel, parentView, *args, **kwargs)
        self.__selectedToyFilters = SelectedToyFilters(tuple(), tuple(), tuple())
        self.__seenToys = defaultdict(int)
        self.__accountIsNonPlayer = False
        self.__isBreakToysProcess = False
        self.__shardsTip = None
        self.__toySlots = []
        self.__selectedIndicesSlots = []
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyDecorationTooltip():
            return NyDecorationTooltip(event.getArgument('toyID'), isPureToy=event.getArgument('isPure'))
        if contentID == R.views.lobby.new_year.tooltips.NyMegaDecorationTooltip():
            return NyMegaDecorationTooltip(event.getArgument('toyID'), isPureToy=event.getArgument('isPure'))
        if contentID == R.views.lobby.new_year.tooltips.NyShardsTooltip():
            return NyShardsTooltip()
        return NyDecorationStateTooltip(event.getArgument('atmosphereBonus')) if contentID == R.views.lobby.new_year.tooltips.NyDecorationStateTooltip() else super(NyBreakDecorationsView, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        return NyBreakFilterPopoverView(self.__selectedToyFilters) if event.contentID == R.views.lobby.new_year.popovers.NyBreakFilterPopover() else super(NyBreakDecorationsView, self).createPopOverContent(event)

    def initialize(self, *args, **kwargs):
        super(NyBreakDecorationsView, self).initialize()
        self.__shardsTip = CraftTip(self.viewModel.shardsTip)
        with self.viewModel.transaction() as model:
            self.__updateShardsCount(model)
            self.__updateSlots(model, initSelected=True)
            self.__updateInfoBySelectedItems(model)

    def finalize(self):
        with self.viewModel.transaction() as model:
            model.setDecorationsJSON('')
            model.setSelectedIndicesJSON('')
        self.__markToysAsSeen()
        if self.__isBreakToysProcess:
            self.viewModel.setIsBreakInitiated(False)
            self.__isBreakToysProcess = False
        super(NyBreakDecorationsView, self).finalize()

    def _getEvents(self):
        return ((self._nyController.onDataUpdated, self.__onDataUpdated),
         (g_playerEvents.onAccountBecomeNonPlayer, self.__onAccountBecomeNonPlayer),
         (self.viewModel.onSelectedAllChanged, self.__onSelectedAllChanged),
         (self.viewModel.onSlotStatusIsNewChanged, self.__onSlotStatusIsNewChanged),
         (self.viewModel.onBreakDecorationsBtnClick, self.__onBreakDecorationsBtnClick),
         (self.viewModel.onBreakAnimationComplete, self.__onBreakAnimationComplete),
         (self.viewModel.filterCounter.onResetBtnClick, self.__onFilterReset),
         (self.viewModel.onDecorationClicked, self.__onDecorationClicked),
         (self.viewModel.onQuestsBtnClick, self.__onQuestsBtnClick),
         (self.viewModel.onCelebrityBtnClick, self.__onCelebrityBtnClick))

    def _getListeners(self):
        return ((events.NewYearEvent.ON_BREAK_TOYS_FILTER_APPLIED, self.__onFilterAppliedEvent, EVENT_BUS_SCOPE.LOBBY),)

    def _getInfoForHistory(self):
        return {'selectedToyFilters': self.__selectedToyFilters}

    def _restoreState(self, stateInfo):
        self.__selectedToyFilters = stateInfo['selectedToyFilters']

    @property
    def __isFilterApplied(self):
        return any(self.__selectedToyFilters)

    @classmethod
    def __keyFunc(cls, toyInfo):
        toy = toyInfo[0]
        atmosphere = max(toy.getAtmosphere(isToyPure=toy.getPureCount() > 0, isSlotPure=cls._nyController.hasPureSlotForToy(toy)), 0)
        priority = toy.getSortPriority()
        return (-atmosphere, priority)

    def __updateSlots(self, model, initSelected=False):
        filteredToysInfo = self.__filterToys()
        self.__updateFilterCounters(model, filteredToysInfo, self.__isFilterApplied)
        newShowState = self.__updateShowToysState(model, filteredToysInfo)
        if newShowState != ShowState.TOYS_VISIBLE:
            self.__toySlots = []
            self.__invalidateToySlots()
            return
        filteredToysInfo.toys.sort(key=self.__keyFunc)
        unseenToys = filteredToysInfo.unseenToys
        for toyId, seenCount in self.__seenToys.iteritems():
            if toyId in unseenToys:
                unseenToys[toyId] -= seenCount

        pureSlotInfoByTypeMap = self.__getPureSlotInfoByTypeMap()
        pureSlots = self._itemsCache.items.festivity.getPureSlots()
        self.__selectedIndicesSlots = []
        self.__toySlots = []
        for toy, idx in filteredToysInfo.toys:
            pureSlotByTypeID = pureSlotInfoByTypeMap[toy.getToyType()].id
            toySlot = self.__toyToToySlot(pureSlots, toy, pureSlotByTypeID, idx < toy.getPureCount())
            toyId = toySlot['toyID']
            if toyId in unseenToys and unseenToys[toyId] > 0:
                toySlot['isNew'] = True
                unseenToys[toyId] -= 1
            self.__toySlots.append(toySlot)
            if initSelected:
                self.__selectedIndicesSlots.append(len(self.__toySlots) - 1)

        model.setIsAllSelected(initSelected)
        self.__invalidateToySlots()
        self.__invalidateSelectedIndices()

    def __filterToys(self, countersOnly=False):
        toys = self._itemsCache.items.festivity.getToys()
        filteredToys = []
        unseenToys = defaultdict(int)
        if not toys:
            return _FilteredToysInfo(filteredToys, 0, 0, 0)
        filterToyTypes = self.__selectedToyFilters.toyTypes
        filterCollections = self.__selectedToyFilters.collectionTypes
        filterAtmosphereBonuses = self.__selectedToyFilters.atmosphereBonuses
        pureSlotInfoByTypeMap = self.__getPureSlotInfoByTypeMap()
        totalToyCount = 0
        filteredToyCount = 0
        for toy in toys.itervalues():
            totalToyCount += toy.getCount()
            if filterCollections and toy.getCollectionName() not in filterCollections:
                continue
            if filterToyTypes and toy.getToyType() not in filterToyTypes:
                continue
            unseenToys[toy.getID()] = toy.getUnseenCount()
            for idx in xrange(toy.getCount()):
                if filterAtmosphereBonuses:
                    atmosphere = max(toy.getAtmosphere(isToyPure=idx < toy.getPureCount(), isSlotPure=pureSlotInfoByTypeMap[toy.getToyType()].hasPure), 0)
                    if atmosphere not in filterAtmosphereBonuses:
                        continue
                if not countersOnly:
                    filteredToys.append((toy, idx))
                filteredToyCount += 1

        return _FilteredToysInfo(filteredToys, unseenToys, filteredToyCount, totalToyCount)

    @staticmethod
    def __updateFilterCounters(viewModel, filteredToysInfo, isFilterApplied=True):
        viewModel.filterCounter.setCurrentCount(filteredToysInfo.toyCount)
        viewModel.filterCounter.setTotalCount(filteredToysInfo.totalToyCount)
        viewModel.filterCounter.setIsFilterApplied(isFilterApplied)

    @staticmethod
    def __updateShowToysState(model, filteredToysInfo):
        newState = ShowState.TOYS_VISIBLE
        if filteredToysInfo.totalToyCount == 0:
            newState = ShowState.TOYS_EMPTY
        elif filteredToysInfo.toyCount == 0:
            newState = ShowState.TOYS_NOT_FOUND
        model.setShowState(newState)
        return newState

    def __onDecorationClicked(self, args):
        selectedIndex = int(args.get('index'))
        with self.viewModel.transaction() as model:
            if selectedIndex in self.__selectedIndicesSlots:
                self.__selectedIndicesSlots.remove(selectedIndex)
            else:
                self.__selectedIndicesSlots.append(selectedIndex)
            model.setSelectedIndicesJSON(json.dumps(self.__selectedIndicesSlots))
            self.__onSelectionChanged(model)

    def __onSelectionChanged(self, model):
        self.__updateInfoBySelectedItems(model)
        isAllItemsSelected = len(self.__selectedIndicesSlots) == len(self.__toySlots)
        if isAllItemsSelected != model.getIsAllSelected():
            model.setIsAllSelected(isAllItemsSelected)

    def __onSelectedAllChanged(self):
        with self.viewModel.transaction() as model:
            isAllSelected = not model.getIsAllSelected()
            model.setIsAllSelected(isAllSelected)
            self.__selectedIndicesSlots = []
            if isAllSelected:
                for index, _ in enumerate(self.__toySlots):
                    self.__selectedIndicesSlots.append(index)

            self.__invalidateSelectedIndices()
            self.__updateInfoBySelectedItems(model)

    def __onSlotStatusIsNewChanged(self, args):
        index = int(args.get('index'))
        if index < len(self.__toySlots):
            toySlot = self.__toySlots[index]
            toySlot['isNew'] = False
            self.__seenToys[toySlot['toyID']] += 1
            self.__invalidateToySlots()

    @decorators.process('newYear/breakDecorationsWaiting')
    def __onBreakDecorationsBtnClick(self):
        self.__isBreakToysProcess = True
        toysToBreak = {}
        for selectedIndex in self.__selectedIndicesSlots:
            toySlot = self.__toySlots[selectedIndex]
            toyID = toySlot['toyID']
            toysToBreak.setdefault(toyID, [0, 0])[0] += 1
            if toySlot['isPure']:
                toysToBreak[toyID][1] += 1

        result = yield NewYearBreakToysProcessor(toysToBreak=toysToBreak, expectedShardsCount=self.viewModel.getExpectedShardsCount(), parent=self, needConfirm=True).request()
        if result.success and self.isLoaded:
            for toyID, countData in toysToBreak.iteritems():
                if toyID in self.__seenToys:
                    self.__seenToys[toyID] -= countData[0]
                    if self.__seenToys[toyID] <= 0:
                        del self.__seenToys[toyID]

        if not result.success and result.userMsg and result.sysMsgType == SystemMessages.SM_TYPE.Error:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)

    def __onBreakAnimationComplete(self, _=None):
        self.__isBreakToysProcess = False
        with self.viewModel.transaction() as model:
            self.__updateShardsCount(model)
            self.__clearSelectedItems(model)
            filteredToysInfo = self.__filterToys(countersOnly=True)
            self.__updateFilterCounters(model, filteredToysInfo, self.__isFilterApplied)
            self.__updateShowToysState(model, filteredToysInfo)
            model.setIsBreakInitiated(False)
            g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.ON_BREAK_TOYS_ANIMATION_COMPLETED, ctx={'totalToyCount': filteredToysInfo.totalToyCount}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onDataUpdated(self, keys):
        fragmentsChanged = SyncDataKeys.TOY_FRAGMENTS in keys
        toysChanged = SyncDataKeys.INVENTORY_TOYS in keys
        with self.viewModel.transaction() as model:
            if fragmentsChanged and toysChanged and self.__isBreakToysProcess:
                model.setIsBreakInitiated(True)
                self.__clearExpectedShards(model)
                return
            if fragmentsChanged:
                self.__updateShardsCount(model)
            if toysChanged:
                self.__shardsTip.update(model.shardsTip)
                self.__updateSlots(model)

    def __updateInfoBySelectedItems(self, model):
        toys = self._itemsCache.items.festivity.getToys()
        expectedShards = 0
        for selectedIndex in self.__selectedIndicesSlots:
            toySlot = self.__toySlots[selectedIndex]
            toyID = toySlot['toyID']
            toy = toys[toyID]
            expectedShards += toy.getShards()

        model.setExpectedShardsCount(expectedShards)
        model.setSelectedDecorationsCount(len(self.__selectedIndicesSlots))

    def __updateShardsCount(self, model):
        shardsCount = self._itemsCache.items.festivity.getShardsCount()
        model.setShardsCount(shardsCount)
        self.__shardsTip.setShardsCount(shardsCount)
        self.__shardsTip.update(model.shardsTip)

    def __clearSelectedItems(self, model):
        isAllSelected = self.viewModel.getIsAllSelected()
        if isAllSelected:
            self.__toySlots = []
            self.viewModel.setIsAllSelected(False)
        else:
            self.__toySlots = [ e for i, e in enumerate(self.__toySlots) if i not in self.__selectedIndicesSlots ]
        self.__selectedIndicesSlots = []
        self.__invalidateSelectedIndices()
        self.__invalidateToySlots()

    def __clearExpectedShards(self, model):
        model.setExpectedShardsCount(0)
        model.setSelectedDecorationsCount(0)

    def __onFilterAppliedEvent(self, event):
        ctx = event.ctx
        self.__selectedToyFilters = SelectedToyFilters(ctx['toyTypes'], ctx['collectionTypes'], ctx['atmosphereBonuses'])
        with self.viewModel.transaction() as model:
            self.__updateSlots(model)
            self.__clearExpectedShards(model)

    def __onFilterReset(self):
        self.__selectedToyFilters = SelectedToyFilters(tuple(), tuple(), tuple())
        with self.viewModel.transaction() as model:
            self.__updateSlots(model)
            self.__clearExpectedShards(model)
            model.filterCounter.setIsFilterApplied(False)

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

    def __onQuestsBtnClick(self):
        se_events.showDailyQuests(subTab=DailyTabs.QUESTS)

    def __onCelebrityBtnClick(self):
        NewYearNavigation.switchByAnchorName(AnchorNames.CELEBRITY)

    def __getPureSlotInfoByTypeMap(self):
        pureSlotsIds = self._itemsCache.items.festivity.getPureSlots()
        result = {}
        for slot in self._nyController.getSlotDescrs():
            if slot.type in result and result[slot.type].hasPure:
                continue
            result[slot.type] = _SlotInfo(slot.id, slot.id in pureSlotsIds)

        return result

    def __toyToToySlot(self, pureSlots, toy, slotId=None, isPureToy=False):
        if slotId is not None:
            isPureSlot = slotId in pureSlots
        else:
            isPureSlot = self._nyController.hasPureSlotForToy(toy)
        toySlot = {'toyID': toy.getID(),
         'title': toy.getName(),
         'description': toy.getDesc(),
         'setting': toy.getSetting(),
         'imageName': toy.getIconName(),
         'rankIcon': toy.getRankIcon(),
         'isMega': toy.isMega(),
         'isNew': False,
         'isPure': isPureToy,
         'atmosphereBonus': toy.getAtmosphere(isPureToy, isPureSlot)}
        return toySlot

    def __invalidateToySlots(self):
        self.viewModel.setDecorationsJSON(json.dumps(self.__toySlots))

    def __invalidateSelectedIndices(self):
        self.viewModel.setSelectedIndicesJSON(json.dumps(self.__selectedIndicesSlots))
