# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/offers_requester.py
import BigWorld
from adisp import async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from skeletons.gui.shared.utils.requesters import IOffersRequester

class OffersRequester(AbstractSyncDataRequester, IOffersRequester):

    def getReceivedGifts(self, offerID):
        return self.__getOffer(offerID).get('gifts', dict())

    def isBannerSeen(self, offerID):
        return self.__getOffer(offerID).get('bannerSeen', False)

    @async
    def _requestCache(self, callback):
        BigWorld.player().offers.getCache(lambda resID, value: self._response(resID, value, callback))

    def __getOffer(self, offerID):
        return self.getCacheValue('offersData', {}).get(offerID, {})
