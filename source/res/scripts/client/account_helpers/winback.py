# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/winback.py
import typing
import AccountCommands
if typing.TYPE_CHECKING:
    from typing import Callable, Optional

class Winback(object):

    def __init__(self, commandsProxy):
        self.__commandsProxy = commandsProxy

    def drawWinbackSelectorHintToken(self, callback):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr)
        else:
            proxy = None
        self.__commandsProxy.perform(AccountCommands.CMD_DRAW_WINBACK_SELECTOR_HINT_TOKEN, 0, proxy)
        return
