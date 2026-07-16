# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/vehicles_data_providers/ls_vehicle_inventory_presenter.py
from __future__ import absolute_import
import typing
from future.utils import viewvalues
import BigWorld
from account_helpers.telecom_rentals import TelecomRentals
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicles_inventory_model import VehiclesInventoryModel
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.listener import IGlobalListener
from gui.battle_pass.battle_pass_helpers import getSupportedCurrentArenaBonusType
from gui.shared import event_dispatcher
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from last_stand.gui.impl.lobby.tooltips.ls_carousel_tooltip_view import LSVehicleCarouselTooltipView
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_vehicle_selection_controller import ILSVehicleSelectionController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IBattlePassController
from telecom_rentals_common import ROSTER_EXPIRATION_TOKEN_NAME, PARTNERSHIP_TOKEN_NAME
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class LSVehicleInventoryPresenter(ViewComponent[VehiclesInventoryModel], IGlobalListener):
    _itemsCache = dependency.descriptor(IItemsCache)
    __battlePass = dependency.descriptor(IBattlePassController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _lsCtrl = dependency.descriptor(ILSController)
    _lsVehicleCtrl = dependency.descriptor(ILSVehicleSelectionController)

    def __init__(self, vehiclesComponent):
        self.__vehiclesComponent = vehiclesComponent
        self.__telecomRentals = None
        super(LSVehicleInventoryPresenter, self).__init__(model=VehiclesInventoryModel)
        return

    def onPrbEntitySwitched(self, _=None):
        self.getViewModel().setBpEntityValid(self._getIsBpEntityValid())

    def createToolTipContent(self, event, contentID):
        return LSVehicleCarouselTooltipView(event.getArgument('inventoryId')) if contentID == R.views.mono.hangar.vehicle_tooltip() else super(LSVehicleInventoryPresenter, self).createToolTipContent(event=event, contentID=contentID)

    @property
    def viewModel(self):
        return super(LSVehicleInventoryPresenter, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(LSVehicleInventoryPresenter, self)._onLoading(*args, **kwargs)
        self.__telecomRentals = BigWorld.player().telecomRentals
        self.__telecomRentals.onPendingRentChanged += self.__onTelecomPendingRentChanged
        self.startGlobalListening()
        self.__updateModel()

    def _finalize(self):
        self.__vehiclesComponent = None
        self.__telecomRentals.onPendingRentChanged -= self.__onTelecomPendingRentChanged
        self.stopGlobalListening()
        super(LSVehicleInventoryPresenter, self)._finalize()
        return

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self.__onVehicleChanged),
         (self.viewModel.onGoBuyVehicle, self.__onGoBuyVehicle),
         (self.viewModel.onBuySlot, self.__onBuySlot),
         (self.viewModel.onGoRecoverVehicle, self.__onGoRecoverVehicle),
         (self.viewModel.onSelectTelecomRentalVehicle, event_dispatcher.showTelecomRentalPage),
         (self._itemsCache.onSyncCompleted, self.__onCacheResync),
         (self.viewModel.onSelect, self.__onSelectVehicle),
         (self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassSettingsChanged))

    def _getIsBpEntityValid(self):
        return self.__battlePass.isGameModeEnabled(self.__getCurrentArenaBonusType())

    def _getCallbacks(self):
        callbacksTuple = super(LSVehicleInventoryPresenter, self)._getCallbacks()
        return callbacksTuple + (('tokens', self.__onTokensUpdated),)

    @prbEntityProperty
    def __prbEntity(self):
        return None

    def __onVehicleChanged(self):
        if self._lsCtrl.isEventPrb():
            self.__updateSelectedModel()

    def __onBattlePassSettingsChanged(self, *_):
        self.__updateModel()

    def __onSelectVehicle(self, vehId):
        inventoryId = int(vehId['id'])
        self._lsVehicleCtrl.selectVehicle(inventoryId)

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
        items = self._itemsCache.items
        inventory = self._itemsCache.items.inventory
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
            model.setBpEntityValid(self._getIsBpEntityValid())
            model.setBpStatus(bpStatus)
            model.setTelecomRentStatus(self.__getTelecomRentStatus())
            model.setSlotPrice(price)
            model.setDefaultSlotPrice(defaultPrice)
            model.setSlotPriceCurrency(slotPriceCurrency)
            model.setFreeSlotsCount(emptySlotsCount)
            model.setHasDiscont(slotPrice != defaultSlotPrice)
            self.__updateSelectedModel()

    def __updateSelectedModel(self):
        vehicles = self.__vehiclesComponent.vehicles
        if not g_currentVehicle.isPresent():
            g_currentVehicle.selectVehicle(min(viewvalues(vehicles)).invID if vehicles else 0)
        if g_currentVehicle.isPresent() and g_currentVehicle.intCD in vehicles:
            with self.viewModel as model:
                model.setCurrentVehicleInventoryId(g_currentVehicle.invID)
                model.setCurrentVehicleIntCD(g_currentVehicle.intCD)
        else:
            self.viewModel.setCurrentVehicleInventoryId(VehiclesInventoryModel.NO_VEHICLE_ID)
            self.viewModel.setCurrentVehicleIntCD(VehiclesInventoryModel.NO_VEHICLE_ID)

    def __getTelecomRentStatus(self):
        if not self.__isTelecomRentalsEnabled() or self.__telecomRentals.getAvailableRentCount() == 0:
            return VehiclesInventoryModel.DISABLED
        return VehiclesInventoryModel.PENDING if self.__telecomRentals.getRentsPending() else VehiclesInventoryModel.READY_TO_SELECT

    def __isTelecomRentalsEnabled(self):
        hasTelecomRentalsActive = self.__telecomRentals.isActive()
        isRentalEnabled = self.__lobbyContext.getServerSettings().isTelecomRentalsEnabled()
        return hasTelecomRentalsActive and isRentalEnabled

    def __onTelecomPendingRentChanged(self, vehCD):
        if vehCD is not None:
            self.__updateModel()
        return

    def __onTokensUpdated(self, diff):
        if PARTNERSHIP_TOKEN_NAME in diff or ROSTER_EXPIRATION_TOKEN_NAME in diff:
            self.__updateModel()
