# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/EventShopAccountComponentBase.py
import logging
import itertools
from collections import namedtuple
import typing
import BigWorld
from PlayerEvents import g_playerEvents
from helpers import time_utils
from helpers.CallbackDelayer import CallbackDelayer
from gui.server_events.bonuses import mergeBonuses, getNonQuestBonuses
from Event import Event
from skeletons.gui.server_events import IEventsCache
from helpers import dependency
from gui.shared.gui_items.processors import Processor, plugins
from gui.shared.money import Money
from historical_battles_common.hb_constants import EventShop
from historical_battles_common.helpers_common import EventShopBundlePrice, Discount
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class ShopBundle(object):
    _BUNDLE_UNLOCK_CLIENT_DELAY = 5

    def __init__(self, config):
        super(ShopBundle, self).__init__()
        self._ID = config['id']
        self._price = EventShopBundlePrice.makePrice(config['price'])
        self._oldPrice = EventShopBundlePrice.makePrice(config['oldPrice']) if 'oldPrice' in config else None
        self._unlockDate = config.get('unlockDate', None)
        self._limit = config.get('limit', None)
        self._bonuses = self._buildBonuses(config)
        self._discountConfig = config.get('discountConfig', None)
        self._questsToRun = config.get('questsToRun', None)
        return

    @property
    def id(self):
        return self._ID

    @property
    def price(self):
        return self._price

    @property
    def prices(self):
        return self._price.subPrices if self._price.type == EventShop.PriceType.MULTI else (self._price,)

    @property
    def oldPrice(self):
        return self._oldPrice

    @property
    def secondsToUnlock(self):
        if self._unlockDate is None:
            return
        else:
            unlockTimeUTC = self._unlockDate + self._BUNDLE_UNLOCK_CLIENT_DELAY
            serverNowUTC = time_utils.getServerUTCTime()
            return max(0, unlockTimeUTC - serverNowUTC)

    @property
    def purchasesLimit(self):
        return self._limit

    @property
    def bonuses(self):
        return self._bonuses

    @property
    def questsToRun(self):
        return self._questsToRun

    @property
    def discountData(self):
        return Discount.parseDiscountConfig(self._discountConfig)

    def _buildBonuses(self, config):
        bonuses = []
        for bonusType, bonusValue in config['bonus'].iteritems():
            bonus = getNonQuestBonuses(bonusType, bonusValue)
            bonuses.extend(bonus)

        return mergeBonuses(bonuses)


class EventShopBundlePurchaseProcessor(Processor):
    RequestResult = namedtuple('RequestResult', ('success', 'errStr'))

    def __init__(self, bundle, count, shopComponent):
        self._bundle = bundle
        self._count = count
        self._shopComponent = shopComponent
        self._price = bundle.price
        discountedPrice = self._shopComponent.getBundleDiscountedPrice(self._bundle)
        if discountedPrice:
            self._price = discountedPrice
        super(EventShopBundlePurchaseProcessor, self).__init__(plugins=self._getPlugins())

    def _getPlugins(self):

        def makePlugin(price):
            return plugins.MoneyValidator(Money(**{price.currency: price.amount})) if price.currencyType == EventShop.CurrencyType.REAL else plugins.TokenValidator(price.currency, price.amount)

        moneyValidationPlugins = []
        if self._price.type == EventShop.PriceType.SINGLE:
            moneyValidationPlugins.append(makePlugin(self._price))
        elif self._price.type == EventShop.PriceType.MULTI:
            moneyValidationPlugins += [ makePlugin(price) for price in self._price.subPrices ]
        return moneyValidationPlugins

    def _request(self, callback):
        self._shopComponent.purchaseBundle(self._bundle.id, self._count, lambda requestID, code, errorCode, *args, **kwargs: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return self.RequestResult(False, errStr)

    def _successHandler(self, code, ctx=None):
        return self.RequestResult(True, '')


class EventShopAccountComponentBase(BigWorld.StaticScriptComponent):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(EventShopAccountComponentBase, self).__init__()
        self.onBundleUnlocked = Event()
        self.onShopUpdated = Event()
        self.onBundlePurchased = Event()
        self._shopBundles = {}
        self._bundleUnlockCallbacks = CallbackDelayer()
        self._configRevision = 0
        self._cacheShopBundles()
        g_playerEvents.onClientUpdated += self._onClientUpdated
        g_playerEvents.onAccountBecomeNonPlayer += self._onAccountBecomeNonPlayer
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onSettingsChanged

    @property
    def configRevision(self):
        return self._configRevision

    def purchaseBundle(self, bundleID, count=1, callback=None):
        self.entity._doCmdIntArrStrArr(self._purchaseCmdID, [count], [bundleID], callback)

    def getBundlePurchasesCount(self, bundle):
        return self._getCounterTokenCount(bundle.id)

    def getBundlePurchasesLeft(self, bundle):
        return min((max(0, limit - self._getCounterTokenCount(limitID)) for limitID, limit in bundle.purchasesLimit)) if bundle.purchasesLimit is not None else None

    def getGroupPurchasesLeft(self, groupID, default=None):
        group = self._shopData.get('groups', {}).get(groupID)
        return default if group is None or 'limit' not in group else max(0, group['limit'] - self._getCounterTokenCount(groupID))

    def getBundleBonusesWithQuests(self, bundle):
        bonuses = list(bundle.bonuses)
        questIDs = bundle.questsToRun
        if not questIDs:
            return bonuses
        quests = self.eventsCache.getHiddenQuests(lambda q: q.getID() in questIDs)
        if not quests:
            return bonuses
        bonuses.extend(itertools.chain.from_iterable((q.getBonuses() for q in quests.itervalues())))
        return mergeBonuses(bonuses)

    def getBundleDiscountedPrice(self, bundle):
        if bundle.discountData is None:
            return
        else:
            discount = Discount(bundle.discountData, self.eventsCache.questsProgress.getTokenCount)
            return bundle.price.getDiscountedPrice(discount)

    def getBundle(self, bundleID):
        return self._shopBundles[bundleID]

    def getBundlesByGroup(self, groupID):
        group = self._shopData.get('groups', {}).get(groupID, None)
        if group is None:
            return []
        else:
            return [ self.getBundle(bundleID) for bundleID in group['bundles'] ]

    @property
    def _purchaseCmdID(self):
        raise NotImplementedError

    @property
    def _shopData(self):
        raise NotImplementedError

    def _isShopDataUpdated(self, diff):
        raise NotImplementedError

    def _getCounterTokenCount(self, bundleLimitID):
        counterToken = EventShop.getBundlePurchaseCounterTokenName(bundleLimitID)
        return self.eventsCache.questsProgress.getTokenCount(counterToken)

    def _cacheShopBundles(self):
        self._shopBundles.clear()
        self._bundleUnlockCallbacks.clearCallbacks()
        bundles = self._shopData.get('shopBundles', None)
        self._configRevision += 1
        if bundles is None:
            return
        else:
            for bundleID, config in bundles.iteritems():
                self._shopBundles[bundleID] = bundle = ShopBundle(config)
                self.__startBundleUnlockTimer(bundle)

            return

    def _onAccountBecomeNonPlayer(self):
        g_playerEvents.onClientUpdated -= self._onClientUpdated
        g_playerEvents.onAccountBecomeNonPlayer -= self._onAccountBecomeNonPlayer
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self._onSettingsChanged
        self._shopBundles.clear()
        self._bundleUnlockCallbacks.clearCallbacks()

    def _onSettingsChanged(self, diff):
        self._cacheShopBundles()

    def _onClientUpdated(self, diff, _):
        self._cacheShopBundles()
        self.__updateBundles(diff)
        self.__updateTokens(diff)

    def __updateTokens(self, diff):
        if 'tokens' not in diff:
            return
        for token in diff['tokens'].iterkeys():
            index = token.find(EventShop.PURCHASES_COUNTER_TOKEN_SUFFIX)
            if index == -1:
                continue
            bundleId = token[:index]
            if bundleId in self._shopBundles:
                self.onBundlePurchased(bundleId)

    def __updateBundles(self, diff):
        if not self._isShopDataUpdated(diff):
            return
        self._cacheShopBundles()
        self.onShopUpdated()

    def __startBundleUnlockTimer(self, bundle):
        if bundle.secondsToUnlock <= 0:
            return
        self._bundleUnlockCallbacks.delayCallback(bundle.secondsToUnlock, self.__onBundleUnlockTimer, bundle)

    def __onBundleUnlockTimer(self, bundle):
        self.onBundleUnlocked(bundle)
