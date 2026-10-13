# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/PortalAccountComponent.py
import AccountCommands
import BigWorld
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from PlayerEvents import g_playerEvents as events
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils import decorators
from gui.shared.gui_items.processors import Processor, makeError
from helpers import dependency
from events_core_client.account_settings.account_event_settings_handler import AccountEventSettingsHandler
from portal_common.account_commands_extension import CMD_PORTAL_INSTALL_UPGRADE, CMD_PORTAL_RESET_UPGRADE, CMD_PURCHASE_TOKEN
from portal_common.portal_constants import PORTAL_ACCOUNT_SETTINGS_KEY, PORTAL_EXPIRE_DATE_ACCOUNT_SETTINGS
from portal.skeletons.portal_event_controller import IPortalEventController

class PortalAccountComponent(BaseAccountExtensionComponent):
    __portalEventController = dependency.descriptor(IPortalEventController)

    def __init__(self):
        BaseAccountExtensionComponent.__init__(self)
        self._ignore = True
        events.onAccountBecomeNonPlayer += self.onAccountBecomeNonPlayer
        events.onAccountBecomePlayer += self.onAccountBecomePlayer
        self.__accountSettingsHandler = AccountEventSettingsHandler(PORTAL_ACCOUNT_SETTINGS_KEY, PORTAL_EXPIRE_DATE_ACCOUNT_SETTINGS, self.__portalEventController)

    def enqueueBattle(self, queueType, vehInvID, battleLevel):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, (queueType, vehInvID, battleLevel))

    def dequeueBattle(self, queueType):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, queueType)

    @decorators.adisp_process('updating')
    def processPurchaseToken(self):
        proc = PurchaseToken()
        result = yield proc.request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def purchaseToken(self, callback=None):
        if self._ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, [])
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
            else:
                proxy = None
            self.entity._doCmdInt(CMD_PURCHASE_TOKEN, 1, proxy)
            return

    def onAccountBecomePlayer(self):
        self._ignore = False
        events.onAccountBecomePlayer -= self.onAccountBecomePlayer

    def onAccountBecomeNonPlayer(self):
        self._ignore = True
        events.onAccountBecomeNonPlayer -= self.onAccountBecomeNonPlayer

    def upgradeVehicle(self, vehInvID, vehCD, upgradeNodeNumber, callback):
        self.entity._doCmdInt3(CMD_PORTAL_INSTALL_UPGRADE, vehInvID, vehCD, upgradeNodeNumber, callback)

    def resetVehicleUpgrades(self, vehInvID, vehCD, callback):
        self.entity._doCmdInt2(CMD_PORTAL_RESET_UPGRADE, vehInvID, vehCD, callback)


class PurchaseToken(Processor):

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeError(backport.text(R.strings.exm_lobby.buy.server_error()))

    def _request(self, callback):
        portalAccComponent = getattr(BigWorld.player(), 'PortalAccountComponent', None)
        if portalAccComponent:
            portalAccComponent.purchaseToken(lambda code: self._response(code, callback))
        return
