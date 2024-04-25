# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBFrontCouponsComponent.py
import typing
from typing import List, Optional, Dict
import BigWorld
import HBAccountSettings
from Event import Event
from PlayerEvents import g_playerEvents
from helpers import dependency
from historical_battles_common.hb_constants import HB_FRONT_COUPONS_GAME_PARAMS_KEY, AccountSettingsKeys
from skeletons.gui.lobby_context import ILobbyContext
from historical_battles.gui.server_events.game_event.front_coupons_progress import FrontCouponsProgressItemsController
if typing.TYPE_CHECKING:
    from historical_battles.gui.server_events.game_event.front_coupon_item import BaseFrontCoupon

class HBFrontCouponsComponent(BigWorld.StaticScriptComponent):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.onFrontCouponsUpdated = Event()
        self._progressController = FrontCouponsProgressItemsController()
        g_playerEvents.onAccountBecomePlayer += self._onAccountBecomePlayer
        g_playerEvents.onAccountBecomeNonPlayer += self._onAccountBecomeNonPlayer

    def getActiveFrontCoupon(self):
        return self._progressController.getActiveFrontCoupon()

    def getRechargeableFrontCoupon(self):
        return self._progressController.getRechargeableFrontCoupon()

    def getFrontCoupons(self):
        return self._progressController.getItems()

    def getGroupedFrontCoupons(self):
        return self._progressController.getGroupedFrontCoupons()

    @staticmethod
    def getViewedFrontCoupons():
        return HBAccountSettings.getSettings(AccountSettingsKeys.FRONT_COUPONS_VIEWED)

    def markFrontCouponsAsViewed(self):
        viewedFrontCoupons = {f.getFrontCouponID():f.getCurrentCount() for f in self.getFrontCoupons().itervalues()}
        HBAccountSettings.setSettings(AccountSettingsKeys.FRONT_COUPONS_VIEWED, viewedFrontCoupons)

    def getFrontCouponConfig(self, frontCouponID):
        return self.getFrontCouponsConfig().get(frontCouponID)

    def getFrontCouponsConfig(self):
        return self._getConfig().get('frontCoupons', {})

    def getUsageOrder(self):
        return self._getConfig().get('usageOrder', [])

    def _getConfig(self):
        settings = self.lobbyContext.getServerSettings().getSettings()
        return settings.get(HB_FRONT_COUPONS_GAME_PARAMS_KEY, {})

    def _onFrontCouponUpdated(self, *_):
        self.onFrontCouponsUpdated()

    def _onAccountBecomePlayer(self):
        self._progressController.start()
        self._progressController.onItemsUpdated += self._onFrontCouponUpdated

    def _onAccountBecomeNonPlayer(self):
        self.onFrontCouponsUpdated.clear()
        self._progressController.stop()
        self._progressController.onItemsUpdated -= self._onFrontCouponUpdated
        g_playerEvents.onAccountBecomePlayer -= self._onAccountBecomePlayer
        g_playerEvents.onAccountBecomeNonPlayer -= self._onAccountBecomeNonPlayer
