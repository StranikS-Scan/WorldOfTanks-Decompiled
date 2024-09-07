# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/shared/gui_items/processors/offer.py
import logging
import typing
from helpers import dependency
from AccountCommands import RES_SUCCESS, RES_FAILURE
from gui import SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.shared.gui_items.processors.offers import ReceiveMultipleOfferGiftsProcessor
from gui.shared.gui_items.processors import makeSuccess
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.system_messages import ISystemMessages
if typing.TYPE_CHECKING:
    from account_helpers.offers.events_data import OfferGift, OfferEventData
_logger = logging.getLogger(__name__)

class WinbackMultipleOfferProcessor(ReceiveMultipleOfferGiftsProcessor):
    __offersProvider = dependency.descriptor(IOffersDataProvider)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def _successHandler(self, code, ctx=None):
        Waiting.hide('loadContent')
        successData = ctx.get(RES_SUCCESS)
        if successData:
            self.__updateBlueprints(successData)
            self.__systemMessages.proto.serviceChannel.pushClientMessage(successData, SCH_CLIENT_MSG_TYPE.WINBACK_SELECTABLE_REWARD)
        failureData = ctx.get(RES_FAILURE)
        if failureData:
            msg = self._errorHandler(code, self.ERROR_CODE_MULTI_ERROR, ctx=failureData)
            SystemMessages.pushMessage(msg.userMsg, msg.sysMsgType)
        return makeSuccess(auxData=ctx)

    def __updateBlueprints(self, successData):
        blueprints = successData.get('blueprints')
        if not blueprints:
            return
        else:
            for offerID, giftIDs in self._chosenGifts.iteritems():
                offer = self.__offersProvider.getOffer(offerID)
                for giftID in giftIDs:
                    gift = offer.getGift(giftID)
                    if gift is None:
                        _logger.error('Wrong giftID=%s for offerID=%s', giftID, offerID)
                        continue
                    chosenBlueprintsBonuses = gift.rawBonuses.get('blueprints', {})
                    for blueprintId, count in chosenBlueprintsBonuses.iteritems():
                        blueprints.setdefault(blueprintId, count)

            return
