# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/ny_mega_decorations_popover.py
import logging
from adisp import process
from frameworks.wulf import ViewStatus, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_mega_decorations_popover_model import NyMegaDecorationsPopoverModel
from gui.impl.gui_decorators import trackLifeCycle
from gui.impl.new_year.mega_toy_bubble import MegaToyBubble
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.tooltips.toy_content import MegaToyContent
from gui.impl.new_year.views.toy_presenter import PopoverToyPresenter
from gui.impl.new_year.sounds import NewYearSoundEvents
from gui.impl.pub import PopOverViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from helpers import dependency
from items.components.ny_constants import INVALID_TOY_ID, ToyTypes
from new_year.ny_bonuses import CreditsBonusHelper
from new_year.ny_constants import SyncDataKeys
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, INewYearCraftMachineController
_logger = logging.getLogger(__name__)

@trackLifeCycle('new_year.mega_decoration_popover')
class NYMegaDecorationsPopover(NewYearNavigation, PopOverViewImpl):
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _isScopeWatcher = False
    __craftCtrl = dependency.descriptor(INewYearCraftMachineController)
    __slots__ = ('__slotID', '__slotType', '__isSelected', '__megaDecoration')

    def __init__(self, slotID, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.ny_mega_decorations_popover.NyMegaDecorationsPopover())
        settings.model = NyMegaDecorationsPopoverModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NYMegaDecorationsPopover, self).__init__(settings)
        self.__slotID = slotID
        self.__slotType = self._nyController.getSlotDescrs()[self.__slotID].type
        toyID = self._itemsCache.items.festivity.getSlots()[self.__slotID]
        self.__isSelected = toyID != INVALID_TOY_ID

    @property
    def viewModel(self):
        return super(NYMegaDecorationsPopover, self).getViewModel()

    @property
    def isCloseBtnVisible(self):
        return True

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.ny_mega_toy_tooltip_content.NyMegaToyTooltipContent():
            toyID = event.getArgument('toyID')
            return MegaToyContent(toyID)

    def _initialize(self, *args, **kwargs):
        soundConfig = {}
        super(NYMegaDecorationsPopover, self)._initialize(soundConfig)
        self.viewModel.onSelectedDecoration += self.__onSelectedDecoration
        self._nyController.onDataUpdated += self.__onDataUpdated
        with self.viewModel.transaction() as vm:
            iconType = ToyTypes.MEGA_COMMON if self.__slotType in ToyTypes.MEGA else self.__slotType
            vm.setDecorationTypeIcon(R.images.gui.maps.icons.new_year.decorationTypes.blue.dyn(iconType)())
            vm.setObjectBonus(CreditsBonusHelper.getMegaToysBonusValue())
            vm.setTotalBonus(CreditsBonusHelper.getMegaToysBonusByCount(len(ToyTypes.MEGA)))
            self.__updateSlot(model=vm)
            self.__updateTitle(vm, self.__isSelected)

    def _finalize(self):
        self.viewModel.onSelectedDecoration -= self.__onSelectedDecoration
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self.__sendSeenToys()
        super(NYMegaDecorationsPopover, self)._finalize()

    def __onDataUpdated(self, keys):
        fragmentsChanged = SyncDataKeys.TOY_FRAGMENTS in keys
        toysChanged = SyncDataKeys.INVENTORY_TOYS in keys
        if fragmentsChanged or toysChanged:
            self.__updateSlot()

    def __getMegaToy(self):
        megaToys = self._nyController.getToysByType(self.__slotType)
        return first(megaToys)

    @replaceNoneKwargsModel
    def __updateSlot(self, model=None):
        megaDecoration = self.__getMegaToy()
        hasDecoration = megaDecoration is not None and megaDecoration.getCount() > 0 or self.__isSelected
        if hasDecoration:
            PopoverToyPresenter(megaDecoration).fillViewModel(model.slot)
        else:
            self.__setShardsInfo(model)
        model.setSelected(self.__isSelected)
        model.setHasDecoration(hasDecoration)
        model.slot.setSelected(self.__isSelected)
        model.slot.setIsButton(not hasDecoration)
        model.slot.setIsNew(MegaToyBubble.mustBeShown(self.__slotType, self.__isSelected))
        return

    def __setShardsInfo(self, model):
        currentCount = self._itemsCache.items.festivity.getShardsCount()
        model.setPartsCurrent(currentCount)
        craftCost = self.__craftCtrl.calculateMegaToyCraftCost()
        model.setPartsTotal(craftCost)

    def __sendSeenToys(self):
        inventoryToys = self._itemsCache.items.festivity.getToys()
        megaToy = self.__getMegaToy()
        if megaToy is None:
            return
        else:
            toyInfo = inventoryToys.get(megaToy.getID())
            if toyInfo is not None and toyInfo.getUnseenCount() > 0:
                self._nyController.sendSeenToys([toyInfo.getID(), toyInfo.getUnseenCount()])
            return

    @process
    def __onSelectedDecoration(self):
        if not self.viewModel.getHasDecoration():
            self._goToCraftView(isMegaOn=True)
            return
        toyID = INVALID_TOY_ID if self.viewModel.getSelected() else self.viewModel.slot.getToyID()
        result = yield self._nyController.hangToy(toyID, self.__slotID)
        if result.success and self.viewStatus == ViewStatus.LOADED:
            self.__isSelected = toyID != INVALID_TOY_ID
            with self.viewModel.transaction() as tx:
                tx.setSelected(self.__isSelected)
                tx.slot.setSelected(self.__isSelected)
                self.__updateTitle(tx, self.__isSelected)
            if self.__isSelected:
                if self.__slotType in ToyTypes.MEGA:
                    self._newYearSounds.playEvent(NewYearSoundEvents.ADD_TOY_MEGA)
                self.destroyWindow()
            else:
                tx.slot.setIsNew(True)
        elif not result.success:
            self.destroyWindow()

    def __updateTitle(self, model, selected):
        if selected:
            megaDecoration = self.__getMegaToy()
            decorationNameResId = megaDecoration.getName()
        else:
            decorationNameResId = R.strings.ny.decorationTypes.dyn(self.__slotType)()
        model.setDecorationName(decorationNameResId)
