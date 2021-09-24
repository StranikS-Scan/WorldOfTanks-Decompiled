# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Followee.py
import BigWorld
import ArenaComponents
from script_component.DynamicScriptComponent import DynamicScriptComponent

class Followee(DynamicScriptComponent):

    def onAvatarReady(self):
        follower = BigWorld.entities.get(self.followerID)
        followerGO = follower.entityGameObject if follower else None
        appearance = self.entity.appearance
        if appearance is not None:
            appearance.createComponent(ArenaComponents.CarryingLootComponent, followerGO)
        return

    def onDestroy(self):
        appearance = self.entity.appearance
        if appearance is not None:
            appearance.removeComponentByType(ArenaComponents.CarryingLootComponent)
        super(Followee, self).onDestroy()
        return
