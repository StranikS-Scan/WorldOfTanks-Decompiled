# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/offers/offer_gifts_window.py
import logging
from functools import partial
import ResMgr
from adisp import adisp_process, adisp_async
from constants import RentType, PREMIUM_ENTITLEMENTS
from PlayerEvents import g_playerEvents
from gui import SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.genConsts.STORAGE_CONSTANTS import STORAGE_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.offers import getGfImagePath
from gui.shared import event_dispatcher
from gui.shared.gui_items.processors.offers import ReceiveOfferGiftProcessor
from gui.shared.money import Currency
from helpers import dependency, time_utils
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.gen.view_models.views.lobby.offers.gift_model import GiftModel
from gui.impl.gen.view_models.views.lobby.offers.offer_model import OfferModel
from gui.impl.pub import ViewImpl
from shared_utils import awaitNextFrame
from skeletons.gui.game_control import IExternalLinksController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider, IOffersNovelty
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from web.cache.web_cache import CachePrefetchResult
_logger = logging.getLogger(__name__)
RENT_TYPE_TO_MODEL_CONSTANT = {RentType.NO_RENT: GiftModel.RENT_TYPE_NO,
 RentType.TIME_RENT: GiftModel.RENT_TYPE_TIME,
 RentType.BATTLES_RENT: GiftModel.RENT_TYPE_BATTLES,
 RentType.WINS_RENT: GiftModel.RENT_TYPE_WINS}
BONUSES_WITHOUT_COUNTER = {Currency.CREDITS,
 Currency.GOLD,
 Currency.CRYSTAL,
 'freeXP',
 PREMIUM_ENTITLEMENTS.PLUS,
 'vehicles'}

class OfferGiftsWindow(ViewImpl):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)
    _offersProvider = dependency.descriptor(IOffersDataProvider)
    _offersNovelty = dependency.descriptor(IOffersNovelty)
    _externalBrowser = dependency.descriptor(IExternalLinksController)

    def __init__(self, layoutID, offerID, overrideSuccessCallback=None):
        settings = ViewSettings(layoutID=layoutID, flags=ViewFlags.LOBBY_SUB_VIEW, model=OfferModel())
        super(OfferGiftsWindow, self).__init__(settings)
        self._offerID = offerID
        self.__overrideSuccessCallback = overrideSuccessCallback

    @property
    def _serverSettings(self):
        return self._lobbyContext.getServerSettings()

    @property
    def _viewModel(self):
        return self.getViewModel()

    @property
    def _offerItem(self):
        return self._offersProvider.getOffer(self._offerID)

    def _initialize(self, *args, **kwargs):
        super(OfferGiftsWindow, self)._initialize()
        self._viewModel.onBack += self._onBack
        self._viewModel.onLearnMore += self._onLearnMore
        g_playerEvents.onAccountBecomeNonPlayer += self._onBecomeNonPlayer
        self._serverSettings.onServerSettingsChange += self._onServerSettingsRecync
        self._itemsCache.onSyncCompleted += self._onItemsCacheResync
        self._offersProvider.onOffersUpdated += self._onOffersUpdated

    def _finalize(self):
        super(OfferGiftsWindow, self)._finalize()
        self._viewModel.onBack -= self._onBack
        self._viewModel.onLearnMore -= self._onLearnMore
        g_playerEvents.onAccountBecomeNonPlayer -= self._onBecomeNonPlayer
        self._serverSettings.onServerSettingsChange -= self._onServerSettingsRecync
        self._itemsCache.onSyncCompleted -= self._onItemsCacheResync
        self._offersProvider.onOffersUpdated -= self._onOffersUpdated

    @adisp_process
    def _onLoading(self, *args, **kwargs):
        super(OfferGiftsWindow, self)._onLoading(*args, **kwargs)
        offerItem = self._offerItem
        if offerItem is not None:
            result = yield self.syncOfferResources()
            if result != CachePrefetchResult.SUCCESS:
                yield awaitNextFrame()
                event_dispatcher.showStorage(defaultSection=STORAGE_CONSTANTS.OFFERS)
                self.destroyWindow()
                return
            self._offersNovelty.saveAsSeen(self._offerID)
            with self._viewModel.transaction() as model:
                localization = ResMgr.openSection(self._offersProvider.getCdnResourcePath(offerItem.cdnLocFilePath, relative=False))
                description = localization.readString('description') if localization else ''
                linkText = localization.readString('linkText') if localization else ''
                tokenIcon = backport.image(R.images.gui.maps.icons.offers.token())
                if offerItem.cdnGiftsTokenImgPath:
                    tokenIcon = getGfImagePath(self._offersProvider.getCdnResourcePath(offerItem.cdnGiftsTokenImgPath))
                signSmall = backport.image(R.images.gui.maps.icons.offers.sign_small())
                if offerItem.cdnSignSmallImgPath:
                    signSmall = getGfImagePath(self._offersProvider.getCdnResourcePath(offerItem.cdnSignSmallImgPath))
                signBig = backport.image(R.images.gui.maps.icons.offers.sign())
                if offerItem.cdnSignBigImgPath:
                    signBig = getGfImagePath(self._offersProvider.getCdnResourcePath(offerItem.cdnSignBigImgPath))
                model.setId(offerItem.id)
                model.setDescription(description)
                model.setLearnMore(linkText)
                model.setTokensIcon(tokenIcon)
                model.setSignImageSmall(signSmall)
                model.setSignImageLarge(signBig)
                model.setShowPrice(offerItem.showPrice)
                title = localization.readString('name') if localization else ''
                model.setName(title)
                model.setBackground(getGfImagePath(self._offersProvider.getCdnResourcePath(offerItem.cdnGiftsBackgroundPath)))
                self._setDynamicInfo(model)
                self._generateGifts(model)
        return

    @adisp_async
    @adisp_process
    def syncOfferResources(self, callback=None):
        Waiting.show('loadContent')
        result = yield self._offersProvider.isCdnResourcesReady()
        Waiting.hide('loadContent')
        callback(result)

    def _setDynamicInfo(self, offerModel):
        offerItem = self._offerItem
        if offerItem.showPrice:
            offerModel.setTokens(offerItem.availableTokens)
        offerModel.setClicksCount(offerItem.clicksCount)
        timeLeft = float(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(offerItem.expiration)))
        offerModel.setExpiration(timeLeft)

    def _generateGifts(self, model):
        giftsContainer = model.gifts.getItems()
        giftsContainer.clear()
        sortedGifts = sorted(self._offerItem.availableGifts, key=lambda item: item.id)
        giftsContainer.reserve(len(sortedGifts))
        for gift in sortedGifts:
            giftModel = GiftModel()
            title, description, icon, count, price = self._getGiftResources(gift)
            giftModel.setId(gift.id)
            giftModel.setRentType(RENT_TYPE_TO_MODEL_CONSTANT[gift.rentType])
            giftModel.setRentValue(gift.rentValue)
            giftModel.setInventoryCount(gift.isVehicle and gift.inventoryCount)
            giftModel.setCount(count)
            giftModel.setTitle(title)
            giftModel.setDescription(description)
            giftModel.setIcon(icon)
            giftModel.setHighlight(gift.highlight)
            giftModel.setButtonLabel(gift.buttonLabel)
            if gift.nationFlag:
                giftModel.setNationFlag(getGfImagePath(gift.nationFlag))
            if self._offerItem.showPrice:
                giftModel.setPrice(price)
            notEnoughTokens = self._offerItem.availableTokens < price
            giftModel.setIsNotEnoughMoney(notEnoughTokens)
            giftCount = self._offerItem.getGiftAvailableCount(gift.id)
            giftDisabled = notEnoughTokens or gift.isDisabled or not giftCount
            giftModel.setIsDisabled(giftDisabled)
            if giftCount > 0:
                giftModel.setAvailableCount(not gift.isVehicle and giftCount)
            giftsContainer.addViewModel(giftModel)

        model.gifts.onItemClicked += self._onGiftClicked
        giftsContainer.invalidate()

    def _getGiftResources(self, gift):
        if gift.fromCdn:
            locFile = ResMgr.openSection(self._offersProvider.getCdnResourcePath(gift.cdnLocFilePath, relative=False))
            title = locFile.readString('name') if locFile else ''
            description = locFile.readString('description') if locFile else ''
            icon = self._offersProvider.getCdnResourcePath(gift.cdnImagePath)
            count = 0
        else:
            title = gift.title
            description = gift.description
            icon = gift.icon
            count = gift.giftCount if gift.bonusType not in BONUSES_WITHOUT_COUNTER else 0
        price = gift.price
        imgPath = getGfImagePath(icon) or ''
        return (title,
         description,
         imgPath,
         count,
         price)

    def _onGiftClicked(self, args):
        giftID = args.get('index')
        gift = self._offerItem.getGift(giftID)
        if gift is None:
            _logger.error('Unknown gift id=%s for offer id=%s', giftID, self._offerID)
            return
        else:
            localization = ResMgr.openSection(self._offersProvider.getCdnResourcePath(gift.cdnLocFilePath, relative=False))
            onGiftConfirm = partial(self._onGiftConfirm, self._offerID, giftID, cdnTitle=localization.readString('name') if localization else '', cdnDescription=localization.readString('description') if localization else '', cdnIcon=getGfImagePath(self._offersProvider.getCdnResourcePath(gift.cdnIconPath)))
            if gift.isVehicle:
                event_dispatcher.showOfferGiftVehiclePreview(offerID=self._offerID, giftID=giftID, confirmCallback=onGiftConfirm)
                self.destroyWindow()
            else:
                onGiftConfirm()
            return

    @adisp_process
    def _onGiftConfirm(self, offerID, giftID, cdnTitle='', cdnDescription='', cdnIcon=''):
        result = yield ReceiveOfferGiftProcessor(offerID, giftID, cdnTitle).request()
        if result.success:
            if self.__overrideSuccessCallback is not None:
                self.__overrideSuccessCallback(offerID, giftID, cdnTitle=cdnTitle, cdnDescription=cdnDescription, cdnIcon=cdnIcon)
            else:
                event_dispatcher.showOfferRewardWindow(offerID, giftID, cdnTitle, cdnDescription, cdnIcon)
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        return

    def _onItemsCacheResync(self, *args, **kwargs):
        if self._offerItem is None:
            return
        else:
            with self._viewModel.transaction() as model:
                for giftModel in model.gifts.getItems():
                    gift = self._offerItem.getGift(giftModel.getId())
                    notEnoughTokens = self._offerItem.availableTokens < gift.price
                    giftModel.setIsNotEnoughMoney(notEnoughTokens)
                    giftCount = self._offerItem.getGiftAvailableCount(gift.id)
                    giftDisabled = notEnoughTokens or gift.isDisabled or not giftCount
                    giftModel.setIsDisabled(giftDisabled)

            return

    def _onOffersUpdated(self):
        if self._offerItem is None or not self._offerItem.isOfferAvailable:
            if self._offersProvider.getUnlockedOffers(includeAllOffers=False):
                event_dispatcher.showStorage(defaultSection=STORAGE_CONSTANTS.OFFERS)
            else:
                event_dispatcher.showHangar()
            self.destroyWindow()
            return
        else:
            with self._viewModel.transaction() as model:
                self._setDynamicInfo(model)
                self._generateGifts(model)
            return

    def _onBecomeNonPlayer(self, *args, **kwargs):
        self.destroyWindow()

    def _onServerSettingsRecync(self, *args, **kwargs):
        if not self._serverSettings.isOffersEnabled():
            event_dispatcher.showHangar()
            self.destroyWindow()

    def _onBack(self):
        event_dispatcher.showStorage(defaultSection=STORAGE_CONSTANTS.OFFERS)
        self.destroyWindow()

    def _onLearnMore(self):
        localization = ResMgr.openSection(self._offersProvider.getCdnResourcePath(self._offerItem.cdnLocFilePath, relative=False))
        if localization:
            url = localization.readString('linkUrl', '')
            if url:
                self._externalBrowser.open(url)
