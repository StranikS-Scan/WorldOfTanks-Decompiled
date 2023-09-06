# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BaseAccountExtensionComponent.py
import BigWorld
from helpers import isPlayerAccount

class BaseAccountExtensionComponent(BigWorld.StaticScriptComponent):

    @property
    def account(self):
        return self.entity

    @property
    def base(self):
        return self.account.base

    @classmethod
    def instance(cls):
        playerAccount = BigWorld.player()
        return getattr(playerAccount, cls.__name__, None) if isPlayerAccount() and cls.__name__ in playerAccount.components else None
