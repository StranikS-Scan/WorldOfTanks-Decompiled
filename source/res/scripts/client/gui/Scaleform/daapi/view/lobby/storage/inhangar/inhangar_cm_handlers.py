# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inhangar/inhangar_cm_handlers.py
from constants import GameSeasonType, RentType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.cm_handlers import ContextMenu, option, CMLabel
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import enoughCreditsForRestore, getVehicleRestoreInfo
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.shared import event_dispatcher as shared_events
from gui.shared.event_dispatcher import showVehicleRentRenewDialog
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from helpers import dependency
from ids_generators import SequenceIDGenerator
from skeletons.gui.game_control import IVehicleComparisonBasket, IEpicBattleMetaGameController
from skeletons.gui.shared import IItemsCache

class VehiclesRegularCMHandler(ContextMenu):
    _sqGen = SequenceIDGenerator()
    _itemsCache = dependency.descriptor(IItemsCache)
    _comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    @option(_sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showVehicleInfo(self._id)

    @option(_sqGen.next(), CMLabel.STATS)
    def goToStats(self):
        shared_events.showVehicleStats(self._id)

    @option(_sqGen.next(), CMLabel.SELL)
    def sell(self):
        shared_events.showVehicleSellDialog(self._itemsCache.items.getItemByCD(self._id).invID)

    @option(_sqGen.next(), CMLabel.ADD_TO_COMPARE)
    def addToCompare(self):
        self._comparisonBasket.addVehicle(self._id)

    @option(_sqGen.next(), CMLabel.SHOW_IN_HANGAR)
    def showInHangar(self):
        shared_events.selectVehicleInHangar(self._id)

    def _getOptionCustomData(self, label):
        if label == CMLabel.STATS:
            return {'enabled': _canGoToStats(self._id, self._itemsCache)}
        elif label == CMLabel.ADD_TO_COMPARE:
            return {'enabled': not self._comparisonBasket.isFull()}
        else:
            return {'enabled': self.__canSell()} if label == CMLabel.SELL else None

    def __canSell(self):
        vehicle = self._itemsCache.items.getItemByCD(self._id)
        return vehicle and vehicle.canSell and not vehicle.isOnlyForEventBattles


class VehiclesRestoreCMHandler(ContextMenu):
    _sqGen = SequenceIDGenerator()
    _itemsCache = dependency.descriptor(IItemsCache)
    _comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    @option(_sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showVehicleInfo(self._id)

    @option(_sqGen.next(), CMLabel.STATS)
    def goToStats(self):
        shared_events.showVehicleStats(self._id)

    @option(_sqGen.next(), CMLabel.RESTORE)
    def restore(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, self._id)

    @option(_sqGen.next(), CMLabel.ADD_TO_COMPARE)
    def addToCompare(self):
        self._comparisonBasket.addVehicle(self._id)

    @option(_sqGen.next(), CMLabel.PREVIEW)
    def preview(self):
        shared_events.showVehiclePreview(self._id, previewBackCb=lambda : shared_events.showStorage(STORAGE_CONSTANTS.IN_HANGAR, STORAGE_CONSTANTS.VEHICLES_TAB_RESTORE), previewAlias=VIEW_ALIAS.LOBBY_STORAGE)

    def _getOptionCustomData(self, label):
        if label == CMLabel.STATS:
            return {'enabled': _canGoToStats(self._id, self._itemsCache)}
        elif label == CMLabel.RESTORE:
            return {'enabled': self.__canRestore()}
        else:
            return {'enabled': not self._comparisonBasket.isFull()} if label == CMLabel.ADD_TO_COMPARE else None

    def __canRestore(self):
        item = self._itemsCache.items.getItemByCD(self._id)
        restoreCreditsPrice = item.restorePrice.credits
        enoughCredits, _ = enoughCreditsForRestore(restoreCreditsPrice, self._itemsCache)
        restoreAvailable, _, _, _ = getVehicleRestoreInfo(item)
        return enoughCredits and restoreAvailable


class VehiclesRentedCMHandler(ContextMenu):
    _sqGen = SequenceIDGenerator()
    _itemsCache = dependency.descriptor(IItemsCache)
    _comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    _epicController = dependency.descriptor(IEpicBattleMetaGameController)

    @option(_sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showVehicleInfo(self._id)

    @option(_sqGen.next(), CMLabel.STATS)
    def goToStats(self):
        shared_events.showVehicleStats(self._id)

    @option(_sqGen.next(), CMLabel.BUY)
    def buy(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, self._id)

    @option(_sqGen.next(), CMLabel.RENEW_RENT)
    def renewRent(self):
        vehicle = self._itemsCache.items.getItemByCD(self._id)
        rentRenewCycle = vehicle.rentInfo.getAvailableRentRenewCycleInfoForSeason(GameSeasonType.EPIC)
        showVehicleRentRenewDialog(self._id, RentType.SEASON_CYCLE_RENT, rentRenewCycle.ID, GameSeasonType.EPIC)

    @option(_sqGen.next(), CMLabel.REMOVE)
    def remove(self):
        shared_events.showVehicleSellDialog(self._itemsCache.items.getItemByCD(self._id).invID)

    @option(_sqGen.next(), CMLabel.ADD_TO_COMPARE)
    def addToCompare(self):
        self._comparisonBasket.addVehicle(self._id)

    @option(_sqGen.next(), CMLabel.SHOW_IN_HANGAR)
    def showInHangar(self):
        shared_events.selectVehicleInHangar(self._id)

    def _getOptionCustomData(self, label):
        if label == CMLabel.STATS:
            return {'enabled': _canGoToStats(self._id, self._itemsCache)}
        elif label == CMLabel.ADD_TO_COMPARE:
            return {'enabled': not self._comparisonBasket.isFull()}
        elif label == CMLabel.BUY:
            return {'enabled': self.__canBuy()}
        elif label == CMLabel.RENEW_RENT:
            return {'enabled': self.__canRenewRent()}
        else:
            return {'enabled': self.__canRemove()} if label == CMLabel.REMOVE else None

    def __canBuy(self):
        items = self._itemsCache.items
        vehicle = self._itemsCache.items.getItemByCD(self._id)
        return vehicle and vehicle.mayObtainWithMoneyExchange(items.stats.money, items.shop.exchangeRate)

    def __canRenewRent(self):
        vehicle = self._itemsCache.items.getItemByCD(self._id)
        return vehicle and vehicle.isOnlyForEpicBattles and vehicle.rentInfo.canCycleRentRenewForSeason(GameSeasonType.EPIC)

    def __canRemove(self):
        vehicle = self._itemsCache.items.getItemByCD(self._id)
        return vehicle and vehicle.canSell and vehicle.rentalIsOver


def _canGoToStats(vehicleCD, itemsCache):
    accDossier = itemsCache.items.getAccountDossier(None)
    if accDossier:
        wasInBattleSet = set(accDossier.getTotalStats().getVehicles().keys())
        wasInBattleSet.update(accDossier.getGlobalMapStats().getVehicles().keys())
        if vehicleCD in wasInBattleSet:
            return True
    return False
