# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/glade/ny_toys_list.py
from adisp import adisp_process
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.toy_model import ToyModel, SlotState, SlotType
from gui.impl.new_year.sounds import NewYearSoundEvents, NewYearSoundsManager
from helpers import dependency
from items.components.ny_constants import ToyTypes, INVALID_TOY_ID
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from uilogging.ny.loggers import NyDecorationsSlotPopoverFlowLogger
_HANG_SOUNDS_MAP = {ToyTypes.TOP: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.BALL: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.GARLAND_FIR: NewYearSoundEvents.ADD_TOY_TREE,
 ToyTypes.FLOOR: NewYearSoundEvents.ADD_TOY_TREE_DOWN,
 ToyTypes.COLOR_FIR: NewYearSoundEvents.ADD_COLOR_FIR,
 ToyTypes.PAVILION: NewYearSoundEvents.ADD_TOY_KITCHEN_TABLE,
 ToyTypes.KITCHEN: NewYearSoundEvents.ADD_TOY_KITCHEN_BBQ,
 ToyTypes.GARLAND_FAIR: NewYearSoundEvents.ADD_TOY_BIG_GARLANDS,
 ToyTypes.ATTRACTION: NewYearSoundEvents.ADD_TOY_KITCHEN_ATTRACTION,
 ToyTypes.EXPOSITION: NewYearSoundEvents.ADD_TOY_KITCHEN_ATTRACTION,
 ToyTypes.SCULPTURE: NewYearSoundEvents.ADD_TOY_SNOWTANK,
 ToyTypes.SCULPTURE_LIGHT: NewYearSoundEvents.ADD_TOY_BIG_GARLANDS,
 ToyTypes.GARLAND_INSTALLATION: NewYearSoundEvents.ADD_TOY_SNOWTANK_LIGHT,
 ToyTypes.PYRO: NewYearSoundEvents.ADD_TOY_SNOWTANK,
 ToyTypes.KIOSK: NewYearSoundEvents.ADD_TOY_SNOWTANK,
 ToyTypes.DOG_BOWL: NewYearSoundEvents.REMOVE_TOY_EFFECT_SMALL,
 ToyTypes.DOG_TOY: NewYearSoundEvents.REMOVE_TOY_EFFECT_SMALL,
 ToyTypes.DOG_COLLAR: NewYearSoundEvents.REMOVE_TOY_EFFECT_SMALL,
 ToyTypes.DOG_HOUSE: NewYearSoundEvents.REMOVE_TOY_EFFECT_SMALL}
_UNHANG_SOUNDS_MAP = {ToyTypes.TOP: NewYearSoundEvents.REMOVE_TOY_EFFECT_SMALL,
 ToyTypes.BALL: NewYearSoundEvents.REMOVE_TOY_EFFECT_SMALL,
 ToyTypes.GARLAND_FIR: NewYearSoundEvents.REMOVE_TOY_EFFECT_SMALL,
 ToyTypes.FLOOR: NewYearSoundEvents.REMOVE_TOY_EFFECT_SMALL,
 ToyTypes.COLOR_FIR: NewYearSoundEvents.REMOVE_COLOR_FIR,
 ToyTypes.PAVILION: NewYearSoundEvents.REMOVE_TOY_EFFECT_EXPL,
 ToyTypes.KITCHEN: NewYearSoundEvents.REMOVE_TOY_EFFECT_EXPL,
 ToyTypes.GARLAND_FAIR: NewYearSoundEvents.REMOVE_TOY_EFFECT_SMALL,
 ToyTypes.ATTRACTION: NewYearSoundEvents.REMOVE_TOY_EFFECT_CIRCLE,
 ToyTypes.EXPOSITION: NewYearSoundEvents.REMOVE_TOY_EFFECT_CIRCLE,
 ToyTypes.SCULPTURE: NewYearSoundEvents.REMOVE_TOY_EFFECT_EXPL,
 ToyTypes.SCULPTURE_LIGHT: NewYearSoundEvents.REMOVE_TOY_EFFECT_SMALL,
 ToyTypes.GARLAND_INSTALLATION: NewYearSoundEvents.REMOVE_TOY_EFFECT_SMALL,
 ToyTypes.PYRO: NewYearSoundEvents.REMOVE_TOY_EFFECT_SMALL,
 ToyTypes.KIOSK: NewYearSoundEvents.REMOVE_TOY_EFFECT_EXPL}

class NyToysList(object):
    __slots__ = ('__viewModel', '__slotType', '__slotID', '__installedToyID')
    __nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __flowLogger = NyDecorationsSlotPopoverFlowLogger()

    def __init__(self):
        self.__slotType = None
        self.__slotID = None
        self.__installedToyID = None
        self.__viewModel = None
        return

    def initialize(self, viewModel):
        self.__viewModel = viewModel

    def clear(self):
        self.__sendSeenToys()
        self.__viewModel.toysList.onApplySelection -= self.__onApplySelection
        self.__viewModel.toysList.onListClose -= self.__onListClose
        self.__viewModel.toysList.onAllToysSeen -= self.__onAllToysSeen
        with self.__viewModel.transaction() as model:
            model.setSelectedSlot(-1)
            toys = model.toysList.getToys()
            toys.clear()
            toys.invalidate()
        self.__slotType = None
        self.__slotID = None
        self.__installedToyID = None
        return

    def open(self, slotID):
        if slotID > -1:
            self.__slotID = slotID
            self.__slotType = self.__nyController.getSlotDescrs()[slotID].type
            self.__installedToyID = self.__nyController.getInstalledToyInSlot(slotID)
            self.__fillSlots()
            self.__viewModel.toysList.onApplySelection += self.__onApplySelection
            self.__viewModel.toysList.onListClose += self.__onListClose
            self.__viewModel.toysList.onAllToysSeen += self.__onAllToysSeen

    def finalize(self):
        self.clear()

    def __onApplySelection(self, args):
        requester = self.__getNewYearRequester()
        inventoryToys = requester.getToys()
        self.__installedToyID = self.__nyController.getInstalledToyInSlot(self.__slotID)
        toyID = int(args.get('toyId', INVALID_TOY_ID))
        if toyID != INVALID_TOY_ID and self.__slotID in inventoryToys and toyID in inventoryToys[self.__slotID]:
            toy = inventoryToys[self.__slotID][toyID] if self.__installedToyID is not toyID else None
            self.__hangToy(toy)
        return

    def __onListClose(self):
        self.clear()

    def __onAllToysSeen(self):
        self.__sendSeenToys()

    def __playHangDecorationSound(self, type_):
        if type_ in _HANG_SOUNDS_MAP:
            NewYearSoundsManager.playEvent(_HANG_SOUNDS_MAP[type_])

    def __playUnhangDecorationSound(self, type_):
        if type_ in _UNHANG_SOUNDS_MAP:
            NewYearSoundsManager.playEvent(_UNHANG_SOUNDS_MAP[type_])

    @adisp_process
    def __hangToy(self, toy):
        toyID = toy.getID() if toy is not None else INVALID_TOY_ID
        slotID = self.__slotID
        slotType = self.__slotType
        result = yield self.__nyController.hangToy(toyID, slotID)
        if result.success:
            if toy is not None:
                self.__playHangDecorationSound(slotType)
            else:
                self.__playUnhangDecorationSound(slotType)
            self.clear()
        return

    def __getNewYearRequester(self):
        return self.__itemsCache.items.festivity

    def __sendSeenToys(self):
        if self.__slotID > -1:
            self.__nyController.sendSeenToys(self.__slotID)

    def __fillSlots(self):
        with self.__viewModel.toysList.transaction() as model:
            allToys = self.__nyController.getAllToysByType(self.__slotType)
            inventoryToys = self.__nyController.getToysBySlot(self.__slotID)
            toys = model.getToys()
            toys.clear()
            for toyDescriptor in allToys:
                toyID = toyDescriptor.id
                toyModel = ToyModel()
                toyModel.setToyID(toyID)
                toyModel.setIcon(toyDescriptor.icon)
                isAvailable = toyID in inventoryToys
                if isAvailable:
                    state = SlotState.AVAILABLE
                    toy = inventoryToys[toyID]
                    if toy.getID() == self.__installedToyID:
                        state = SlotState.SELECTED
                    toyModel.setIsNew(toy.getUnseenCount() > 0)
                elif toyDescriptor.type in ToyTypes.DOG:
                    state = SlotState.LOCKED
                else:
                    state = SlotState.UNAVAILABLE
                toyModel.setSlotType(SlotType.GUESTD if toyDescriptor.type in ToyTypes.DOG else SlotType.DECORATION)
                toyModel.setState(state)
                toyModel.setDropSource('' if toyDescriptor.type in ToyTypes.DOG else toyDescriptor.dropSource)
                toys.addViewModel(toyModel)

            toys.invalidate()
            model.setType(self.__slotType)
