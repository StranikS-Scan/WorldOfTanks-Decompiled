# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/SpringboardEffectComponent.py
import BigWorld
from cosmic_sound import CosmicBattleSounds

class SpringboardEffectComponent(BigWorld.DynamicScriptComponent):

    def set_timeApply(self, _):
        CosmicBattleSounds.playBoardJump(self.entity.position)
