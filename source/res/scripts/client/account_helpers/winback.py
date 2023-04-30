# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/winback.py
import typing
import AccountCommands
if typing.TYPE_CHECKING:
    from typing import Callable, Optional

class Winback(object):

    def __init__(self, commandsProxy):
        self.__commandsProxy = commandsProxy

    def turnOffBattles(self, reason, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr)
        else:
            proxy = None
        self.__commandsProxy.perform(AccountCommands.CMD_TURNOFF_WINBACK_BATTLES, reason, proxy)
        return
