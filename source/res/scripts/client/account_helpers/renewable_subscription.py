# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/renewable_subscription.py
import logging
from functools import partial
import typing
import AccountCommands
from Event import Event
from account_helpers import AccountSyncData
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events import settings
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from piggy_bank_common.settings_constants import PIGGY_BANK_PDATA_KEY
from renewable_subscription_common.settings_constants import RS_PDATA_KEY, IDLE_CREW_XP_PDATA_KEY, IDLE_CREW_VEH_INV_ID, SUBSCRIPTION_DURATION_LENGTH
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Callable, Optional, Union
    from Account import PlayerAccount
    from gui.shared.gui_items import ItemsCollection
_logger = logging.getLogger(__name__)
_SECONDS_IN_DAY = 86400

class RenewableSubscription(object):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, syncData):
        self._account = None
        self._syncData = syncData
        self._cache = {}
        self.onRenewableSubscriptionDataChanged = Event()
        self.onPendingRentChanged = Event()
        self._ignore = True
        return

    def onAccountBecomePlayer(self):
        self._ignore = False

    def onAccountBecomeNonPlayer(self):
        self._ignore = True

    def setAccount(self, account):
        self._account = account

    def synchronize(self, isFullSync, diff):
        if isFullSync:
            self._cache.clear()
        itemDiff = diff.get(RS_PDATA_KEY, {})
        if IDLE_CREW_XP_PDATA_KEY in diff:
            itemDiff[IDLE_CREW_XP_PDATA_KEY] = diff[IDLE_CREW_XP_PDATA_KEY]
        if PIGGY_BANK_PDATA_KEY in diff:
            itemDiff[PIGGY_BANK_PDATA_KEY] = diff[PIGGY_BANK_PDATA_KEY]
        if itemDiff:
            synchronizeDicts(itemDiff, self._cache)
            self.onRenewableSubscriptionDataChanged(itemDiff)

    def getCache(self, callback=None):
        if self._ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self._syncData.waitForSync(partial(self._onGetCacheResponse, callback))
            return

    def toggleRenewableSubDev(self):
        self._account._doCmdInt(AccountCommands.CMD_TOGGLE_RENEWABLE_SUB_DEV, 0, self._onCmdResponseReceived)

    def activateRenewableSubDev(self, expirySecondsInFuture=_SECONDS_IN_DAY):
        self._account._doCmdInt(AccountCommands.CMD_ACTIVATE_RENEWABLE_SUB_DEV, expirySecondsInFuture, self._onCmdResponseReceived)

    def simulateNewGameDay(self):
        self._account._doCmdInt(AccountCommands.CMD_WOT_PLUS_NEW_GAME_DAY, 0, self._onCmdResponseReceived)

    def simulateRentTank(self, tankId):
        self._account._doCmdInt(AccountCommands.CMD_WOT_PLUS_RENT_TANK, tankId, self._onCmdResponseReceived)

    def idleCrewXPSelectVehicle(self, vehicleInvID, errorCallback):

        def callback(resultID, requestID, errorStr, errorMsg=None):
            if AccountCommands.isCodeValid(requestID):
                _logger.debug('[RenewableSubscription] _onIdleCrewXPVehicleSelected SUCCESS')
                return
            if requestID == AccountCommands.RES_NOT_AVAILABLE:
                SystemMessages.pushMessage(backport.text(R.strings.messenger.serviceChannelMessages.wotPlus.passiveXP.isDisabled.title()), type=SystemMessages.SM_TYPE.Warning)
            _logger.warning((errorStr, errorMsg))
            errorCallback()

        if vehicleInvID is None:
            vehicleInvID = -1
        self._account._doCmdInt(AccountCommands.CMD_IDLE_CREW_XP_SELECT_VEHICLE, vehicleInvID, callback=callback)
        return

    def setReservesDev(self, creditsVal, goldVal):
        self._account._doCmdInt2(AccountCommands.CMD_SET_RESERVES_PIGGY_BANK_DEV, creditsVal, goldVal, self._onCmdResponseReceived)

    def smashPiggyBankDev(self):
        self._account._doCmdInt(AccountCommands.CMD_SMASH_PIGGY_BANK_DEV, 6, self._onCmdResponseReceived)

    def isEnabled(self):
        return self._cache['isEnabled']

    def getExpiryTime(self):
        return self._cache['expiry']

    def getStartTime(self):
        return self._cache['expiry'] - SUBSCRIPTION_DURATION_LENGTH

    def getGoldReserve(self):
        return self._cache.get('piggyBank', {}).get('gold')

    def vehicleCrewHasIdleXP(self, vehicleInvID):
        return self._cache.get(IDLE_CREW_XP_PDATA_KEY, {}).get(IDLE_CREW_VEH_INV_ID) == vehicleInvID

    def getVehicleIDWithIdleXP(self):
        return self._cache.get(IDLE_CREW_XP_PDATA_KEY, {}).get(IDLE_CREW_VEH_INV_ID)

    def getRentVehicle(self):
        return self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.WOTPLUS_RENT)

    def setRentPending(self, vehCD):
        with settings.wotPlusSettings() as dt:
            dt.setRentPending(vehCD)
        self.onPendingRentChanged(vehCD)

    def getRentPending(self):
        return settings.getWotPlusSettings().rentPendingVehCD

    def resetRentPending(self):
        with settings.wotPlusSettings() as dt:
            dt.setRentPending(None)
        self.onPendingRentChanged(None)
        return

    def _onGetCacheResponse(self, callback, resultID):
        if self._ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        elif resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self._cache)
            return

    def _onCmdResponseReceived(self, resultID, requestID, errorStr, errorMsg=None):
        if not AccountCommands.isCodeValid(requestID):
            _logger.error((errorStr, errorMsg))
