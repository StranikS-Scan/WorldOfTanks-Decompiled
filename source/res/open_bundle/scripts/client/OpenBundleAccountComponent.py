# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/OpenBundleAccountComponent.py
import typing
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from open_bundle_common.open_bundle_account_commands import CMD_OPEN_BUNDLE_PROCESS_NEXT_STEP
if typing.TYPE_CHECKING:
    from typing import Callable, Optional

def _getAccountRepository():
    import Account
    return Account.g_accountRepository


class OpenBundleAccountComponent(BaseAccountExtensionComponent):

    def processNextStep(self, bundleID, stepNumber, callback):
        repository = _getAccountRepository()
        if repository is None:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, 'NON_PLAYER', None)
            return
        else:
            if callback is not None:
                proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID, errorStr, ext)
            else:
                proxy = None
            repository.commandProxy.perform(CMD_OPEN_BUNDLE_PROCESS_NEXT_STEP, bundleID, stepNumber, proxy)
            return
