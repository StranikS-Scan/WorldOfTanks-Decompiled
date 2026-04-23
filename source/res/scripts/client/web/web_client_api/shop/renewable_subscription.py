# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/renewable_subscription.py
from gui.server_events.bonuses_wot_plus import getAvailableCoreBonuses, getAvailableProBonuses
from helpers import dependency
from skeletons.gui.game_control import IWotPlusController
from uilogging.wot_plus.loggers import WotPlusInfoPageLogger
from uilogging.wot_plus.logging_constants import WotPlusInfoPageSource
from renewable_subscription_common.settings_constants import WotPlusTier
from web.web_client_api import W2CSchema, w2c
_TIER_TO_STRING = {WotPlusTier.NONE: 'none',
 WotPlusTier.CORE: 'core',
 WotPlusTier.PRO: 'pro'}

class RenewableSubWebApiMixin(object):
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)

    @w2c(W2CSchema, 'get_subscription_info')
    def getSubscriptionInfo(self, cmd):
        storage = self._wotPlusCtrl.getSettingsStorage()
        return {'period_start': self._wotPlusCtrl.getStartTime(),
         'period_end': self._wotPlusCtrl.getExpiryTime(),
         'enabled_core_bonuses': [ bonus.getName() for bonus in getAvailableCoreBonuses(storage) ],
         'enabled_pro_bonuses': [ bonus.getName() for bonus in getAvailableProBonuses(storage) ],
         'is_free_deluxe_demount_included': self._wotPlusCtrl.getSettingsStorage().isFreeDeluxeEquipmentDemountingAvailable(),
         'current_active_tier': _TIER_TO_STRING[self._wotPlusCtrl.getTier()],
         'enabled_for_steam': self._wotPlusCtrl.getSettingsStorage().isEnabledForSteam()}

    @w2c(W2CSchema, 'subscription_info_window')
    def handleSubscriptionInfoWindow(self, cmd):
        WotPlusInfoPageLogger().logInfoPage(WotPlusInfoPageSource.SHOP)
