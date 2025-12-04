# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/popovers/ny_decorations_popover.py
from adisp import adisp_process
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.gui.impl.new_year.sounds import NewYearSoundEvents, NewYearSoundsManager
from new_year.gui.impl.new_year.views.toy_presenter import PopoverToyPresenter
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency
from new_year.gui.shared.events import NewYearEvent
from new_year_common.items.components.ny_constants import ToyTypes, INVALID_TOY_ID
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from new_year.skeletons.new_year import INewYearController
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.ny_city_view_model import NyCityViewModel
from new_year.gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from shared_utils import findFirst
from itertools import chain
_HANG_SOUNDS_MAP = {ToyTypes.TOP: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.BALL: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.GARLAND_FIR: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.FLOOR: NewYearSoundEvents.ADD_TOY_TREE_DOWN,
 ToyTypes.LIGHTS_HOUSES: NewYearSoundEvents.ADD_TOY_TEREM,
 ToyTypes.LIGHTS_FIR: NewYearSoundEvents.ADD_TOY_TEREM,
 ToyTypes.KIOSK: NewYearSoundEvents.ADD_TOY_FAIR_SMALL,
 ToyTypes.PAVILION: NewYearSoundEvents.ADD_TOY_FAIR_BIG,
 ToyTypes.SCULPTURE: NewYearSoundEvents.ADD_TOY_INSTALLATIONS,
 ToyTypes.SKATING: NewYearSoundEvents.ADD_TOY_SNOWSLIDE,
 ToyTypes.ATTRACTION: NewYearSoundEvents.ADD_TOY_FIREWORKS,
 ToyTypes.PET_TOY: NewYearSoundEvents.ADD_TOY_TEREM,
 ToyTypes.PET_FOOD: NewYearSoundEvents.ADD_TOY_TEREM,
 ToyTypes.PET_BED: NewYearSoundEvents.ADD_TOY_TEREM,
 ToyTypes.PET_INTERACTIVE: NewYearSoundEvents.ADD_TOY_TEREM,
 ToyTypes.FIREWORKS: NewYearSoundEvents.ADD_TOY_FIREWORKS,
 ToyTypes.SNOW_SLIDE: NewYearSoundEvents.ADD_TOY_SNOWSLIDE,
 ToyTypes.TENT: NewYearSoundEvents.ADD_TOY_FAIR_BIG,
 ToyTypes.TABLE: NewYearSoundEvents.ADD_TOY_FAIR_SMALL,
 ToyTypes.TEREM: NewYearSoundEvents.ADD_TOY_TEREM,
 ToyTypes.FENCE: NewYearSoundEvents.ADD_TOY_TEREM}

class NyDecorationsPopover(HistorySubModelPresenter):
    __slots__ = ('__selectedSlotId', '__newToys')
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, viewModel=None, parentView=None, selectedSlotId=None, **kwargs):
        super(NyDecorationsPopover, self).__init__(viewModel, parentView, **kwargs)
        self.__selectedSlotId = selectedSlotId
        self.__newToys = {}

    @property
    def viewModel(self):
        return super(NyDecorationsPopover, self).getViewModel()

    def finalize(self):
        self.__sendSeenToy()
        super(NyDecorationsPopover, self).finalize()

    def _getEvents(self):
        return ((self.viewModel.onIsNewStateChanged, self.__onIsNewStateChanged), (self.viewModel.onApplyDecorationSelection, self.__onApplyDecorationSelection), (self._nyController.onCustomizationObjectUpdated, self.__onCustomizationObjectUpdated))

    def setSelectedSlotID(self, selectedSlotId):
        self.__selectedSlotId = selectedSlotId
        with self.viewModel.transaction() as model:
            self.__updateDecorationSlots(model=model)

    def __onCustomizationObjectUpdated(self, *args):
        currentObject = NewYearNavigation.getCurrentObject()
        if currentObject in args:
            with self.viewModel.transaction() as model:
                self.__updateDecorationSlots(model=model)

    def __onApplyDecorationSelection(self, args):
        toyId = int(args['index'])
        self.__applyDecorationSelection(toyID=toyId)
        with self.viewModel.transaction() as model:
            self.__updateDecorationSlots(model=model, selectedToyID=toyId)

    def __onIsNewStateChanged(self, args):
        toyID = int(args.get('index'))
        toySlots = self.viewModel.getDecorationsSlots()
        toyItem = findFirst(lambda toySlot: toySlot.getToyID() == toyID, toySlots)
        inventoryToys = self._itemsCache.items.festivity.getToys()
        toyInfo = inventoryToys.get(toyID)
        if toyItem and toyItem.getIsNew() and toyInfo is not None:
            self.__newToys[toyID] = toyInfo.getUnseenCount()
            toyItem.setIsNew(False)
        return

    def __sendSeenToy(self):
        if self.__newToys:
            self._nyController.sendSeenToys([ toy for toy in chain(*self.__newToys.iteritems()) ])
            self.__newToys = {}

    def __updateDecorationSlots(self, model, selectedToyID=None):
        selectedSlotId = self.__selectedSlotId
        slots = model.getDecorationsSlots()
        slots.clear()
        if selectedSlotId < 0:
            slots.invalidate()
            self.__sendSeenToy()
            return
        else:
            decorationType = self._nyController.getSlotDescrs()[selectedSlotId].type
            selectedToyID = self._itemsCache.items.festivity.getSlots()[selectedSlotId] if selectedToyID is None else selectedToyID
            allToys = self._nyController.getAllToysByTypeFromCache(decorationType)
            for toyDescriptor in allToys:
                slot = PopoverToyPresenter(toyDescriptor).asSlotViewModel()
                if selectedToyID == toyDescriptor.getID():
                    slot.setIsSelected(True)
                if toyDescriptor.getID() in self.__newToys:
                    slot.setIsNew(False)
                slots.addViewModel(slot)

            slots.invalidate()
            self.__sendSeenToy()
            return

    @adisp_process
    def __applyDecorationSelection(self, toyID):
        slotID = self.__selectedSlotId
        toy = self._itemsCache.items.festivity.getToys().get(toyID)
        if not toy:
            result = yield self._nyController.buyToy(toyID)
            if not result.success:
                return
            toy = self._itemsCache.items.festivity.getToys().get(toyID)
        toyID = toy.getID() if toy is not None else INVALID_TOY_ID
        slotData = self._itemsCache.items.festivity.getSlots()[slotID]
        oldToy = self._itemsCache.items.festivity.getToys()[slotData] if slotData > 0 else None
        oldToyAtmosphere = oldToy.getAtmosphere() if oldToy is not None else 0
        newToyAtmosphere = toy.getAtmosphere() if toy is not None else 0
        result = yield self._nyController.hangToy(toyID, slotID)
        if result.success:
            g_eventBus.handleEvent(NewYearEvent(NewYearEvent.ON_TOY_INSTALLED, ctx={'toyID': toyID,
             'slotID': slotID,
             'atmosphereBonus': newToyAtmosphere - oldToyAtmosphere}), scope=EVENT_BUS_SCOPE.LOBBY)
            decorationType = self._nyController.getSlotDescrs()[slotID].type
            if toy is not None and decorationType in _HANG_SOUNDS_MAP:
                NewYearSoundsManager.playEvent(_HANG_SOUNDS_MAP[decorationType])
        return
