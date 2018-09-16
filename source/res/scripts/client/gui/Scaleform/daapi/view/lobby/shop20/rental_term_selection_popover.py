# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shop20/rental_term_selection_popover.py
import constants
from gui.Scaleform.daapi.view.meta.RentalTermSelectionPopoverMeta import RentalTermSelectionPopoverMeta
from gui.Scaleform.locale.STORE import STORE
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import ShopEvent
from gui.shared.formatters import text_styles, getItemPricesVO, getMoneyVO
from gui.shared.money import Money
from gui.shared.gui_items.gui_item_economics import ItemPrice
from helpers import dependency, i18n, time_utils
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
_NOT_RENT_IDX = -1

class RentalTermSelectionPopover(RentalTermSelectionPopoverMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(RentalTermSelectionPopover, self).__init__()
        data = ctx.get('data')
        self.__vehicleIntCD = int(data.vehicleIntCD)
        self.__selectedRentTerm = int(data.selectedRentTerm)

    def selectTerm(self, itemId):
        self.fireEvent(ShopEvent(ShopEvent.SELECT_RENT_TERM, ctx=itemId), EVENT_BUS_SCOPE.LOBBY)
        self.itemsCache.onSyncCompleted -= self.__onItemCacheSyncCompleted
        self.destroy()

    def _populate(self):
        super(RentalTermSelectionPopover, self)._populate()
        self.as_setInitDataS(self.__getInitialVO())
        self.itemsCache.onSyncCompleted += self.__onItemCacheSyncCompleted

    def __onItemCacheSyncCompleted(self, *args):
        self.as_setInitDataS(self.__getInitialVO())

    def __getInitialVO(self):
        vehicle = self.itemsCache.items.getItemByCD(self.__vehicleIntCD)
        rentalTermSlots = []
        statsMoney = self.itemsCache.items.stats.money
        isRestoreAvailable = vehicle.isRestoreAvailable()
        if isRestoreAvailable:
            isEnough = vehicle.restorePrice <= statsMoney or isIngameShopEnabled()
            isEnoughStatuses = Money.makeFromMoneyTuple((isEnough, isEnough, isEnough))
            enabled = isRestoreAvailable or not (constants.IS_CHINA and vehicle.rentalIsActive)
            rentalTermSlots.append({'itemId': -1,
             'label': i18n.makeString(STORE.BUYVEHICLEWINDOW_RESTORE),
             'price': getItemPricesVO(ItemPrice(vehicle.restorePrice, vehicle.restorePrice)),
             'enabled': enabled,
             'selected': self.__selectedRentTerm <= _NOT_RENT_IDX,
             'isEnough': isEnough,
             'isEnoughStatuses': getMoneyVO(isEnoughStatuses)})
        rentPackages = vehicle.rentPackages
        for rentPackageId in xrange(len(rentPackages)):
            rentPackage = rentPackages[rentPackageId]
            days = rentPackage['days']
            standartRentDays = STORE.getRentTermDays(days)
            price = ItemPrice(rentPackage['rentPrice'], rentPackage['defaultRentPrice'])
            isEnough = statsMoney >= price.price or isIngameShopEnabled()
            isEnoughStatuses = Money.makeFromMoneyTuple((isEnough, isEnough, isEnough))
            enabled = vehicle.maxRentDuration - vehicle.rentLeftTime >= days * time_utils.ONE_DAY
            rentalTermSlots.append({'itemId': rentPackageId,
             'label': standartRentDays if standartRentDays is not None else i18n.makeString(STORE.RENTALTERMSELECTIONPOPOVER_TERMSLOTANY, days=days),
             'price': getItemPricesVO(price),
             'enabled': enabled,
             'selected': self.__selectedRentTerm == days,
             'isEnough': isEnough,
             'isEnoughStatuses': getMoneyVO(isEnoughStatuses)})

        if not isRestoreAvailable:
            isEnough = vehicle.buyPrices.itemPrice.price <= statsMoney or isIngameShopEnabled()
            isEnoughStatuses = Money.makeFromMoneyTuple((isEnough, isEnough, isEnough))
            enabled = not vehicle.isDisabledForBuy and not vehicle.isHidden
            rentalTermSlots.append({'itemId': _NOT_RENT_IDX,
             'label': i18n.makeString(STORE.RENTALTERMSELECTIONPOPOVER_TERMSLOTUNLIM),
             'price': getItemPricesVO(vehicle.buyPrices.itemPrice),
             'enabled': enabled,
             'selected': self.__selectedRentTerm <= _NOT_RENT_IDX,
             'isEnough': isEnough,
             'isEnoughStatuses': getMoneyVO(isEnoughStatuses)})
        return {'titleLabel': text_styles.highTitle(STORE.RENTALTERMSELECTIONPOPOVER_TITLELABEL),
         'rentalTermSlots': rentalTermSlots}
