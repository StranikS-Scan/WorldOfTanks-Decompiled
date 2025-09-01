# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_inventory_presenter.py
from __future__ import absolute_import
import typing
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicles_inventory_model import VehiclesInventoryModel
from gui.impl.lobby.tooltips.carousel_vehicle_tooltip import CarouselVehicleTooltipView
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.battle_pass.battle_pass_helpers import getSupportedCurrentArenaBonusType
from gui.shared import event_dispatcher
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IBattlePassController
if typing.TYPE_CHECKING:
    from gui.shared.utils.requesters import RequestCriteria

class VehicleInventoryPresenter(ViewComponent[VehiclesInventoryModel], IGlobalListener):
    __battlePass = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, validVehicleCriteria):
        self.__validVehicleCriteria = validVehicleCriteria
        super(VehicleInventoryPresenter, self).__init__(model=VehiclesInventoryModel)

    def onPrbEntitySwitched(self, _=None):
        self.getViewModel().setBpEntityValid(self.__battlePass.isGameModeEnabled(self.__getCurrentArenaBonusType()))

    def createToolTipContent(self, event, contentID):
        return CarouselVehicleTooltipView(event.getArgument('inventoryId')) if contentID == R.views.mono.hangar.vehicle_tooltip() else super(VehicleInventoryPresenter, self).createToolTipContent(event=event, contentID=contentID)

    @property
    def viewModel(self):
        return super(VehicleInventoryPresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(VehicleInventoryPresenter, self)._onLoading(*args, **kwargs)
        self.startGlobalListening()
        self.__updateModel()

    def _finalize(self):
        self.__validVehicleCriteria = None
        self.stopGlobalListening()
        super(VehicleInventoryPresenter, self)._finalize()
        return

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self.__onVehicleChanged),
         (self.viewModel.onGoBuyVehicle, self.__onGoBuyVehicle),
         (self.viewModel.onBuySlot, self.__onBuySlot),
         (self.viewModel.onGoRecoverVehicle, self.__onGoRecoverVehicle),
         (self.__itemsCache.onSyncCompleted, self.__onCacheResync),
         (self.viewModel.onSelect, self.__onSelectVehicle),
         (self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassSettingsChanged))

    @prbEntityProperty
    def __prbEntity(self):
        return None

    def __onVehicleChanged(self):
        if g_currentVehicle.intCD in self.__itemsCache.items.getVehicles(self.__validVehicleCriteria):
            self.__updateSelectedModel()

    def __onBattlePassSettingsChanged(self, *_):
        self.__updateModel()

    def __onSelectVehicle(self, vehId):
        inventoryId = int(vehId['id'])
        g_currentVehicle.selectVehicle(inventoryId)

    def __onCacheResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.CLIENT_UPDATE:
            self.__updateModel()

    def __onGoBuyVehicle(self):
        event_dispatcher.showTechTree()

    def __onBuySlot(self):
        ActionsFactory.doAction(ActionsFactory.BUY_VEHICLE_SLOT)

    def __onGoRecoverVehicle(self):
        event_dispatcher.showStorage(STORAGE_CONSTANTS.IN_HANGAR, STORAGE_CONSTANTS.VEHICLES_TAB_RESTORE)

    def __getCurrentArenaBonusType(self):
        return getSupportedCurrentArenaBonusType(self.prbEntity.getQueueType())

    def __updateModel(self):
        items = self.__itemsCache.items
        inventory = self.__itemsCache.items.inventory
        slots = items.stats.vehicleSlots
        slotPrice = items.shop.getVehicleSlotsPrice(slots)
        slotPriceCurrency = slotPrice.getCurrency()
        price = int(slotPrice.get(slotPriceCurrency, 0))
        defaultSlotPrice = items.shop.defaults.getVehicleSlotsPrice(slots)
        defaultPriceCurrency = defaultSlotPrice.getCurrency()
        defaultPrice = int(defaultSlotPrice.get(defaultPriceCurrency, 0))
        emptySlotsCount = inventory.getFreeSlots(slots)
        criteria = REQ_CRITERIA.IN_CD_LIST(items.recycleBin.getVehiclesIntCDs()) | REQ_CRITERIA.VEHICLE.IS_RESTORE_POSSIBLE
        bpStatus = self.viewModel.ENABLED
        if self.__battlePass.isDisabled():
            bpStatus = self.viewModel.DISABLED
        elif self.__battlePass.isPaused():
            bpStatus = self.viewModel.PAUSED
        with self.viewModel as model:
            model.setRecoverableVehicleCount(len(items.getVehicles(criteria)))
            model.setBpEntityValid(self.__battlePass.isGameModeEnabled(self.__getCurrentArenaBonusType()))
            model.setBpStatus(bpStatus)
            model.setSlotPrice(price)
            model.setDefaultSlotPrice(defaultPrice)
            model.setSlotPriceCurrency(slotPriceCurrency)
            model.setFreeSlotsCount(emptySlotsCount)
            model.setHasDiscont(slotPrice != defaultSlotPrice)
            self.__updateSelectedModel()

    def __updateSelectedModel(self):
        if not g_currentVehicle.isPresent():
            g_currentVehicle.selectVehicle()
        if g_currentVehicle.isPresent():
            with self.viewModel as model:
                model.setCurrentVehicleInventoryId(g_currentVehicle.invID)
                model.setCurrentVehicleIntCD(g_currentVehicle.intCD)
        else:
            self.viewModel.setCurrentVehicleInventoryId(VehiclesInventoryModel.NO_VEHICLE_ID)
            self.viewModel.setCurrentVehicleIntCD(VehiclesInventoryModel.NO_VEHICLE_ID)
