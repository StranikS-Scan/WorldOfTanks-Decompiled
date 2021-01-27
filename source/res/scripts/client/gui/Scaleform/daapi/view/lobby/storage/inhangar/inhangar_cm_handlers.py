# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inhangar/inhangar_cm_handlers.py
from constants import GameSeasonType, RentType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.shared.cm_handlers import ContextMenu, option, CMLabel
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import enoughCreditsForRestore, getVehicleRestoreInfo
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getTradeInVehiclesUrl, getPersonalTradeInVehiclesUrl
from gui.Scaleform.framework.managers.context_menu import CM_BUY_COLOR
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.shared import event_dispatcher as shared_events
from gui.shared.event_dispatcher import showVehicleRentRenewDialog, showShop
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from helpers import dependency
from ids_generators import SequenceIDGenerator
from skeletons.gui.game_control import IVehicleComparisonBasket, IEpicBattleMetaGameController, ITradeInController, IPersonalTradeInController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED

class VehiclesRegularCMHandler(ContextMenu):
    __sqGen = SequenceIDGenerator()
    __itemsCache = dependency.descriptor(IItemsCache)
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    __tradeInController = dependency.descriptor(ITradeInController)
    __personalTradeInController = dependency.descriptor(IPersonalTradeInController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    @option(__sqGen.next(), CMLabel.EXCHANGE)
    def exchange(self):
        self.__tradeInController.setActiveTradeOffVehicleCD(self._id)
        showShop(getTradeInVehiclesUrl())

    @option(__sqGen.next(), CMLabel.PERSONAL_EXCHANGE)
    def personalTradeExchange(self):
        self.__personalTradeInController.setActiveTradeInSaleVehicleCD(self._id)
        showShop(getPersonalTradeInVehiclesUrl())

    @option(__sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showVehicleInfo(self._id)

    @option(__sqGen.next(), CMLabel.STATS)
    def goToStats(self):
        shared_events.showVehicleStats(self._id)

    @option(__sqGen.next(), CMLabel.GO_TO_COLLECTION)
    def goToCollection(self):
        vehicle = self.__itemsCache.items.getItemByCD(self._id)
        shared_events.showCollectibleVehicles(vehicle.nationID)

    @option(__sqGen.next(), CMLabel.SELL)
    def sell(self):
        shared_events.showVehicleSellDialog(self.__itemsCache.items.getItemByCD(self._id).invID)

    @option(__sqGen.next(), CMLabel.ADD_TO_COMPARE)
    def addToCompare(self):
        self.__comparisonBasket.addVehicle(self._id)

    @option(__sqGen.next(), CMLabel.SHOW_IN_HANGAR)
    def showInHangar(self):
        shared_events.selectVehicleInHangar(self._id)

    @option(__sqGen.next(), CMLabel.NATION_CHANGE)
    def changeNation(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.CHANGE_NATION, self._id)

    def _getOptionCustomData(self, label):
        optionData = super(VehiclesRegularCMHandler, self)._getOptionCustomData(label)
        if label in CMLabel.EXCHANGE:
            optionData.visible = self.__canTradeOff()
            optionData.enabled = self.__isReadyToTradeOff()
            optionData.textColor = CM_BUY_COLOR
        elif label in CMLabel.PERSONAL_EXCHANGE:
            optionData.visible = self.__canPersonalTradeIn()
            optionData.enabled = self.__isReadyToPersonalTradeIn()
            optionData.textColor = CM_BUY_COLOR
        elif label == CMLabel.STATS:
            optionData.enabled = _canGoToStats(self._id)
        elif label == CMLabel.GO_TO_COLLECTION:
            optionData.visible = self.__isVehicleCollectorAvailable()
            optionData.enabled = self.__lobbyContext.getServerSettings().isCollectorVehicleEnabled()
        elif label == CMLabel.ADD_TO_COMPARE:
            optionData.enabled = _canAddToComparisonBasket(self._id)
        elif label == CMLabel.SELL:
            optionData.enabled = self.__canSell()
        elif label == CMLabel.NATION_CHANGE:
            optionData.visible = self.__canNationChange()
            optionData.enabled = self.__isNationChangeAvailable()
            optionData.isNew = not AccountSettings.getSettings(NATION_CHANGE_VIEWED)
        return optionData

    def __canTradeOff(self):
        vehicle = self.__itemsCache.items.getItemByCD(self._id)
        return vehicle is not None and vehicle.canTradeOff

    def __isReadyToTradeOff(self):
        vehicle = self.__itemsCache.items.getItemByCD(self._id)
        return vehicle is not None and vehicle.isReadyToTradeOff

    def __canPersonalTradeIn(self):
        vehicle = self.__itemsCache.items.getItemByCD(self._id)
        buyVehicleCDs = self.__personalTradeInController.getBuyVehicleCDs()
        return vehicle is not None and vehicle.canPersonalTradeInSale and bool(buyVehicleCDs)

    def __isReadyToPersonalTradeIn(self):
        vehicle = self.__itemsCache.items.getItemByCD(self._id)
        return vehicle is not None and vehicle.isReadyPersonalTradeInSale

    def __canSell(self):
        vehicle = self.__itemsCache.items.getItemByCD(self._id)
        return vehicle is not None and vehicle.canSell and not vehicle.isOnlyForEventBattles

    def __canNationChange(self):
        vehicle = self.__itemsCache.items.getItemByCD(self._id)
        return vehicle is not None and vehicle.hasNationGroup

    def __isNationChangeAvailable(self):
        vehicle = self.__itemsCache.items.getItemByCD(self._id)
        return vehicle is not None and vehicle.isNationChangeAvailable

    def __isVehicleCollectorAvailable(self):
        vehicle = self.__itemsCache.items.getItemByCD(self._id)
        return vehicle is not None and vehicle.isCollectible


class VehiclesRestoreCMHandler(ContextMenu):
    __sqGen = SequenceIDGenerator()
    __itemsCache = dependency.descriptor(IItemsCache)
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    @option(__sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showVehicleInfo(self._id)

    @option(__sqGen.next(), CMLabel.STATS)
    def goToStats(self):
        shared_events.showVehicleStats(self._id)

    @option(__sqGen.next(), CMLabel.RESTORE)
    def restore(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, self._id)

    @option(__sqGen.next(), CMLabel.ADD_TO_COMPARE)
    def addToCompare(self):
        self.__comparisonBasket.addVehicle(self._id)

    @option(__sqGen.next(), CMLabel.PREVIEW)
    def preview(self):
        shared_events.showVehiclePreview(self._id, previewBackCb=lambda : shared_events.showStorage(STORAGE_CONSTANTS.IN_HANGAR, STORAGE_CONSTANTS.VEHICLES_TAB_RESTORE), previewAlias=VIEW_ALIAS.LOBBY_STORAGE)

    def _getOptionCustomData(self, label):
        optionData = super(VehiclesRestoreCMHandler, self)._getOptionCustomData(label)
        if label == CMLabel.STATS:
            optionData.enabled = _canGoToStats(self._id)
        elif label == CMLabel.RESTORE:
            optionData.enabled = self.__canRestore()
        elif label == CMLabel.ADD_TO_COMPARE:
            optionData.enabled = _canAddToComparisonBasket(self._id)
        return optionData

    def __canRestore(self):
        item = self.__itemsCache.items.getItemByCD(self._id)
        if item is not None:
            restoreCreditsPrice = item.restorePrice.credits
            enoughCredits, _ = enoughCreditsForRestore(restoreCreditsPrice, self.__itemsCache)
            restoreAvailable, _, _, _ = getVehicleRestoreInfo(item)
            return enoughCredits and restoreAvailable
        else:
            return False


class VehiclesRentedCMHandler(ContextMenu):
    __sqGen = SequenceIDGenerator()
    __itemsCache = dependency.descriptor(IItemsCache)
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    @option(__sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showVehicleInfo(self._id)

    @option(__sqGen.next(), CMLabel.STATS)
    def goToStats(self):
        shared_events.showVehicleStats(self._id)

    @option(__sqGen.next(), CMLabel.BUY)
    def buy(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, self._id)

    @option(__sqGen.next(), CMLabel.RENEW_RENT)
    def renewRent(self):
        vehicle = self.__itemsCache.items.getItemByCD(self._id)
        rentRenewCycle = vehicle.rentInfo.getAvailableRentRenewCycleInfoForSeason(GameSeasonType.EPIC)
        showVehicleRentRenewDialog(self._id, RentType.SEASON_CYCLE_RENT, rentRenewCycle.ID, GameSeasonType.EPIC)

    @option(__sqGen.next(), CMLabel.REMOVE)
    def remove(self):
        shared_events.showVehicleSellDialog(self.__itemsCache.items.getItemByCD(self._id).invID)

    @option(__sqGen.next(), CMLabel.ADD_TO_COMPARE)
    def addToCompare(self):
        self.__comparisonBasket.addVehicle(self._id)

    @option(__sqGen.next(), CMLabel.SHOW_IN_HANGAR)
    def showInHangar(self):
        shared_events.selectVehicleInHangar(self._id)

    def _getOptionCustomData(self, label):
        optionData = super(VehiclesRentedCMHandler, self)._getOptionCustomData(label)
        if label == CMLabel.STATS:
            optionData.enabled = _canGoToStats(self._id)
        elif label == CMLabel.ADD_TO_COMPARE:
            optionData.enabled = _canAddToComparisonBasket(self._id)
        elif label == CMLabel.BUY:
            optionData.enabled = self.__canBuy()
        elif label == CMLabel.RENEW_RENT:
            optionData.enabled = self.__canRenewRent()
        elif label == CMLabel.REMOVE:
            optionData.enabled = self.__canRemove()
        return optionData

    def __canBuy(self):
        items = self.__itemsCache.items
        vehicle = self.__itemsCache.items.getItemByCD(self._id)
        return vehicle is not None and vehicle.mayObtainWithMoneyExchange(items.stats.money, items.shop.exchangeRate)

    def __canRenewRent(self):
        vehicle = self.__itemsCache.items.getItemByCD(self._id)
        canRenew = False
        if vehicle is None:
            return canRenew
        else:
            if vehicle.isOnlyForEpicBattles:
                canRenew = vehicle.rentInfo.canCycleRentRenewForSeason(GameSeasonType.EPIC)
            elif vehicle.isOnlyForBob:
                canRenew = vehicle.rentInfo.canCycleRentRenewForSeason(GameSeasonType.BOB)
            return canRenew

    def __canRemove(self):
        vehicle = self.__itemsCache.items.getItemByCD(self._id)
        return vehicle is not None and vehicle.canSell and vehicle.rentalIsOver


@dependency.replace_none_kwargs(comparisonBasket=IVehicleComparisonBasket, itemsCache=IItemsCache)
def _canAddToComparisonBasket(vehicleCD, comparisonBasket=None, itemsCache=None):
    vehicle = itemsCache.items.getItemByCD(vehicleCD)
    return vehicle is not None and comparisonBasket.isEnabled() and comparisonBasket.isReadyToAdd(vehicle)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _canGoToStats(vehicleCD, itemsCache=None):
    accDossier = itemsCache.items.getAccountDossier(None)
    if accDossier is not None:
        wasInBattleSet = set(accDossier.getTotalStats().getVehicles().keys())
        wasInBattleSet.update(accDossier.getGlobalMapStats().getVehicles().keys())
        if vehicleCD in wasInBattleSet:
            return True
    return False
