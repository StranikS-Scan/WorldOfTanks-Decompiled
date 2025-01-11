# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/popovers/ny_decorations_popover.py
from itertools import chain
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from adisp import adisp_process
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.impl.gen.resources import R
from new_year.gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_decorations_popover_model import NyDecorationsPopoverModel
from new_year.gui.impl.lobby.new_year.tooltips.ny_decoration_state_tooltip import NyDecorationStateTooltip
from new_year.gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from new_year.gui.impl.lobby.new_year.tooltips.ny_pet_decoration_tooltip import NyPetDecorationTooltip
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.gui.impl.new_year.sounds import NewYearSoundEvents, NewYearSoundsManager
from new_year.gui.impl.new_year.views.toy_presenter import PopoverToyPresenter
from gui.impl.pub import PopOverViewImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency
from new_year.gui.shared.events import NewYearEvent
from new_year_common.items.components.ny_constants import ToyTypes, TOY_TYPE_IDS_BY_NAME, RANDOM_VALUE, INVALID_TOY_ID
from new_year.ny_constants import SyncDataKeys, ViewAliases
from new_year.gui.shared.gui_items.processors.ny_processor import NewYearBreakToysProcessor
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from new_year.skeletons.new_year import INewYearController, INewYearCraftMachineController
_HANG_SOUNDS_MAP = {ToyTypes.TOP: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.BALL: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.GARLAND_FIR: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.FLOOR: NewYearSoundEvents.ADD_TOY_TREE_DOWN,
 ToyTypes.LIGHTS_HOUSES: NewYearSoundEvents.ADD_TOY_ILLUMINATION,
 ToyTypes.LIGHTS_FIR: NewYearSoundEvents.ADD_TOY_ILLUMINATION,
 ToyTypes.KIOSK: NewYearSoundEvents.ADD_TOY_FAIR_SMALL,
 ToyTypes.PAVILION: NewYearSoundEvents.ADD_TOY_FAIR_BIG,
 ToyTypes.SCULPTURE: NewYearSoundEvents.ADD_TOY_INSTALLATIONS,
 ToyTypes.SKATING: NewYearSoundEvents.ADD_TOY_SKATING,
 ToyTypes.ATTRACTION: NewYearSoundEvents.ADD_TOY_ATTRACTION,
 ToyTypes.PET_TOY: NewYearSoundEvents.ADD_TOY_ILLUMINATION,
 ToyTypes.PET_FOOD: NewYearSoundEvents.ADD_TOY_ILLUMINATION,
 ToyTypes.PET_BED: NewYearSoundEvents.ADD_TOY_ILLUMINATION,
 ToyTypes.PET_INTERACTIVE: NewYearSoundEvents.ADD_TOY_ILLUMINATION}
_ANIMATION_DELAY = 0.5
_MIN_COUNT_IN_LIST = 0

class NyDecorationsPopover(PopOverViewImpl):
    __slots__ = ('__slotID', '__decorationType', '__breakDecorationsProcess', '__selectedDecoration', '__newToys')
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    __craftCtrl = dependency.descriptor(INewYearCraftMachineController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, slotID):
        settings = ViewSettings(R.views.new_year.lobby.new_year.popovers.NyDecorationsPopover())
        settings.model = NyDecorationsPopoverModel()
        super(NyDecorationsPopover, self).__init__(settings)
        self.__slotID = slotID
        self.__decorationType = self.__getDecorationType()
        toyID = self.__getNewYearRequester().getSlots()[self.__slotID]
        self.__selectedDecoration = self.__getNewYearRequester().getToys().get(toyID)
        self.__breakDecorationsProcess = False
        self.__newToys = {}

    @property
    def viewModel(self):
        return super(NyDecorationsPopover, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        toyID = event.getArgument('toyID')
        if contentID == R.views.new_year.lobby.new_year.tooltips.NyDecorationTooltip():
            return NyDecorationTooltip(toyID)
        if contentID == R.views.new_year.lobby.new_year.tooltips.NyPetDecorationTooltip():
            return NyPetDecorationTooltip(toyID)
        return NyDecorationStateTooltip(event.getArgument('atmosphereBonus')) if contentID == R.views.new_year.lobby.new_year.tooltips.NyDecorationStateTooltip() else super(NyDecorationsPopover, self).createToolTipContent(event, contentID)

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
        if self.__newToys:
            self.__sendSeenToy()
        super(NyDecorationsPopover, self)._finalize()

    def __updateHeader(self, model):
        title = R.strings.ny.decorationTypes.dyn(self.__decorationType)()
        setting = R.invalid()
        decorationTypeIcon = R.images.new_year.gui.maps.icons.newYear.decoration_types.craft.dyn(self.__decorationType)()
        model.setTitle(title)
        model.setSetting(setting)
        model.setDecorationTypeIcon(decorationTypeIcon)
        model.setCurrentObject(NewYearNavigation.getCurrentObject())

    def __fillSlots(self, model):
        slots = model.getSlots()
        if self.__selectedDecoration is not None:
            model.getAppliedSelections().addNumber(self.__selectedDecoration.getID())
        allToys = self._nyController.getAllToysByTypeFromCache(self.__decorationType)
        self.__fillSlotsByType(slots, allToys)
        slots.invalidate()
        return

    def __fillSlotsByType(self, slots, allToys):
        for toyDescriptor in allToys:
            slot = PopoverToyPresenter(toyDescriptor).asSlotViewModel()
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
        if not nyStorage.get(NewYearStorageKeys.DECORATIONS_POPOVER_VIEWED, False):
            self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.DECORATIONS_POPOVER_VIEWED: True})
            if self._nyController.getAllCollectedToysId():
                return False
            model.setState(NyDecorationsPopoverModel.RECEIVE_INFO_STATE)
        elif not isSlotsEmpty and not nyStorage.get(NewYearStorageKeys.DECORATIONS_POPOVER_BROKEN, False):
            model.setState(NyDecorationsPopoverModel.BREAK_INFO_STATE)
        else:
            return False
        return True

    def __getDecorationType(self):
        return self._nyController.getSlotDescrs()[self.__slotID].type

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

    @adisp_process
    def __onApplySelection(self, args):
        selectedItemIdx = int(args['index'])
        isAlreadyApplied = selectedItemIdx in self.viewModel.getAppliedSelections()
        with self.viewModel.transaction() as model:
            self.__updateSelection(model.getAppliedSelections(), selectedItemIdx)
        selectedItem = self.viewModel.getSlots().getValue(selectedItemIdx)
        if selectedItem is None or isAlreadyApplied:
            return
        else:
            toyID = selectedItem.getToyID()
            toy = self.__getNewYearRequester().getToys().get(toyID)
            if not toy and selectedItem.getGoldPrice() >= 0:
                result = yield self._nyController.buyToy(toyID)
                if not result.success:
                    return
                toy = self.__getNewYearRequester().getToys().get(toyID)
            self.__hangToy(toy, self.__slotID)
            return

    @adisp_process
    def __hangToy(self, toy, slotID):
        toyID = toy.getID() if toy is not None else INVALID_TOY_ID
        slotData = self._itemsCache.items.festivity.getSlots()[slotID]
        oldToy = self._itemsCache.items.festivity.getToys()[slotData] if slotData > 0 else None
        oldToyAtmosphere = oldToy.getAtmosphere() if oldToy is not None else 0
        newToyAtmosphere = toy.getAtmosphere() if toy is not None else 0
        result = yield self._nyController.hangToy(toyID, slotID)
        if result.success:
            g_eventBus.handleEvent(NewYearEvent(NewYearEvent.ON_TOY_INSTALLED, ctx={'toyID': toyID,
             'slotID': slotID,
             'atmoshereBonus': newToyAtmosphere - oldToyAtmosphere}), scope=EVENT_BUS_SCOPE.LOBBY)
            if toy is not None:
                self.__playHangDecorationSound()
        self.destroyWindow()
        return

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

    @adisp_process
    def __onBreakBtnClick(self, *_):
        if self.__breakDecorationsProcess:
            return
        toysToBreak = {}
        for idx in self.viewModel.getBreakSelections():
            slot = self.viewModel.getSlots().getValue(idx)
            toysToBreak[slot.getToyID()] = toysToBreak.setdefault(slot.getToyID(), 0) + slot.getCount()

        self.__breakDecorationsProcess = True
        result = yield NewYearBreakToysProcessor(toysToBreak, self.viewModel.getExpectedShardsCount(), False).request()
        if not result.success and result.userMsg and result.sysMsgType == SystemMessages.SM_TYPE.Error:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
            self.__breakDecorationsProcess = False
        elif result.userMsg and result.sysMsgType:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.DECORATIONS_POPOVER_BROKEN: True})

    def __onNeedMoreClick(self):
        self.__craftCtrl.setSettings(toyTypeID=TOY_TYPE_IDS_BY_NAME.get(self.__decorationType, RANDOM_VALUE))
        NewYearNavigation.switchToView(ViewAliases.CRAFT_VIEW)
        self.destroyWindow()

    def __onIsNewStateChanged(self, args):
        changedIndex = int(args.get('index'))
        slot = self.viewModel.getSlots().getValue(changedIndex)
        if slot.getIsNew() is False:
            self.__updateNewToys(slot.getToyID())
        slot.setIsNew(False)

    def __updateNewToys(self, toyID):
        inventoryToys = self.__getNewYearRequester().getToys()
        if inventoryToys.get(toyID) is not None:
            toyInfo = inventoryToys[toyID]
            if toyInfo.getToyType() == self.__decorationType and toyInfo.getCount() > 0:
                self.__newToys[toyID] = toyInfo.getUnseenCount()
        return

    def __sendSeenToy(self):
        self._nyController.sendSeenToys([ toy for toy in chain(*self.__newToys.iteritems()) ])
        self.__newToys = {}

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
