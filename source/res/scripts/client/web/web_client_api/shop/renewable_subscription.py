# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/renewable_subscription.py
from typing import TYPE_CHECKING
import logging
from constants import WoTPlusBonusType
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.Vehicle import getUserName
from helpers import dependency
from items.vehicles import getVehicleType
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.wot_plus.loggers import WotPlusInfoPageLogger
from uilogging.wot_plus.logging_constants import WotPlusInfoPageSource
from web.web_client_api import W2CSchema, w2c, Field
_logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from typing import List
    from helpers.server_settings import ServerSettings

class _RenewableSubRentVehicleInfoSchema(W2CSchema):
    vehCD = Field(required=True, type=int)


class RenewableSubWebApiMixin(object):
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    @w2c(W2CSchema, 'get_subscription_info')
    def getSubscriptionInfo(self, cmd):
        serverSettings = self._lobbyContext.getServerSettings()
        return {'period_start': self._wotPlusCtrl.getStartTime(),
         'period_end': self._wotPlusCtrl.getExpiryTime(),
         'enabled_bonuses': self.getEnabledBonuses(serverSettings),
         'is_free_deluxe_demount_included': serverSettings.isFreeDeluxeEquipmentDemountingEnabled()}

    def getEnabledBonuses(self, serverSettings):
        enabledBonuses = []
        if serverSettings.isRenewableSubGoldReserveEnabled():
            enabledBonuses.append(WoTPlusBonusType.GOLD_BANK)
        if serverSettings.isRenewableSubPassiveCrewXPEnabled():
            enabledBonuses.append(WoTPlusBonusType.IDLE_CREW_XP)
        if serverSettings.isWotPlusExcludedMapEnabled():
            enabledBonuses.append(WoTPlusBonusType.EXCLUDED_MAP)
        if serverSettings.isFreeEquipmentDemountingEnabled():
            enabledBonuses.append(WoTPlusBonusType.FREE_EQUIPMENT_DEMOUNTING)
        if serverSettings.isWoTPlusExclusiveVehicleEnabled():
            enabledBonuses.append(WoTPlusBonusType.EXCLUSIVE_VEHICLE)
        return enabledBonuses

    @w2c(W2CSchema, 'subscription_info_window')
    def handleSubscriptionInfoWindow(self, cmd):
        WotPlusInfoPageLogger().logInfoPage(WotPlusInfoPageSource.SHOP)

    @w2c(_RenewableSubRentVehicleInfoSchema, 'subscription_rent_delayed')
    def subscriptionRentDelayed(self, cmd):
        if cmd.vehCD:
            self._wotPlusCtrl.setRentPending(cmd.vehCD)
            vehName = getUserName(getVehicleType(cmd.vehCD))
            SystemMessages.pushMessage('', messageData={'header': backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.tankRental.isPending.title()),
             'text': backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.tankRental.isPending.text(), vehicle=vehName)}, type=SystemMessages.SM_TYPE.MessageHeader)
