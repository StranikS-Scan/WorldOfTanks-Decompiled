# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/offers/offers_view.py
import ResMgr
from account_helpers.offers.cache import CachePrefetchResult
from adisp import process, async
from battle_pass_common import BATTLE_PASS_TOKEN_TROPHY_OFFER_2020, BATTLE_PASS_TOKEN_NEW_DEVICE_OFFER_2020
from gui.battle_pass.battle_pass_helpers import showOfferTrophyDevices, showOfferNewDevices
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import createStorageDefVO
from gui.Scaleform.daapi.view.meta.StorageCategoryOffersViewMeta import StorageCategoryOffersViewMeta
from gui.Scaleform.Waiting import Waiting
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import showOfferGiftsWindow, showShop
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersNovelty, IOffersDataProvider

class StorageCategoryOffersView(StorageCategoryOffersViewMeta):
    _offersProvider = dependency.descriptor(IOffersDataProvider)
    _offersNovelty = dependency.descriptor(IOffersNovelty)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def _populate(self):
        super(StorageCategoryOffersView, self)._populate()
        self._offersProvider.onOffersUpdated += self._onOffersUpdated
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def _dispose(self):
        super(StorageCategoryOffersView, self)._dispose()
        self._offersProvider.onOffersUpdated -= self._onOffersUpdated
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def _update(self):
        self._updateData()

    def _onOffersUpdated(self):
        if self.getActive():
            self._updateData()

    @async
    @process
    def _syncOffers(self, callback=None):
        result = CachePrefetchResult.SUCCESS
        currentIDs = {offerVO['id'] for offerVO in self._dataProvider.collection}
        newIDs = {offer.id for offer in self._offersProvider.getAvailableOffers(onlyVisible=True)}
        if currentIDs != newIDs:
            Waiting.show('loadContent')
            result = yield self._offersProvider.isCdnResourcesReady()
            Waiting.hide('loadContent')
        callback(result)

    @process
    def _updateData(self):
        result = yield self._syncOffers()
        if not self._offersProvider.getAvailableOffers(onlyVisible=True):
            return
        if result != CachePrefetchResult.SUCCESS:
            self.as_showDummyScreenS(True)
        else:
            self.as_showDummyScreenS(False)
            self._offersNovelty.setAsSeen()
            currentOffersVo = self._getVoList()
            self._currentOffersCount = len(currentOffersVo)
            self._dataProvider.buildList(currentOffersVo)

    def _getTotalClicksText(self):
        clicksCount = sum([ o.clicksCount for o in self._offersProvider.iAvailableOffers(onlyVisible=True) ])
        clicksText = backport.text(R.strings.storage.offers.giftsTitle(), gifts=text_styles.stats(clicksCount))
        return clicksText

    def _getVoList(self):
        sortedOffers = sorted(self._offersProvider.iAvailableOffers(onlyVisible=True), key=lambda o: o.priority)
        return [ self._getVO(offer) for offer in sortedOffers ]

    def _getVO(self, offer):
        gifts = backport.text(R.strings.storage.offers.giftAmount(), gifts=text_styles.neutral(offer.availableGiftsCount))
        date = backport.getShortDateFormat(offer.expiration)
        time = backport.getShortTimeFormat(offer.expiration)
        expiration = backport.text(R.strings.storage.offers.expiration(), date=text_styles.neutral(date), time=text_styles.neutral(time))
        description = '\n'.join([gifts, expiration])
        localization = ResMgr.openSection(self._offersProvider.getCdnResourcePath(offer.cdnLocFilePath, relative=False))
        title = localization.readString('name') if localization else ''
        vo = createStorageDefVO(offer.id, title, description, 0, None, self._offersProvider.getCdnResourcePath(offer.cdnLogoPath, relative=False), 'altimage', contextMenuId=None)
        return vo

    def scrolledToBottom(self):
        pass

    def openOfferWindow(self, offerID):
        offer = self._offersProvider.getOffer(offerID)
        if offer is not None and offer.token == BATTLE_PASS_TOKEN_TROPHY_OFFER_2020:
            showOfferTrophyDevices()
            return
        elif offer is not None and offer.token == BATTLE_PASS_TOKEN_NEW_DEVICE_OFFER_2020:
            showOfferNewDevices()
            return
        else:
            showOfferGiftsWindow(offerID)
            return

    def navigateToStore(self):
        showShop()

    def __onServerSettingsChange(self, *args, **kwargs):
        if not self._lobbyContext.getServerSettings().isOffersEnabled():
            event_dispatcher.showHangar()
