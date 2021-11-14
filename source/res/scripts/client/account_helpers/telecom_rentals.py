# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/telecom_rentals.py
import logging
import typing
import AccountCommands
from Event import Event
from account_helpers import AccountSyncData
from gui.server_events import settings
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from telecom_rentals_common import PartnershipState, PARTNERSHIP_BLOCKED_TOKEN_NAME
from telecom_rentals_common import ROSTER_EXPIRATION_TOKEN_NAME, PARTNERSHIP_TOKEN_NAME
if typing.TYPE_CHECKING:
    from Account import PlayerAccount
    from typing import Set
_logger = logging.getLogger(__name__)

class TelecomRentals(object):
    itemsCache = dependency.descriptor(IItemsCache)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, syncData):
        self._account = None
        self._syncData = syncData
        self._tokens = None
        self.onPendingRentChanged = Event()
        self._ignore = True
        return

    def onAccountBecomePlayer(self):
        self._ignore = False

    def onAccountBecomeNonPlayer(self):
        self._ignore = True

    def setAccount(self, account):
        self._account = account
        self._tokens = self._account.tokens

    def synchronize(self, isFullSync, diff):
        pass

    def togglePartnership(self, partnershipState):
        self._account._doCmdInt(AccountCommands.CMD_TELECOM_RENTALS_TOGGLE_ACTIVE, partnershipState, self._onCmdResponseReceived)

    def setRentalTokensDev(self, amount):
        self._account._doCmdInt(AccountCommands.CMD_TELECOM_RENTALS_VEHICLE_RENT_AMOUNT, amount, self._onCmdResponseReceived)

    def hasPartnership(self):
        subscritionToken = self._tokens.getToken(PARTNERSHIP_TOKEN_NAME)
        return bool(subscritionToken)

    def isBlocked(self):
        subscritionToken = self._tokens.getToken(PARTNERSHIP_BLOCKED_TOKEN_NAME)
        return bool(subscritionToken)

    def isActive(self):
        serverSettings = self._lobbyContext.getServerSettings()
        isRentalEnabled = serverSettings.isTelecomRentalsEnabled()
        subscritionToken = self.hasPartnership()
        return True if subscritionToken and isRentalEnabled else False

    def getRosterExpirationTime(self):
        rosterToken = self._tokens.getToken(ROSTER_EXPIRATION_TOKEN_NAME)
        return rosterToken[0] if rosterToken else 0

    def getTotalRentCount(self):
        rentToken = self._tokens.getToken(ROSTER_EXPIRATION_TOKEN_NAME)
        return 0 if not rentToken else rentToken[1]

    def getAvailableRentCount(self):
        rentToken = self._tokens.getToken(ROSTER_EXPIRATION_TOKEN_NAME)
        if not rentToken:
            return 0
        telecomVehiclesCount = len(self.itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.TELECOM_RENT))
        return max(0, rentToken[1] - telecomVehiclesCount)

    def setRentPending(self, vehCD):
        with settings.telecomRentalsSettings() as dt:
            dt.setRentPending(vehCD)
        self.onPendingRentChanged(vehCD)

    def getRentsPending(self):
        return settings.getTelecomRentalsSettings().pendingRentals

    def resetRentsPending(self, vehCDs):
        with settings.telecomRentalsSettings() as dt:
            for vehCD in vehCDs:
                dt.resetRentPending(vehCD)

        self.onPendingRentChanged(None)
        return

    def simulateRentTank(self, tankId):
        self._account._doCmdInt(AccountCommands.CMD_TELECOM_RENTALS_RENT_TANK, tankId, self._onCmdResponseReceived)

    def _onCmdResponseReceived(self, resultID, requestID, errorStr, errorMsg=None):
        if not AccountCommands.isCodeValid(requestID):
            _logger.error((errorStr, errorMsg))
