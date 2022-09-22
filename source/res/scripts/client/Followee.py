# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Followee.py
import BigWorld
import GenericComponents
from script_component.DynamicScriptComponent import DynamicScriptComponent

class Followee(DynamicScriptComponent):

    def _onAvatarReady(self):
        follower = BigWorld.entities.get(self.followerID)
        followerGO = follower.entityGameObject if follower else None
        appearance = self.entity.appearance
        if appearance is not None:
            appearance.createComponent(GenericComponents.CarryingLootComponent, followerGO)
        return

    def onDestroy(self):
        appearance = self.entity.appearance
        if appearance is not None:
            appearance.removeComponentByType(GenericComponents.CarryingLootComponent)
        super(Followee, self).onDestroy()
        return
