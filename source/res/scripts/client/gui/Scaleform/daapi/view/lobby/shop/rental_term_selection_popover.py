# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/shop/rental_term_selection_popover.py
import constants
from constants import RentType, GameSeasonType
from rent_common import parseRentID, isWithinMaxRentTime, SeasonRentDuration
from soft_exception import SoftException
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.Scaleform.daapi.view.meta.RentalTermSelectionPopoverMeta import RentalTermSelectionPopoverMeta
from gui.Scaleform.locale.STORE import STORE
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import ShopEvent
from gui.shared.formatters import text_styles, getItemPricesVO, getMoneyVO
from gui.shared.money import Money
from gui.shared.gui_items.gui_item_economics import ItemPrice
from helpers import dependency, i18n
from skeletons.gui.shared import IItemsCache
_NOT_RENT_IDX = -1
_SEASON_RENT_TERMS = {GameSeasonType.EPIC: {RentType.SEASON_RENT: STORE.RENTALTERMSELECTIONPOPOVER_TERMSLOTSEASON_EPICSEASON,
                       RentType.SEASON_CYCLE_RENT: STORE.RENTALTERMSELECTIONPOPOVER_TERMSLOTSEASON_EPICCYCLE},
 GameSeasonType.RANKED: {RentType.SEASON_RENT: STORE.RENTALTERMSELECTIONPOPOVER_TERMSLOTSEASON_RANKEDSEASON,
                         RentType.SEASON_CYCLE_RENT: STORE.RENTALTERMSELECTIONPOPOVER_TERMSLOTSEASON_RANKEDCYCLE}}

class RentalTermSelectionPopover(RentalTermSelectionPopoverMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(RentalTermSelectionPopover, self).__init__()
        data = ctx.get('data')
        self.__vehicleIntCD = int(data.vehicleIntCD)
        self.__selectedRentID = int(data.selectedRentTerm)

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
        isEnoughStatuses = getMoneyVO(Money.makeFromMoneyTuple((True, True, True)))
        rentalTermSlots = []
        isRestoreAvailable = vehicle.isRestoreAvailable()
        if isRestoreAvailable:
            enabled = isRestoreAvailable or not (constants.IS_CHINA and vehicle.rentalIsActive)
            rentalTermSlots.append({'itemId': -1,
             'label': backport.text(R.strings.hangar.buyVehicleWindow.restore()),
             'price': getItemPricesVO(ItemPrice(vehicle.restorePrice, vehicle.restorePrice)),
             'enabled': enabled,
             'selected': self.__selectedRentID <= _NOT_RENT_IDX,
             'isEnoughStatuses': isEnoughStatuses})
        rentPackages = vehicle.rentPackages
        currentSeasonRent = vehicle.currentSeasonRent
        isSeasonRented = currentSeasonRent is not None
        for rentPackageIdx, rentPackage in enumerate(rentPackages):
            rentID = rentPackage['rentID']
            rentType, packageID = parseRentID(rentID)
            if rentType == constants.RentType.TIME_RENT:
                days = packageID
                standardRentDays = STORE.getRentTermDays(days)
                if standardRentDays is not None:
                    label = standardRentDays
                else:
                    label = i18n.makeString(STORE.RENTALTERMSELECTIONPOPOVER_TERMSLOTANY, days=days)
                inMaxRentTime = isWithinMaxRentTime(vehicle.maxRentDuration, vehicle.rentLeftTime, days)
                enabled = not isSeasonRented and inMaxRentTime
            elif rentType in (constants.RentType.SEASON_RENT, constants.RentType.SEASON_CYCLE_RENT):
                seasonType = rentPackage['seasonType']
                label = i18n.makeString(_SEASON_RENT_TERMS[seasonType][rentType])
                if rentType == constants.RentType.SEASON_RENT:
                    enabled = not isSeasonRented or isSeasonRented and currentSeasonRent.duration == SeasonRentDuration.SEASON_CYCLE
                else:
                    enabled = not isSeasonRented
            else:
                raise SoftException('Unsupported rental type [{}]!'.format(rentType))
            price = ItemPrice(rentPackage['rentPrice'], rentPackage['defaultRentPrice'])
            rentalTermSlots.append({'itemId': rentPackageIdx,
             'label': label,
             'price': getItemPricesVO(price),
             'enabled': enabled,
             'selected': self.__selectedRentID == rentID,
             'isEnoughStatuses': isEnoughStatuses})

        if not isRestoreAvailable:
            enabled = not vehicle.isDisabledForBuy and not vehicle.isHidden
            rentalTermSlots.append({'itemId': _NOT_RENT_IDX,
             'label': i18n.makeString(STORE.RENTALTERMSELECTIONPOPOVER_TERMSLOTUNLIM),
             'price': getItemPricesVO(vehicle.buyPrices.itemPrice),
             'enabled': enabled,
             'selected': self.__selectedRentID <= _NOT_RENT_IDX,
             'isEnoughStatuses': isEnoughStatuses})
        return {'titleLabel': text_styles.highTitle(STORE.RENTALTERMSELECTIONPOPOVER_TITLELABEL),
         'rentalTermSlots': rentalTermSlots}
