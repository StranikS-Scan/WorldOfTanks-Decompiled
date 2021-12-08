# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/popovers/ny_mega_decorations_popover.py
import logging
from adisp import process
from frameworks.wulf import ViewStatus, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_mega_decorations_popover_model import NyMegaDecorationsPopoverModel
from gui.impl.lobby.new_year.tooltips.ny_decoration_state_tooltip import NyDecorationStateTooltip
from gui.impl.lobby.new_year.tooltips.ny_mega_decoration_tooltip import NyMegaDecorationTooltip
from gui.impl.new_year.mega_toy_bubble import MegaToyBubble
from gui.impl.new_year.navigation import ViewAliases, NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundEvents, NewYearSoundsManager
from gui.impl.new_year.views.toy_presenter import PopoverToyPresenter
from gui.impl.pub import PopOverViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from items.components.ny_constants import INVALID_TOY_ID, TOY_SLOT_USAGE, ToyTypes
from new_year.ny_bonuses import CreditsBonusHelper
from new_year.ny_constants import SyncDataKeys, PERCENT
from shared_utils import first
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, INewYearCraftMachineController
from uilogging.ny.loggers import NyDecorationsSlotPopoverFlowLogger
_logger = logging.getLogger(__name__)

class NyMegaDecorationsPopover(PopOverViewImpl):
    _nyController = dependency.descriptor(INewYearController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __craftCtrl = dependency.descriptor(INewYearCraftMachineController)
    __flowLogger = NyDecorationsSlotPopoverFlowLogger()
    __slots__ = ('__slotID', '__slotType', '__isSelected', '__megaDecoration', '__isPureSlot')

    def __init__(self, slotID, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.popovers.NyMegaDecorationsPopover())
        settings.model = NyMegaDecorationsPopoverModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NyMegaDecorationsPopover, self).__init__(settings)
        self.__slotID = slotID
        self.__slotType = self._nyController.getSlotDescrs()[self.__slotID].type
        toyID = self.__itemsCache.items.festivity.getSlots()[self.__slotID]
        self.__isSelected = toyID != INVALID_TOY_ID
        self.__megaDecoration = self.__getMegaToy()
        self.__isPureSlot = self.__slotID in self.__itemsCache.items.festivity.getPureSlots()

    @property
    def viewModel(self):
        return super(NyMegaDecorationsPopover, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyDecorationStateTooltip():
            atmosphereBonus = event.getArgument('atmosphereBonus')
            return NyDecorationStateTooltip(atmosphereBonus)
        if contentID == R.views.lobby.new_year.tooltips.NyMegaDecorationTooltip():
            toyID = event.getArgument('toyID')
            return NyMegaDecorationTooltip(toyID, isPureToy=self.__isPureSlot)
        return super(NyMegaDecorationsPopover, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as vm:
            vm.setObjectBonus(CreditsBonusHelper.getMegaToysBonusValue() * PERCENT)
            vm.setTotalBonus(CreditsBonusHelper.getMegaToysBonusByCount(len(ToyTypes.MEGA)) * PERCENT)
            self.__updateSlot(model=vm)
            self.__updateTitle(vm)

    def _initialize(self, *args, **kwargs):
        super(NyMegaDecorationsPopover, self)._initialize(*args, **kwargs)
        self.viewModel.onSelectedDecoration += self.__onSelectedDecoration
        self._nyController.onDataUpdated += self.__onDataUpdated

    def _finalize(self):
        self.viewModel.onSelectedDecoration -= self.__onSelectedDecoration
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self.__sendSeenToys()
        super(NyMegaDecorationsPopover, self)._finalize()

    def __updateTitle(self, model):
        if self.__isSelected:
            decorationNameResId = self.__megaDecoration.getName()
        else:
            decorationNameResId = R.strings.ny.decorationTypes.dyn(self.__slotType)()
        model.setDecorationName(decorationNameResId)
        model.setDecorationTypeIcon(R.images.gui.maps.icons.newYear.decoration_types.craft_small.dyn('{}_pure'.format(self.__slotType))())

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
        hasDecoration = self.__megaDecoration is not None and self.__megaDecoration.getCount() > 0 or self.__isSelected
        if hasDecoration:
            PopoverToyPresenter(self.__megaDecoration, slotId=self.__slotID).fillViewModel(model.slot)
        else:
            self.__setShardsInfo(model)
        model.setIsMaxAtmosphereLevel(self._nyController.isMaxAtmosphereLevel())
        model.setSelected(self.__isSelected)
        model.setHasDecoration(hasDecoration)
        model.slot.setIsNew(MegaToyBubble.mustBeShown(self.__slotType, self.__isSelected))
        if self.__megaDecoration is not None:
            isPureSlot = self.__slotID in self.__itemsCache.items.festivity.getPureSlots()
            model.slot.setAtmosphereBonus(self.__megaDecoration.getAtmosphere(isPureSlot, isPureSlot))
            model.slot.setIsPure(isPureSlot)
        return

    def __setShardsInfo(self, model):
        currentCount = self.__itemsCache.items.festivity.getShardsCount()
        model.setPartsCurrent(currentCount)
        craftCost = self.__craftCtrl.calculateMegaToyCraftCost()
        model.setPartsTotal(craftCost)

    def __sendSeenToys(self):
        if self.__megaDecoration is not None and self.__megaDecoration.getUnseenCount() > 0:
            self._nyController.sendSeenToys([self.__megaDecoration.getID(), self.__megaDecoration.getUnseenCount()])
        return

    @process
    def __onSelectedDecoration(self):
        if not self.viewModel.getHasDecoration():
            self.__craftCtrl.setSettings(isMegaOn=True)
            self.__flowLogger.logBigDecorationSlotClick(NewYearNavigation.getCurrentObject())
            NewYearNavigation.switchToView(ViewAliases.CRAFT_VIEW)
            self.destroyWindow()
            return
        else:
            toyID = INVALID_TOY_ID if self.viewModel.getSelected() else self.viewModel.slot.getToyID()
            toy = self.__itemsCache.items.festivity.getToys().get(toyID)
            if toy is not None:
                isPureToy = toy.getPureCount() > 0
                points = toy.getAtmosphere(isPureToy, self.__isPureSlot)
                toyUsage = TOY_SLOT_USAGE.PURE if isPureToy else TOY_SLOT_USAGE.USED
            else:
                points = 0
                toyUsage = TOY_SLOT_USAGE.USED
            result = yield self._nyController.hangToy(toyID, self.__slotID, toyUsage)
            if result.success and self.viewStatus == ViewStatus.LOADED:
                g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.ON_TOY_INSTALLED, ctx={'toyID': toyID,
                 'slotID': self.__slotID,
                 'atmoshereBonus': points}), scope=EVENT_BUS_SCOPE.LOBBY)
                self.__isSelected = toyID != INVALID_TOY_ID
                with self.viewModel.transaction() as tx:
                    tx.setSelected(self.__isSelected)
                    self.__updateTitle(tx)
                    if self.__isSelected:
                        if self.__slotType in ToyTypes.MEGA:
                            NewYearSoundsManager.playEvent(NewYearSoundEvents.ADD_TOY_MEGA)
                    else:
                        tx.slot.setIsNew(True)
            self.destroyWindow()
            return
