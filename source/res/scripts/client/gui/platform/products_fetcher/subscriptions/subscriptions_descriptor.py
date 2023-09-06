# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/products_fetcher/subscriptions/subscriptions_descriptor.py
import typing
from constants import SUBSCRIPTION_ENTITLEMENT
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.player_subscriptions.subscription_model import SubscriptionTypeEnum
from gui.impl.gen.view_models.views.lobby.player_subscriptions.wot_subscription_model import WotSubscriptionStateEnum
from gui.platform.products_fetcher.product_descriptor import ProductDescriptor
from helpers import dependency
from renewable_subscription_common.settings_constants import WotPlusState
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest

class SubscriptionDescriptor(ProductDescriptor):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, params):
        super(SubscriptionDescriptor, self).__init__(params)
        self._offerToken = None
        return

    @property
    def type(self):
        return SubscriptionTypeEnum.EXTERNALSUBSCRIPTION

    @property
    def isSubscribed(self):
        return False

    @property
    def expirationTime(self):
        pass

    def hasDepotRewards(self):
        return False

    def isRewardsClaimed(self):
        return False

    def getOfferToken(self):
        return self._offerToken

    def getOfferID(self):
        return None

    def _getEvents(self):
        return ((self._lobbyContext.getServerSettings().onServerSettingsChange, self._onServerSettingsChange), (self._connectionMgr.onDisconnected, self._onServerSettingsChange))

    def _onServerSettingsChange(self, *args, **kwargs):
        self._offerToken = None
        return


class PrimeGamingDescriptor(SubscriptionDescriptor):
    __PRIME_GAMING_FILTER_STR = 'PrimeGaming'
    __eventsCache = dependency.descriptor(IEventsCache)
    __offersProvider = dependency.descriptor(IOffersDataProvider)

    def __init__(self, params):
        super(PrimeGamingDescriptor, self).__init__(params)
        self.__primeGamingQuest = None
        return

    @property
    def isSubscribed(self):
        return True

    @property
    def expirationTime(self):
        quest = self.getPrimeGamingQuest()
        return quest.getFinishTimeRaw() if quest else 0

    def hasDepotRewards(self):
        offerID = self.getOfferToken()
        return offerID and self.__offersProvider.isOfferAvailable(offerID)

    def isRewardsClaimed(self):
        quest = self.getPrimeGamingQuest()
        return quest.isCompleted() if quest else False

    def getPrimeGamingQuest(self):
        if self.__primeGamingQuest:
            return self.__primeGamingQuest
        quests = self.__eventsCache.getAllQuests(self.__twitchFilterFunc)
        for quest in quests.values():
            conditionTokens = quest.accountReqs.getTokens()
            isPrimeGamingQuest = all((self.__PRIME_GAMING_FILTER_STR in token.getID() for token in conditionTokens))
            if isPrimeGamingQuest:
                self.__primeGamingQuest = quest

        return self.__primeGamingQuest

    def getOfferToken(self):
        if self._offerToken:
            return self._offerToken
        quests = self.__eventsCache.getAllQuests(self.__twitchFilterFunc)
        for quest in quests.values():
            bonuses = quest.getBonuses('tokens')
            for bonus in bonuses:
                for tID in bonus.getTokens():
                    if tID.startswith('offer:'):
                        self._offerToken = tID
                        break

        return self._offerToken

    def getOfferID(self):
        offerToken = self.getOfferToken()
        return self.__offersProvider.getOfferByToken(offerToken).id if offerToken and self.__offersProvider.isOfferAvailable(offerToken) else None

    def _onServerSettingsChange(self, *args, **kwargs):
        super(PrimeGamingDescriptor, self)._onServerSettingsChange(args, kwargs)
        self.__primeGamingQuest = None
        return

    def __twitchFilterFunc(self, q):
        return q.getID().startswith('twitch')


class WotPlusDescriptor(SubscriptionDescriptor):
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    _COMMON_TO_UI_STATE_DICT = {WotPlusState.INACTIVE: WotSubscriptionStateEnum.INACTIVE,
     WotPlusState.ACTIVE: WotSubscriptionStateEnum.ACTIVE,
     WotPlusState.CANCELLED: WotSubscriptionStateEnum.CANCELLED}

    @property
    def type(self):
        return SubscriptionTypeEnum.WOTSUBSCRIPTION

    @property
    def productID(self):
        return SUBSCRIPTION_ENTITLEMENT

    @property
    def name(self):
        return backport.text(R.strings.subscription.dashboard.subscriptionCard.label())

    @property
    def description(self):
        vehicleName = self._wotPlusCtrl.getActiveExclusiveVehicleName()
        return backport.text(R.strings.subscription.dashboard.subscriptionCard.description(), vehicleName=vehicleName)

    @property
    def largeImageURL(self):
        return backport.image(R.images.gui.maps.icons.subscription.dashboard_card.largeCard())

    @property
    def mediumImageURL(self):
        return backport.image(R.images.gui.maps.icons.subscription.dashboard_card.mediumCard())

    @property
    def expirationTime(self):
        return self._wotPlusCtrl.getExpiryTime()

    @property
    def state(self):
        return self._COMMON_TO_UI_STATE_DICT[self._wotPlusCtrl.getState()]
