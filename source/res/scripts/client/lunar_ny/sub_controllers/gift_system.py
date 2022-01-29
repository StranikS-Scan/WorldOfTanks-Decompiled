# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/sub_controllers/gift_system.py
import typing
import Event
from adisp import process
from gifts.gifts_common import GiftEventID
from gui.gift_system.constants import HubUpdateReason
from helpers import dependency
from lunar_ny.lunar_ny_constants import ENVELOPE_TYPE_TO_ENTITLEMENT_CODE, ENVELOPE_ENTITLEMENT_COUNTER, ENVELOPE_IN_SECRET_SANTA_ENTITLEMENTS
from lunar_ny.sub_controllers import IBaseLunarSubController
from skeletons.gui.game_control import IGiftSystemController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from lunar_ny.lunar_ny_constants import EnvelopeTypes

class LunarNYGiftSystemSubController(IBaseLunarSubController):
    __giftController = dependency.descriptor(IGiftSystemController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__giftEventHub', 'onEnvelopesEntitlementUpdated', 'onWebStateUpdated')

    def __init__(self, eManager):
        self.onEnvelopesEntitlementUpdated = Event.Event(eManager)
        self.onGiftSystemSettingsUpdated = Event.Event(eManager)
        self.onWebStateUpdated = Event.Event(eManager)
        self.__giftEventHub = None
        return

    def start(self):
        self.__giftController.onEventHubsCreated += self.__onEventHubsCreated
        self.__giftController.onEventHubsDestroyed += self.__onEventHubsDestroyed
        self.__addEventHub()
        self.onGiftSystemSettingsUpdated()

    def stop(self):
        self.__removeEventHub()
        self.__giftController.onEventHubsCreated -= self.__onEventHubsCreated
        self.__giftController.onEventHubsDestroyed -= self.__onEventHubsDestroyed

    def isGiftEventActive(self):
        return self.__giftEventHub and self.__giftEventHub.getSettings().isEnabled

    def isDisabledGiftForSendById(self, giftID):
        result = False
        if self.__giftEventHub is not None:
            result = giftID in self.__giftEventHub.getSettings().disabledGifts
        return result

    def isAllGiftDisabledForSend(self):
        if self.__giftEventHub is not None:
            settings = self.__giftEventHub.getSettings()
            return set(settings.disabledGifts) == set(settings.giftItemIDs)
        else:
            return False

    @process
    def sendGift(self, envelopeType, receiverID, messageIdx, callback=None):
        if self.__giftEventHub is not None:
            metaInfo = {'message_id': messageIdx}
            entitlementCode = ENVELOPE_TYPE_TO_ENTITLEMENT_CODE[envelopeType]
            result = yield self.__giftEventHub.getGifter().sendGift(entitlementCode, receiverID, metaInfo)
            callback(result)
        elif callback is not None:
            callback(None)
        return

    def getEnvelopesEntitlementCount(self):
        return sum((self.getEnvelopesEntitlementCountByType(count) for count in ENVELOPE_TYPE_TO_ENTITLEMENT_CODE.keys()))

    def getAmountOfPurchasedEnvelopes(self):
        return self.__itemsCache.items.stats.entitlements.get(ENVELOPE_ENTITLEMENT_COUNTER, 0)

    def getEnvelopesEntitlementCountByType(self, envelopeType):
        return 0 if self.__giftEventHub is None else self.__giftEventHub.getStamper().getStampCount(ENVELOPE_TYPE_TO_ENTITLEMENT_CODE[envelopeType])

    def getSecretSantaSentPeriodLimit(self):
        return self.__giftEventHub.getKeeper().getSentPeriodLimit() if self.__giftEventHub is not None else 0

    def envelopeInSecretSantaPoll(self, envelopeType):
        return False if self.__giftEventHub is None else self.__giftEventHub.getStamper().getStampCount(ENVELOPE_IN_SECRET_SANTA_ENTITLEMENTS[envelopeType]) > 0

    def __onEventHubsCreated(self, hubsToCreate):
        if GiftEventID.LUNAR_NY in hubsToCreate:
            self.__removeEventHub()
            self.__addEventHub()

    def __onEventHubsDestroyed(self, hubsToDestroyed):
        if GiftEventID.LUNAR_NY in hubsToDestroyed:
            self.__removeEventHub()

    def __onHubUpdated(self, reason, *_):
        if reason == HubUpdateReason.STAMPER_UPDATE:
            self.onEnvelopesEntitlementUpdated()
        elif reason == HubUpdateReason.SETTINGS:
            self.onGiftSystemSettingsUpdated()
        elif reason == HubUpdateReason.WEB_STATE:
            self.onWebStateUpdated()

    def __addEventHub(self):
        self.__giftEventHub = self.__giftController.getEventHub(GiftEventID.LUNAR_NY)
        if self.__giftEventHub is not None:
            self.__giftEventHub.onHubUpdated += self.__onHubUpdated
        return

    def __removeEventHub(self):
        if self.__giftEventHub is not None:
            self.__giftEventHub.onHubUpdated -= self.__onHubUpdated
            self.__giftEventHub = None
        return
