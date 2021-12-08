# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/popovers/ny_decorations_popover.py
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from adisp import process
from async import async
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_decorations_popover_model import NyDecorationsPopoverModel
from gui.impl.lobby.new_year.dialogs.dialogs import showInstallToUnprofitableSlotConfirm
from gui.impl.lobby.new_year.tooltips.ny_decoration_state_tooltip import NyDecorationStateTooltip
from gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.sounds import NewYearSoundEvents, NewYearSoundsManager
from gui.impl.new_year.views.toy_presenter import PopoverToyPresenter
from gui.impl.pub import PopOverViewImpl
from gui.impl.pub.dialog_window import DialogButtons
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from helpers import dependency, isPlayerAccount
from items.components.ny_constants import ToyTypes, TOY_TYPE_IDS_BY_NAME, RANDOM_VALUE, TOY_SLOT_USAGE, INVALID_TOY_ID
from new_year.ny_constants import SyncDataKeys
from new_year.ny_processor import NewYearBreakToysProcessor
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, INewYearCraftMachineController
from uilogging.ny.loggers import NyDecorationsSlotPopoverFlowLogger
_HANG_SOUNDS_MAP = {ToyTypes.TOP: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.BALL: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.GARLAND_FIR: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.FLOOR: NewYearSoundEvents.ADD_TOY_TREE_DOWN,
 ToyTypes.KITCHEN: NewYearSoundEvents.ADD_TOY_KITCHEN_BBQ,
 ToyTypes.PAVILION: NewYearSoundEvents.ADD_TOY_KITCHEN_TABLE,
 ToyTypes.ATTRACTION: NewYearSoundEvents.ADD_TOY_KITCHEN_ATTRACTION,
 ToyTypes.GARLAND_FAIR: NewYearSoundEvents.ADD_TOY_BIG_GARLANDS,
 ToyTypes.SCULPTURE: NewYearSoundEvents.ADD_TOY_SNOWTANK,
 ToyTypes.SCULPTURE_LIGHT: NewYearSoundEvents.ADD_TOY_SNOWTANK_LIGHT,
 ToyTypes.PYRO: NewYearSoundEvents.ADD_TOY_SNOWTANK_LIGHT,
 ToyTypes.SNOW_ITEM: NewYearSoundEvents.ADD_TOY_SNOWTANK_LIGHT,
 ToyTypes.GARLAND_INSTALLATION: NewYearSoundEvents.ADD_TOY_BIG_GARLANDS}
_ANIMATION_DELAY = 0.5
_MIN_COUNT_IN_LIST = 0

class NyDecorationsPopover(PopOverViewImpl):
    __slots__ = ('__slotID', '__decorationType', '__breakDecorationsProcess', '__selectedDecoration')
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    __craftCtrl = dependency.descriptor(INewYearCraftMachineController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __flowLogger = NyDecorationsSlotPopoverFlowLogger()

    def __init__(self, slotID):
        settings = ViewSettings(R.views.lobby.new_year.popovers.NyDecorationsPopover())
        settings.model = NyDecorationsPopoverModel()
        super(NyDecorationsPopover, self).__init__(settings)
        self.__slotID = slotID
        self.__decorationType = self.__getDecorationType()
        toyID = self.__getNewYearRequester().getSlots()[self.__slotID]
        self.__selectedDecoration = self.__getNewYearRequester().getToys().get(toyID)
        self.__breakDecorationsProcess = False

    @property
    def viewModel(self):
        return super(NyDecorationsPopover, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        toyID = event.getArgument('toyID')
        if contentID == R.views.lobby.new_year.tooltips.NyDecorationTooltip():
            return NyDecorationTooltip(toyID, isCountEnabled=True, isPureToy=event.getArgument('isPure'))
        return NyDecorationStateTooltip(event.getArgument('atmosphereBonus')) if contentID == R.views.lobby.new_year.tooltips.NyDecorationStateTooltip() else super(NyDecorationsPopover, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as model:
            self.__updateHeader(model)
            model.setDecorationType(self.__decorationType)
            self.__fillSlots(model)
            self.__updateStatus(model, isInitialUpdate=True)

    def _initialize(self, *args, **kwargs):
        super(NyDecorationsPopover, self)._initialize(*args, **kwargs)
        self.viewModel.onApplySelection += self.__onApplySelection
        self.viewModel.onBreakSelection += self.__onBreakSelection
        self.viewModel.onIsNewStateChanged += self.__onIsNewStateChanged
        self.viewModel.onBreakBtnClick += self.__onBreakBtnClick
        self.viewModel.onNeedMoreClick += self.__onNeedMoreClick
        self._nyController.onDataUpdated += self.__onDataUpdated
        self.viewModel.onBreakAnimationComplete += self.__onBreakAnimationComplete
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.HAS_TOYS_HINT_SHOWN: True})

    def _finalize(self):
        self.viewModel.onApplySelection -= self.__onApplySelection
        self.viewModel.onBreakSelection -= self.__onBreakSelection
        self.viewModel.onIsNewStateChanged -= self.__onIsNewStateChanged
        self.viewModel.onBreakBtnClick -= self.__onBreakBtnClick
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self.viewModel.onBreakAnimationComplete -= self.__onBreakAnimationComplete
        if isPlayerAccount():
            self.__sendSeenToys()
        super(NyDecorationsPopover, self)._finalize()

    def __updateHeader(self, model, slotItem=None):
        title = R.strings.ny.decorationTypes.dyn(self.__decorationType)()
        setting = R.invalid()
        if self.__selectedDecoration or slotItem is not None:
            if slotItem:
                title = slotItem.getTitle()
            else:
                title = PopoverToyPresenter(self.__selectedDecoration, slotId=self.__slotID).title
            setting = R.strings.ny.settings.dyn(self.__selectedDecoration.getSetting())()
        decorationTypeIcon = R.images.gui.maps.icons.newYear.decoration_types.craft.dyn(self.__decorationType)()
        model.setTitle(title)
        model.setSetting(setting)
        model.setDecorationTypeIcon(decorationTypeIcon)
        return

    def __fillSlots(self, model):
        slots = model.getSlots()
        if self.__selectedDecoration is not None:
            slot = PopoverToyPresenter(self.__selectedDecoration, isPureToy=False, slotId=self.__slotID).asSlotViewModel()
            slot.setCount(1)
            slot.setIsNew(False)
            slots.addViewModel(slot)
            model.getAppliedSelections().addNumber(0)
        allToys = self._nyController.getToysByType(self.__decorationType)
        if not self._nyController.isMaxAtmosphereLevel():
            self.__fillSlotsByType(slots, allToys, True)
        self.__fillSlotsByType(slots, allToys)
        slots.invalidate()
        return

    def __fillSlotsByType(self, slots, allToys, isPureToy=False):
        for toyDescriptor in allToys:
            slot = PopoverToyPresenter(toyDescriptor, isPureToy=isPureToy, slotId=self.__slotID).asSlotViewModel()
            if slot.getCount() > 0:
                slots.addViewModel(slot)

    def __updateStatus(self, model, isInitialUpdate=False):
        slotsEmpty = len(self.viewModel.getSlots()) == 0
        if isInitialUpdate and self.__setInfoStatus(model, slotsEmpty):
            return
        if slotsEmpty:
            model.setState(NyDecorationsPopoverModel.EMPTY_STATE)
        else:
            model.setState(NyDecorationsPopoverModel.BREAK_STATE)

    def __setInfoStatus(self, model, isSlotsEmpty):
        nyStorage = self.__settingsCore.serverSettings.getNewYearStorage()
        if isSlotsEmpty and not nyStorage.get(NewYearStorageKeys.DECORATIONS_POPOVER_VIEWED, False):
            model.setState(NyDecorationsPopoverModel.RECEIVE_INFO_STATE)
            self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.DECORATIONS_POPOVER_VIEWED: True})
        elif not isSlotsEmpty and not nyStorage.get(NewYearStorageKeys.DECORATIONS_POPOVER_BROKEN, False):
            model.setState(NyDecorationsPopoverModel.BREAK_INFO_STATE)
        else:
            return False
        return True

    def __getDecorationType(self):
        return self._nyController.getSlotDescrs()[self.__slotID].type

    def __getIsPureSlot(self):
        return self.__slotID in self._itemsCache.items.festivity.getPureSlots()

    def __getNewYearRequester(self):
        return self._itemsCache.items.festivity

    @staticmethod
    def __updateSelection(selectionsModel, selectedIndex):
        selections = [ i for i in selectionsModel ]
        if selectedIndex in selections:
            selectionsModel.remove(selections.index(selectedIndex))
        else:
            selectionsModel.addNumber(selectedIndex)
        selectionsModel.invalidate()

    def __onApplySelection(self, args):
        selectedItemIdx = int(args['index'])
        isAlreadyApplied = selectedItemIdx in self.viewModel.getAppliedSelections()
        with self.viewModel.transaction() as model:
            self.__updateSelection(model.getAppliedSelections(), selectedItemIdx)
        selectedItem = self.viewModel.getSlots().getValue(selectedItemIdx)
        if selectedItem is not None and not isAlreadyApplied:
            toy = self.__getNewYearRequester().getToys().get(selectedItem.getToyID())
            isPureToy = selectedItem.getIsPure()
        else:
            toy = None
            isPureToy = False
        if toy is not None and isPureToy and not self.__getIsPureSlot() and self._nyController.hasPureSlotForToy(toy):
            self.__showInstallUnprofitableSlotDialog(toy)
        else:
            self.__hangToy(toy, self.__slotID, isPureToy)
        return

    @process
    def __hangToy(self, toy, slotID, isPureToy):
        toyID = toy.getID() if toy is not None else INVALID_TOY_ID
        isPureSlot = slotID in self._itemsCache.items.festivity.getPureSlots()
        toyAtmosphere = toy.getAtmosphere(isPureToy, isPureSlot) if toy is not None else 0
        toyUsage = TOY_SLOT_USAGE.PURE if isPureToy else TOY_SLOT_USAGE.USED
        result = yield self._nyController.hangToy(toyID, slotID, toyUsage)
        if result.success:
            g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.ON_TOY_INSTALLED, ctx={'toyID': toyID,
             'slotID': slotID,
             'atmoshereBonus': toyAtmosphere}), scope=EVENT_BUS_SCOPE.LOBBY)
            if toy is not None:
                self.__playHangDecorationSound()
        self.destroyWindow()
        return

    @async
    def __showInstallUnprofitableSlotDialog(self, toy):
        result = yield showInstallToUnprofitableSlotConfirm()
        if result.result == DialogButtons.SUBMIT:
            slotID = self._nyController.getPureSlotForToy(toy)
            self.__hangToy(toy, slotID, True)
        elif result.result == DialogButtons.INSTALL:
            self.__hangToy(toy, self.__slotID, True)
        elif result.result == DialogButtons.CANCEL:
            self.viewModel.getAppliedSelections().clear()

    def __playHangDecorationSound(self):
        if self.__decorationType in _HANG_SOUNDS_MAP:
            NewYearSoundsManager.playEvent(_HANG_SOUNDS_MAP[self.__decorationType])

    def __onBreakSelection(self, args):
        selectedIndex = int(args.get('index'))
        with self.viewModel.transaction() as model:
            slot = model.getSlots().getValue(selectedIndex)
            toy = self.__getNewYearRequester().getToys()[slot.getToyID()]
            toyCost = toy.getShards() * slot.getCount()
            if selectedIndex in self.viewModel.getBreakSelections():
                model.setExpectedShardsCount(self.viewModel.getExpectedShardsCount() - toyCost)
            else:
                model.setExpectedShardsCount(self.viewModel.getExpectedShardsCount() + toyCost)
            self.__updateSelection(model.getBreakSelections(), selectedIndex)
            self.__updateStatus(model)

    @process
    def __onBreakBtnClick(self, *_):
        if self.__breakDecorationsProcess:
            return
        toysToBreak = {}
        for idx in self.viewModel.getBreakSelections():
            slot = self.viewModel.getSlots().getValue(idx)
            toysToBreak.setdefault(slot.getToyID(), [0, 0])[0] += slot.getCount()
            if slot.getIsPure():
                toysToBreak[slot.getToyID()][1] += slot.getCount()

        self.__breakDecorationsProcess = True
        result = yield NewYearBreakToysProcessor(toysToBreak, self.viewModel.getExpectedShardsCount(), False).request()
        if not result.success and result.userMsg and result.sysMsgType == SystemMessages.SM_TYPE.Error:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
            self.__breakDecorationsProcess = False
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.DECORATIONS_POPOVER_BROKEN: True})

    def __onNeedMoreClick(self):
        self.__craftCtrl.setSettings(toyTypeID=TOY_TYPE_IDS_BY_NAME.get(self.__decorationType, RANDOM_VALUE))
        self.__flowLogger.logSmallDecorationSlotClick(NewYearNavigation.getCurrentObject())
        NewYearNavigation.switchToView(ViewAliases.CRAFT_VIEW)
        self.destroyWindow()

    def __onIsNewStateChanged(self, args):
        changedIndex = int(args.get('index'))
        slot = self.viewModel.getSlots().getValue(changedIndex)
        slot.setIsNew(False)

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
        if fragmentsChanged and toysChanged and self.__breakDecorationsProcess:
            self.__breakDecorationsProcess = False
            with self.viewModel.transaction() as model:
                model.setIsBreakAnimationEnabled(True)
                model.setExpectedShardsCount(0)
                self.__updateStatus(model)

    @staticmethod
    def __removeBrokenSlots(model):
        breakSelections = model.getBreakSelections()
        modelSlots = model.getSlots()
        modelSlots.removeValues([ i for i in breakSelections ])
        modelSlots.invalidate()
        breakSelections.invalidate()
        breakSelections.clear()

    def __onBreakAnimationComplete(self):
        with self.viewModel.transaction() as model:
            model.setIsBreakAnimationEnabled(False)
            self.__removeBrokenSlots(model)
            self.__updateStatus(model)
