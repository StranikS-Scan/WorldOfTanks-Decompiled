# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/trade_in.py
import logging
import time
import typing
import AccountCommands
if typing.TYPE_CHECKING:
    from Account import PlayerAccount
_logger = logging.getLogger(__name__)
_SECONDS_IN_DAY = 86400

class TradeIn(object):

    def __init__(self):
        self._account = None
        return

    def setAccount(self, account):
        self._account = account

    def addTokenDev(self, tokenID, expiryTimeOffset=_SECONDS_IN_DAY):
        currentTime = time.time()
        expiryTime = int(currentTime + expiryTimeOffset)
        self._account._doCmdIntStr(AccountCommands.CMD_TRADE_IN_ADD_TOKEN, expiryTime, tokenID, self._onCmdResponseReceived)

    def removeTokenDev(self, tokenID):
        self._account._doCmdStr(AccountCommands.CMD_TRADE_IN_REMOVE_TOKEN, tokenID, self._onCmdResponseReceived)

    def _onCmdResponseReceived(self, resultID, requestID, errorStr, errorMsg=None):
        if not AccountCommands.isCodeValid(requestID):
            _logger.error((errorStr, errorMsg))
