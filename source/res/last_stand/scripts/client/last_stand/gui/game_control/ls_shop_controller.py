# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/game_control/ls_shop_controller.py
import Event
from collections import namedtuple
from adisp import adisp_async
from gui import SystemMessages
from gui.shared.utils import decorators
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.server_events.bonuses import getNonQuestBonuses, TokensBonus
from last_stand.gui.shared.gui_items.processors.processors import BuyBundleProcessor
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_shop_controller import ILSShopController
from last_stand_common.last_stand_constants import ShopSettings, ArtefactsSettings
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
Price = namedtuple('Price', ('currency', 'amount'))

class Bundle(namedtuple('Bundle', ('bundleID', 'groupID', 'orderInGroup', 'descrGroupKey', 'limit', 'isWebShopBundle', 'price', 'oldPrice', 'url', 'bonuses'))):

    def getCtx(self):
        return dict(self._asdict())


class LSShopController(ILSShopController):
    eventsCache = dependency.descriptor(IEventsCache)
    lsCtrl = dependency.descriptor(ILSController)

    def __init__(self):
        super(LSShopController, self).__init__()
        self.onShopSettingsUpdated = Event.Event()
        self.onBundlesUpdated = Event.Event()
        self._bundles = {}

    def init(self):
        g_clientUpdateManager.addCallbacks({'tokens': self.__handleTokensUpdate})
        self.lsCtrl.onSettingsUpdate += self.__updateSettings

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.lsCtrl.onSettingsUpdate -= self.__updateSettings
        self.onShopSettingsUpdated.clear()
        self.onBundlesUpdated.clear()
        self._bundles = {}

    def keyBundles(self):
        return sorted(self._bundles.itervalues(), key=lambda bundle: bundle.bundleID)

    def getBundleByID(self, bundleID):
        return self._bundles.get(bundleID)

    def getKeysInBundle(self, bundleID):
        bundle = self._bundles.get(bundleID)
        if not bundle:
            return 0
        for bonus in bundle.bonuses:
            if not isinstance(bonus, TokensBonus):
                continue
            tokens = bonus.getTokens()
            for token in tokens.itervalues():
                if token.id != ArtefactsSettings.KEY_TOKEN:
                    continue
                return token.count

    def isEnabled(self):
        return self._getConfig().get('enabled', False)

    def onLobbyStarted(self, ctx):
        super(LSShopController, self).onLobbyStarted(ctx)
        self._initBundles()

    @adisp_async
    @decorators.adisp_process('buyItem')
    def purchaseBundle(self, bundleID, count, callback):
        bundle = self.getBundleByID(bundleID)
        result = yield BuyBundleProcessor(bundleID, bundle.price, count).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        callback(result.success)

    def getPurchaseCount(self, bundleID):
        return self.eventsCache.questsProgress.getTokenCount(bundleID + ShopSettings.PURCHASED_SUFFIX)

    def checkIsEnoughBundles(self):
        for bundle in self.keyBundles():
            if bundle.limit is not None:
                limit = bundle.limit - self.getPurchaseCount(bundle.bundleID)
                if limit > 0:
                    return True

        return False

    def _initBundles(self):
        self._bundles = dict(((bundleID, Bundle(bundleID, int(self._getBundleGroupID(bundleID)), int(self._getBundleOrderInGroup(bundleID)), self._getBundleDescrGroupKey(bundleID), self._getBundleLimit(bundleID), self._isWebShopBundle(bundleID), Price(*self._getPrice(bundleID, 'price')), Price(*self._getPrice(bundleID, 'oldPrice')), self._getBundleUrl(bundleID), self._getBonuses(bundleID))) for bundleID in self._getBundles().iterkeys()))

    def _getBundleGroupID(self, bundleID):
        return self._getBundles().get(bundleID, {}).get('groupId')

    def _getBundleOrderInGroup(self, bundleID):
        return self._getBundles().get(bundleID, {}).get('orderInGroup')

    def _getBundleDescrGroupKey(self, bundleID):
        return self._getBundles().get(bundleID, {}).get('descrGroupKey')

    def _getBundleLimit(self, bundleID):
        return self._getBundles().get(bundleID, {}).get('limit')

    def _getBundleUrl(self, bundleID):
        return self._getBundles().get(bundleID, {}).get('url')

    def _isWebShopBundle(self, bundleID):
        return self._getBundles().get(bundleID, {}).get('isWebShopBundle', True)

    def _getPrice(self, bundleID, priceKey):
        return self._getBundles().get(bundleID, {}).get(priceKey, (None, 0))

    def _getBundles(self):
        return self._getConfig().get('bundles', {})

    def _getBonuses(self, bundleID):
        rewards = []
        bonuses = self._getBundles().get(bundleID, {}).get('bonus', {})
        for bonusType, bonusValue in bonuses.iteritems():
            rewards.extend(getNonQuestBonuses(bonusType, bonusValue))

        return rewards

    def _getConfig(self):
        return self.lsCtrl.getModeSettings().shop

    def __updateSettings(self):
        self._initBundles()
        self.onShopSettingsUpdated()

    def __handleTokensUpdate(self, diff):
        for token in diff:
            if token.startswith(ShopSettings.SHOP_BUNDLE_PREFFIX):
                self.onBundlesUpdated()
