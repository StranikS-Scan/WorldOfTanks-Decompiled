# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/shop.py
import logging
import itertools
from collections import namedtuple
import BigWorld
from adisp import async
from Event import EventManager, Event
from gui import SystemMessages
from gui.server_events.bonuses import mergeBonuses, getNonQuestBonuses
from helpers import dependency, time_utils
from skeletons.gui.server_events import IEventsCache
from gui.shared.gui_items.processors import Processor, plugins, makeI18nError
from gui.shared.utils import decorators
from constants import EVENT, EVENT_CLIENT_DATA
from gui.shared.money import Money, Currency
from helpers.CallbackDelayer import CallbackDelayer
from gui.ClientUpdateManager import g_clientUpdateManager
_BONUS_BATTLETOKEN = 'battleToken'
_BONUS_CUSTOMIZATIONS = 'customizations'
_logger = logging.getLogger(__name__)

class ShopBundle(object):
    _ShopBundlePrice = namedtuple('_ShopBundlePrice', ('currencyType', 'currency', 'amount'))
    _BUNDLE_UNLOCK_CLIENT_DELAY = 5

    def __init__(self, config):
        super(ShopBundle, self).__init__()
        self._ID = config['id']
        self._price = self._ShopBundlePrice(*config['price'])
        self._oldPrice = self._ShopBundlePrice(*config['oldPrice']) if 'oldPrice' in config else None
        self._unlockDate = config.get('unlockDate', None)
        self._limit = config.get('limit', None)
        self._bonuses = self._buildBonuses(config)
        self._questsToRun = config.get('questsToRun', None)
        return

    @property
    def id(self):
        return self._ID

    @property
    def price(self):
        return self._price

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

    def _buildBonuses(self, config):
        bonuses = []
        for bonusType, bonusValue in config['bonus'].iteritems():
            bonus = getNonQuestBonuses(bonusType, bonusValue)
            bonuses.extend(bonus)

        return mergeBonuses(bonuses)


class Shop(object):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(Shop, self).__init__()
        self._em = EventManager()
        self.onBundleUnlocked = Event(self._em)
        self.onBundlePurchaseFinished = Event(self._em)
        self.onGoldChanged = Event(self._em)
        self.onShopBundlesChanged = Event(self._em)
        self._shopBundles = {}
        self._bundleUnlockCallbacks = CallbackDelayer()

    def start(self):
        self.cacheShopBundles()
        g_clientUpdateManager.addCallbacks({'stats.{}'.format(Currency.GOLD): self.__onGoldChanged,
         'eventsData.{}'.format(EVENT_CLIENT_DATA.INGAME_EVENTS_REV): self.__onIngameEventsUpdate})

    def stop(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._bundleUnlockCallbacks.destroy()
        self._em.clear()

    def cacheShopBundles(self):
        self._shopBundles.clear()
        self._bundleUnlockCallbacks.clearCallbacks()
        bundles = self.shopData.get('shopBundles', None)
        if bundles is None:
            return
        else:
            for bundleID, config in bundles.iteritems():
                self._shopBundles[bundleID] = bundle = ShopBundle(config)
                self.__startBunleUnlockTimer(bundle)

            return

    @async
    @decorators.process('buyItem')
    def purchaseShopBundle(self, bundleID, callback, count=1):
        result = yield ShopBundlePurchaseProcessor(self._shopBundles[bundleID], count).request()
        if not result.success and result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        callback(result.success)

    @property
    def shopData(self):
        return self._getShopData()

    def getShopBundleBonusesWithQuests(self, bundle):
        bonuses = list(bundle.bonuses)
        questIDs = bundle.questsToRun
        if not questIDs:
            return bonuses
        quests = self.eventsCache.getHiddenQuests(lambda q: q.getID() in questIDs)
        if not quests:
            return bonuses
        bonuses.extend(itertools.chain.from_iterable((q.getBonuses() for q in quests.itervalues())))
        return mergeBonuses(bonuses)

    def isEnabled(self):
        return self._getShopData().get('enabled', False)

    def getKeys(self):
        return self.eventsCache.questsProgress.getTokenCount(EVENT.REWARD_BOX.KEY_TOKEN)

    def getBundlePurchasesCount(self, bundleID):
        counterToken = EVENT.SHOP.getBundlePurchaseCounterTokenName(bundleID)
        return self.eventsCache.questsProgress.getTokenCount(counterToken)

    def getBundle(self, bundleID):
        return self._shopBundles[bundleID]

    def getBundlesByShopType(self, shopType):
        shopConfig = self._getShopData().get(shopType, None)
        if shopConfig is None:
            return []
        else:
            return [ self.getBundle(bundleID) for bundleID in shopConfig['bundles'] ]

    def _getShopData(self):
        return self.eventsCache.getGameEventData().get('shop', {})

    def __startBunleUnlockTimer(self, bundle):
        if bundle.secondsToUnlock <= 0:
            return
        self._bundleUnlockCallbacks.delayCallback(bundle.secondsToUnlock, self.__onBundleUnlockTimer, bundle)

    def __onBundleUnlockTimer(self, bundle):
        self.onBundleUnlocked(bundle)

    def __onGoldChanged(self, v):
        self.onGoldChanged(v)

    def __onIngameEventsUpdate(self, *args):
        self.cacheShopBundles()
        self.onShopBundlesChanged()


class ShopBundlePurchaseProcessor(Processor):

    def __init__(self, bundle, count=1):
        self._bundle = bundle
        self._count = count
        price = bundle.price
        moneyValidationPlugin = plugins.MoneyValidator(Money(**{price.currency: price.amount})) if price.currencyType == EVENT.SHOP.REAL_CURRENCY else plugins.TokenValidator(price.currency, price.amount)
        super(ShopBundlePurchaseProcessor, self).__init__(plugins=(moneyValidationPlugin,))

    def _request(self, callback):
        BigWorld.player().shop.purchaseEventShopBundle(self._bundle.id, self._count, lambda requestID, code, errorCode: self._response(code, callback, errorCode))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('hw21/{}'.format(errStr), defaultSysMsgKey='hw21/server_error')
