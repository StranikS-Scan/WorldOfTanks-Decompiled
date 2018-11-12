# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/inhangar/inhangar_cm_handlers.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.cm_handlers import ContextMenu, option, CMLabel
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import enoughCreditsForRestore, getVehicleRestoreInfo
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from helpers import dependency
from ids_generators import SequenceIDGenerator
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache

class VehiclesRegularCMHandler(ContextMenu):
    sqGen = SequenceIDGenerator()
    itemsCache = dependency.descriptor(IItemsCache)
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    @option(sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showVehicleInfo(self._id)

    @option(sqGen.next(), CMLabel.SELL)
    def sell(self):
        shared_events.showVehicleSellDialog(self.itemsCache.items.getItemByCD(self._id).invID)

    @option(sqGen.next(), CMLabel.ADD_TO_COMPARE)
    def addToCompare(self):
        self.comparisonBasket.addVehicle(self._id)

    @option(sqGen.next(), CMLabel.SHOW_IN_HANGAR)
    def showInHangar(self):
        shared_events.selectVehicleInHangar(self._id)

    def _getOptionCustomData(self, label):
        return {'enabled': not self.comparisonBasket.isFull()} if label == CMLabel.ADD_TO_COMPARE else None


class VehiclesRestoreCMHandler(ContextMenu):
    sqGen = SequenceIDGenerator()
    itemsCache = dependency.descriptor(IItemsCache)
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    @option(sqGen.next(), CMLabel.INFORMATION)
    def showInfo(self):
        shared_events.showVehicleInfo(self._id)

    @option(sqGen.next(), CMLabel.RESTORE)
    def restore(self):
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, self._id)

    @option(sqGen.next(), CMLabel.ADD_TO_COMPARE)
    def addToCompare(self):
        self.comparisonBasket.addVehicle(self._id)

    @option(sqGen.next(), CMLabel.PREVIEW)
    def preview(self):
        shared_events.showVehiclePreview(self._id, previewBackCb=lambda : shared_events.showStorage(STORAGE_CONSTANTS.IN_HANGAR, STORAGE_CONSTANTS.VEHICLES_TAB_RESTORE), previewAlias=VIEW_ALIAS.LOBBY_STORAGE)

    def _getOptionCustomData(self, label):
        if label == CMLabel.RESTORE:
            return {'enabled': self.__canRestore()}
        else:
            return {'enabled': not self.comparisonBasket.isFull()} if label == CMLabel.ADD_TO_COMPARE else None

    def __canRestore(self):
        item = self.itemsCache.items.getItemByCD(self._id)
        restoreCreditsPrice = item.restorePrice.credits
        enoughCredits, _ = enoughCreditsForRestore(restoreCreditsPrice, self.itemsCache)
        restoreAvailable, _, _, _ = getVehicleRestoreInfo(item)
        return enoughCredits and restoreAvailable
