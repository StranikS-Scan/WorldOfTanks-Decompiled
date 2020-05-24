# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/offers/offer_gift_dialog.py
import logging
from functools import partial
from account_helpers.offers.events_data import OfferGift, OfferEventData
from constants import RentType
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.impl import backport
from gui.impl.dialogs.builders import SimpleDialogBuilder, PureDialogBuilder
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogButtons
from gui.impl.pub.pure_dialog_window import PureDialogWindow
from gui.impl.pub.simple_dialog_window import SimpleDialogWindow
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
_logger = logging.getLogger(__name__)
RENT_VALUE_DESCR_BY_TYPE = {RentType.TIME_RENT: R.strings.offers.description.rentValue.days(),
 RentType.WINS_RENT: R.strings.offers.description.rentValue.wins(),
 RentType.BATTLES_RENT: R.strings.offers.description.rentValue.battles()}

class OffersDialogWindowMixin(object):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self, offerID, *args, **kwargs):
        super(OffersDialogWindowMixin, self).__init__(*args, **kwargs)
        self._offerID = offerID

    def _initialize(self):
        super(OffersDialogWindowMixin, self)._initialize()
        self._offersProvider.onOffersUpdated += self._onOffersUpdated
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def _finalize(self):
        super(OffersDialogWindowMixin, self)._finalize()
        self._offersProvider.onOffersUpdated -= self._onOffersUpdated
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def __onServerSettingsChange(self, *args, **kwargs):
        if not self._lobbyContext.getServerSettings().isOffersEnabled():
            from gui.shared import event_dispatcher
            event_dispatcher.showHangar()
            self.destroy()

    def _onOffersUpdated(self):
        from gui.shared import event_dispatcher
        offer = self._offersProvider.getOffer(self._offerID)
        if offer is None or not offer.isOfferAvailable:
            if self._offersProvider.getAvailableOffers():
                event_dispatcher.showStorage(defaultSection=STORAGE_CONSTANTS.OFFERS)
            else:
                event_dispatcher.showHangar()
            self.destroy()
        return


class OffersSimpleDialogWindow(OffersDialogWindowMixin, SimpleDialogWindow):
    pass


class OffersPureDialogWindow(OffersDialogWindowMixin, PureDialogWindow):
    pass


class _OffersSimpleDialogBuilder(SimpleDialogBuilder):
    _offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self, offerID, giftID):
        super(_OffersSimpleDialogBuilder, self).__init__()
        self._windowClass = partial(OffersSimpleDialogWindow, offerID)
        self._offer = self._offersProvider.getOffer(offerID)
        self._gift = self._offer.getGift(giftID)
        self.setTitle(self.title)
        self.setFormattedMessage(self.description)

    @property
    def title(self):
        if self._gift.rentType == RentType.NO_RENT:
            titleRes = R.strings.offers.giftDialog.title.tank()
        else:
            titleRes = R.strings.offers.giftDialog.title.tankRent()
        return titleRes

    @property
    def description(self):
        vehicle = self._gift.bonus.displayedItem
        if self._gift.rentType == RentType.NO_RENT:
            base = R.strings.offers.giftDialog.description.noRent()
        elif vehicle.isRented:
            base = R.strings.offers.giftDialog.description.prolongRent()
        else:
            base = R.strings.offers.giftDialog.description.newRent()
        strArgs = dict(tankName=text_styles.neutralBig(self._gift.bonus.displayedItem.shortUserName))
        if self._gift.rentType != RentType.NO_RENT:
            rentValue = backport.text(RENT_VALUE_DESCR_BY_TYPE[self._gift.rentType])
            strArgs['rentValue'] = rentValue % dict(value=self._gift.rentValue)
        return backport.text(base, **strArgs)


class _OffersPureDialogBuilder(PureDialogBuilder):
    _offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self, offerID, giftID, cdnTitle=''):
        super(_OffersPureDialogBuilder, self).__init__()
        self._windowClass = partial(OffersPureDialogWindow, offerID)
        self._offer = self._offersProvider.getOffer(offerID)
        self._gift = self._offer.getGift(giftID)
        self._cdnTitle = cdnTitle
        self.setFormattedTitle(self.title)

    @property
    def title(self):
        if self._gift.fromCdn:
            giftName = self._cdnTitle
        else:
            giftName = self._gift.title
        giftName = giftName.format(neutralOpen='', neutralClose='', expTagOpen='', expTagClose='')
        return backport.text(R.strings.offers.giftDialog.title.common(), name=giftName)


def makeOfferGiftDialog(offerID, giftID, cdnTitle=''):
    offersProvider = dependency.instance(IOffersDataProvider)
    offer = offersProvider.getOffer(offerID)
    if offer is None:
        _logger.error('Wrong offerID=%s', offerID)
    gift = offer.getGift(giftID)
    if gift is None:
        _logger.error('Wrong giftID=%s for offerID=%s', offerID, giftID)
    if gift.isVehicle:
        builder = _OffersSimpleDialogBuilder(offerID, giftID)
    else:
        builder = _OffersPureDialogBuilder(offerID, giftID, cdnTitle)
    builder.addButton(DialogButtons.SUBMIT, R.strings.offers.giftDialog.submit(), isFocused=True)
    builder.addButton(DialogButtons.CANCEL, R.strings.offers.giftDialog.cancel(), isFocused=False)
    return builder
