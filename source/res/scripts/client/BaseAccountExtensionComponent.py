# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BaseAccountExtensionComponent.py
import BigWorld

class BaseAccountExtensionComponent(BigWorld.StaticScriptComponent):

    @property
    def account(self):
        return self.entity

    @property
    def base(self):
        return self.account.base
