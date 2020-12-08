# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_decorations_popover.py
import random
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NEW_YEAR_POPOVER_VIEWED, NEW_YEAR_POPOVER_BREAKED
from adisp import process
from frameworks.wulf import Array, ViewSettings
from frameworks.wulf.gui_constants import ViewStatus
from gui import SystemMessages
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_popover_decoration_slot_model import NewYearPopoverDecorationSlotModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_decorations_popover_model import NewYearDecorationsPopoverModel
from gui.impl.gui_decorators import trackLifeCycle
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.new_year_helper import formatRomanNumber
from gui.impl.new_year.sounds import NewYearSoundEvents
from gui.impl.new_year.tooltips.toy_content import RegularToyContent
from gui.impl.new_year.views.toy_presenter import PopoverToyPresenter
from gui.impl.pub import PopOverViewImpl
from helpers import dependency, isPlayerAccount
from items.components.ny_constants import ToyTypes, TOY_TYPE_IDS_BY_NAME
from new_year.ny_constants import SyncDataKeys
from new_year.ny_processor import NewYearBreakToysProcessor
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from uilogging.decorators import loggerTarget, loggerEntry, simpleLog
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger
_HANG_SOUNDS_MAP = {ToyTypes.TOP: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.BALL: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.GARLAND: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.FLOOR: NewYearSoundEvents.ADD_TOY_TREE_DOWN,
 ToyTypes.KITCHEN: NewYearSoundEvents.ADD_TOY_KITCHEN_BBQ,
 ToyTypes.TABLE: NewYearSoundEvents.ADD_TOY_KITCHEN_TABLE,
 ToyTypes.TENT: NewYearSoundEvents.ADD_TOY_KITCHEN_TABLE,
 ToyTypes.SCULPTURE: NewYearSoundEvents.ADD_TOY_SNOWTANK,
 ToyTypes.DECORATION: NewYearSoundEvents.ADD_TOY_SNOWTANK_LIGHT,
 ToyTypes.SNOW_ITEM: NewYearSoundEvents.ADD_TOY_SNOWTANK,
 ToyTypes.TREES: NewYearSoundEvents.ADD_TOY_LIGHT,
 ToyTypes.GROUND_LIGHT: NewYearSoundEvents.ADD_TOY_LIGHT_DOWN,
 ToyTypes.PYRO: NewYearSoundEvents.ADD_TOY_LIGHT}
_ANIMATION_DELAY = 0.5
_MIN_COUNT_IN_LIST = 1

@loggerTarget(logKey=NY_LOG_KEYS.NY_DECOR_POPOVER, loggerCls=NYLogger)
@trackLifeCycle('new_year.decoration_popover')
class NewYearDecorationsPopover(NewYearNavigation, PopOverViewImpl):
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _isScopeWatcher = False

    def __init__(self, slotID):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_decorations_popover.NewYearDecorationsPopover())
        settings.model = NewYearDecorationsPopoverModel()
        super(NewYearDecorationsPopover, self).__init__(settings)
        self.__slotID = slotID
        self.__decorationType = self.__getDecorationType()
        toyID = self.__getNewYearRequester().getSlots()[self.__slotID]
        self.__selectedDecoration = self.__getNewYearRequester().getToys().get(toyID)
        self.__slotsForBreak = set()
        self.__breakToysAnimation = False

    @property
    def viewModel(self):
        return super(NewYearDecorationsPopover, self).getViewModel()

    @property
    def isCloseBtnVisible(self):
        return True

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.ny_regular_toy_tooltip_content.NyRegularToyTooltipContent():
            toyID = event.getArgument('toyID')
            return RegularToyContent(toyID)

    @loggerEntry
    def _initialize(self, *args, **kwargs):
        soundConfig = {}
        super(NewYearDecorationsPopover, self)._initialize(soundConfig)
        with self.viewModel.transaction() as tx:
            self.__updateHeader(tx)
            self.__updateSlotsList()
            self.__updateStatus()
        self.viewModel.onBreakBtnClick += self.__onBreakBtnClick
        self.viewModel.slotsList.onSelectionChanged += self.__onSelectionChanged
        self.viewModel.slotsList.onItemClicked += self.__onItemClicked
        self.viewModel.onSlotStatusIsNewChanged += self.__onSlotStatusIsNewChanged
        self.viewModel.onSlotSelectedForBreak += self.__onSlotSelectedForBreak
        self._nyController.onDataUpdated += self.__onDataUpdated
        self.viewModel.onBreakAnimationComplete += self.__onBreakAnimationComplete

    def _finalize(self):
        self.viewModel.onBreakBtnClick -= self.__onBreakBtnClick
        self.viewModel.slotsList.onUserSelectionChanged -= self.__onSelectionChanged
        self.viewModel.slotsList.onItemClicked -= self.__onItemClicked
        self.viewModel.onSlotStatusIsNewChanged -= self.__onSlotStatusIsNewChanged
        self.viewModel.onSlotSelectedForBreak -= self.__onSlotSelectedForBreak
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self.viewModel.onBreakAnimationComplete -= self.__onBreakAnimationComplete
        if isPlayerAccount():
            self.__sendSeenToys()
        super(NewYearDecorationsPopover, self)._finalize()

    def __updateSlotsList(self):
        toys = [ toy for toy in self._nyController.getToysByType(self.__decorationType) if toy.getCount() > 0 ]
        slots = self.viewModel.slotsList
        selectedToyID = self.__selectedDecoration.getID() if self.__selectedDecoration is not None else None
        curRank = 0
        if selectedToyID:
            slotViewModel = PopoverToyPresenter(self.__selectedDecoration).asSlotViewModel()
            slotViewModel.setCount(slotViewModel.getCount() + 1)
            slots.addViewModel(slotViewModel, isSelected=True)
            curRank = self.__selectedDecoration.getRank()
        for toyDescriptor in toys:
            if toyDescriptor.getID() != selectedToyID:
                slots.addViewModel(PopoverToyPresenter(toyDescriptor, curRank).asSlotViewModel())

        buttonSlot = NewYearPopoverDecorationSlotModel()
        buttonSlot.setIsButton(True)
        slots.addViewModel(buttonSlot)
        slots.invalidate()
        return

    def __updateStatus(self):
        toysCount = self.viewModel.slotsList.getItemsLength()
        if toysCount == _MIN_COUNT_IN_LIST and not AccountSettings.getUIFlag(NEW_YEAR_POPOVER_VIEWED):
            self.viewModel.setState(NewYearDecorationsPopoverModel.INFO_GET_STATE)
            AccountSettings.setUIFlag(NEW_YEAR_POPOVER_VIEWED, True)
        elif not toysCount == _MIN_COUNT_IN_LIST and not AccountSettings.getUIFlag(NEW_YEAR_POPOVER_BREAKED):
            self.viewModel.setState(NewYearDecorationsPopoverModel.INFO_BREAK_STATE)
        else:
            self.__updateBreakSatus()

    def __updateBreakSatus(self):
        toysCount = self.viewModel.slotsList.getItemsLength()
        if toysCount == _MIN_COUNT_IN_LIST:
            self.viewModel.setState(NewYearDecorationsPopoverModel.EMPTY_STATE)
        else:
            self.viewModel.setState(NewYearDecorationsPopoverModel.BREAK_STATE)

    def __removeBrokenSlots(self):
        with self.viewModel.transaction() as model:
            removeIndices = Array()
            for idx in self.__slotsForBreak:
                removeIndices.addNumber(idx)

            model.slotsList.removeItemByIndexes(removeIndices)
            model.slotsList.invalidate()
            model.setEnabledBreakBtn(False)
            model.setExpectedShardsCount(0)
        self.__slotsForBreak.clear()

    def __getDecorationType(self):
        return self._nyController.getSlotDescrs()[self.__slotID].type

    def __getNewYearRequester(self):
        return self._itemsCache.items.festivity

    @process
    def __onSelectionChanged(self, args):
        selectedItemIdx = args['selectedIndex']
        if selectedItemIdx is not None:
            selectedItem = self.viewModel.slotsList.getItem(selectedItemIdx)
            if selectedItem.getIsButton():
                return
        else:
            selectedItem = None
        if selectedItem:
            toyID = selectedItem.getToyID()
            toy = self.__getNewYearRequester().getToys().get(toyID)
        else:
            toyID = -1
            toy = None
        result = yield self._nyController.hangToy(toyID, self.__slotID)
        if result.success and self.viewStatus == ViewStatus.LOADED:
            self.__selectedDecoration = toy
            if selectedItem:
                if self.__decorationType in _HANG_SOUNDS_MAP:
                    self._newYearSounds.playEvent(_HANG_SOUNDS_MAP[self.__decorationType])
                    if self.__decorationType in ToyTypes.MEGA:
                        self._newYearSounds.playEvent(_HANG_SOUNDS_MAP[ToyTypes.MEGA])
                self.destroyWindow()
            else:
                with self.viewModel.transaction() as tx:
                    self.__updateHeader(tx, selectedItem)
        elif not result.success:
            self.destroyWindow()
        return

    def __onItemClicked(self, args):
        slot = self.viewModel.slotsList.getItem(args.get('index'))
        if slot.getIsButton():
            toyTypeID = TOY_TYPE_IDS_BY_NAME[self.__decorationType]
            self._goToCraftView(toyTypeID=toyTypeID)

    def __updateHeader(self, tx, slotItem=None):
        if self.__selectedDecoration or slotItem is not None:
            if slotItem:
                title = slotItem.getTitle()
            else:
                title = PopoverToyPresenter(self.__selectedDecoration).title
            setting = R.strings.ny.settings.dyn(self.__selectedDecoration.getSetting())()
            rank = formatRomanNumber(self.__selectedDecoration.getRank())
        else:
            title = R.strings.ny.decorationTypes.dyn(self.__decorationType)()
            setting = R.invalid()
            rank = ''
        tx.setTitle(title)
        tx.setSetting(setting)
        iconType = ToyTypes.MEGA_COMMON if self.__decorationType in ToyTypes.MEGA else self.__decorationType
        tx.setDecorationTypeIcon(R.images.gui.maps.icons.new_year.decorationTypes.blue.dyn(iconType)())
        tx.setRank(rank)
        return

    @process
    def __onBreakBtnClick(self, *_):
        self.__breakToysAnimation = True
        toysToBreak = {}
        for idx in self.__slotsForBreak:
            slot = self.viewModel.slotsList.getItem(idx)
            toysToBreak[slot.getToyID()] = slot.getCount()

        result = yield NewYearBreakToysProcessor(toysToBreak, self.viewModel.getExpectedShardsCount(), False).request()
        if not result.success and result.userMsg and result.sysMsgType == SystemMessages.SM_TYPE.Error:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        AccountSettings.setUIFlag(NEW_YEAR_POPOVER_BREAKED, True)

    def __onSlotStatusIsNewChanged(self, args):
        slot = self.viewModel.slotsList.getItem(args.get('idx'))
        slot.setIsNew(False)

    @simpleLog(action=NY_LOG_ACTIONS.NY_DECOR_POPOVER_SELECT_FOR_BREAK)
    def __onSlotSelectedForBreak(self, args):
        idx = int(args.get('idx'))
        with self.viewModel.transaction() as model:
            slot = model.slotsList.getItem(idx)
            toy = self.__getNewYearRequester().getToys()[slot.getToyID()]
            toyCost = toy.getShards() * toy.getCount()
            if idx in self.__slotsForBreak:
                self.__slotsForBreak.remove(idx)
                model.setExpectedShardsCount(self.viewModel.getExpectedShardsCount() - toyCost)
            else:
                self.__slotsForBreak.add(idx)
                model.setExpectedShardsCount(self.viewModel.getExpectedShardsCount() + toyCost)
            slot.setSelectedForBreak(idx in self.__slotsForBreak)
            model.setEnabledBreakBtn(bool(self.__slotsForBreak))
            self.__updateBreakSatus()

    def __sendSeenToys(self):
        serverFormatted = []
        inventoryToys = self.__getNewYearRequester().getToys()
        for toyID, toyInfo in inventoryToys.iteritems():
            if toyInfo.getToyType() == self.__decorationType and toyInfo.getCount() > 0:
                serverFormatted.append(toyID)
                serverFormatted.append(toyInfo.getUnseenCount())

        self._nyController.sendSeenToys(serverFormatted)

    def __onDataUpdated(self, keys):
        fragmentsChanged = SyncDataKeys.TOY_FRAGMENTS in keys
        toysChanged = SyncDataKeys.INVENTORY_TOYS in keys
        if fragmentsChanged and toysChanged and self.__breakToysAnimation:
            with self.viewModel.transaction() as model:
                for idx in self.__slotsForBreak:
                    item = model.slotsList.getItem(idx)
                    item.setBreakDuration(random.random() * _ANIMATION_DELAY)

            if self.viewModel.getTotalRegisterDecorations() == 0:
                self.__breakToysAnimation = False
                self.__removeBrokenSlots()
                self.__updateBreakSatus()

    def __isSelected(self, item):
        return self.__selectedDecoration.getID() == item.getToyID()

    def __onBreakAnimationComplete(self):
        self.__breakToysAnimation = False
        self.__removeBrokenSlots()
        self.__updateBreakSatus()
        slots = self.viewModel.slotsList
        if self.__selectedDecoration is not None:
            for index in slots.findIndices(self.__isSelected):
                slots.addSelectedIndex(index)

        slots.invalidateSelectedIndices()
        self.viewModel.setCurrentBreakDecorations(0)
        self.viewModel.setTotalRegisterDecorations(0)
        return
