# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/offers.py
import typing
from skeletons.gui import INovelty
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Iterable, Optional, Union
    from account_helpers.offers.events_data import OfferEventData
    from Event import Event

class IOffersNovelty(INovelty):

    def saveAsSeen(self, offerId):
        raise NotImplementedError


class IOffersBannerController(object):
    onShowBanners = None
    onHideBanners = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def showBanners(self):
        raise NotImplementedError

    def hideBanners(self):
        raise NotImplementedError


class IOffersDataProvider(object):
    onOffersUpdated = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def update(self, diff):
        raise NotImplementedError

    @property
    def isSynced(self):
        raise NotImplementedError

    def getReceivedGifts(self, offerID):
        raise NotImplementedError

    def isBannerSeen(self, offerID):
        raise NotImplementedError

    def isCdnResourcesReady(self, callback=None, timeout=0):
        raise NotImplementedError

    def getCdnResourcePath(self, cdnRelativePath, relative=True):
        raise NotImplementedError

    def getOffer(self, offerID):
        raise NotImplementedError

    def getOfferByToken(self, token):
        raise NotImplementedError

    def iAvailableOffers(self, onlyVisible=True):
        raise NotImplementedError

    def getAvailableOffers(self, onlyVisible=True):
        raise NotImplementedError

    def getAvailableOffersByToken(self, token):
        raise NotImplementedError

    def isOfferAvailable(self, tokenID):
        raise NotImplementedError

    def iUnlockedOffers(self, onlyVisible=True):
        raise NotImplementedError

    def getUnlockedOffers(self, onlyVisible=True):
        raise NotImplementedError

    def isOfferUnlocked(self, tokenID):
        raise NotImplementedError

    def getAmountOfGiftsGenerated(self, tokenID, mainTokenCount):
        raise NotImplementedError
