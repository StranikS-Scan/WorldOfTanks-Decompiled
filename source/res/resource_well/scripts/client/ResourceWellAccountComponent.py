# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/ResourceWellAccountComponent.py
import json
import typing
from resource_well_common.resource_well_account_commands import CMD_RESOURCE_WELL_PUT, CMD_RESOURCE_WELL_TAKE
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
if typing.TYPE_CHECKING:
    from typing import Callable, Optional, List, Tuple

def _getAccountRepository():
    import Account
    return Account.g_accountRepository


class ResourceWellAccountComponent(BaseAccountExtensionComponent):

    def putResources(self, resources, reward, callback):
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
            resourcesStr = json.dumps(resources)
            repository.commandProxy.perform(CMD_RESOURCE_WELL_PUT, [reward, resourcesStr], proxy)
            return

    def takeBack(self, callback):
        repository = _getAccountRepository()
        if repository is None:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER)
            return
        else:
            proxy = (lambda requestID, resultID, errorStr, ext={}: callback(resultID)) if callback is not None else None
            repository.commandProxy.perform(CMD_RESOURCE_WELL_TAKE, 0, proxy)
            return
