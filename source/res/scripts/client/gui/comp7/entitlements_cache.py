# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/comp7/entitlements_cache.py
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import COMP7_ENTITLEMENTS, COMP7_ENTITLEMENTS_TIMESTAMP, COMP7_ENTITLEMENTS_BALANCE
from adisp import adisp_process
from comp7_common import eliteRankEntNameBySeasonNumber, ratingEntNameBySeasonNumber
from gui.entitlements.entitlements_requester import EntitlementsRequester
from helpers.time_utils import ONE_DAY, getServerUTCTime
_logger = logging.getLogger(__name__)

class EntitlementsCache(object):
    __slots__ = ('__requester',)
    __COMP7_ENTITLEMENTS_NAMES = [eliteRankEntNameBySeasonNumber(1),
     eliteRankEntNameBySeasonNumber(2),
     ratingEntNameBySeasonNumber(1),
     ratingEntNameBySeasonNumber(2)]
    __EXPIRY_TIME = ONE_DAY

    def __init__(self):
        self.__requester = EntitlementsRequester()

    def reset(self):
        self.__requester.clear()

    def clear(self):
        self.__requester.clear()
        self.__requester = None
        return

    def isExpired(self):
        currentTimestamp = getServerUTCTime()
        return currentTimestamp > self.__getCacheTimestamp() + self.__EXPIRY_TIME

    def isEntitlementCached(self, entitlementName):
        return entitlementName in self.__COMP7_ENTITLEMENTS_NAMES and self.__getCacheTimestamp()

    def getEntitlementCount(self, entitlementName):
        balance = AccountSettings.getSettings(COMP7_ENTITLEMENTS).get(COMP7_ENTITLEMENTS_BALANCE, {})
        return balance.get(entitlementName, 0)

    @adisp_process
    def update(self, callback=None):
        isSuccess, result = yield self.__requester.requestByCodes(self.__COMP7_ENTITLEMENTS_NAMES)
        if isSuccess:
            balance = {ent:result.get(ent, {}).get('amount', 0) for ent in self.__COMP7_ENTITLEMENTS_NAMES}
            comp7Entitlements = {COMP7_ENTITLEMENTS_TIMESTAMP: getServerUTCTime(),
             COMP7_ENTITLEMENTS_BALANCE: balance}
            AccountSettings.setSettings(COMP7_ENTITLEMENTS, comp7Entitlements)
        else:
            _logger.error('Failed to update comp7 entitlements cache through agate')
        if callback is not None:
            callback(isSuccess)
        return

    def __getCacheTimestamp(self):
        return AccountSettings.getSettings(COMP7_ENTITLEMENTS).get(COMP7_ENTITLEMENTS_TIMESTAMP, 0)
