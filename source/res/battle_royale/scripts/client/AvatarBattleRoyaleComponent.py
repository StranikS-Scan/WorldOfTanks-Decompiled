# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/AvatarBattleRoyaleComponent.py
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class AvatarBattleRoyaleComponent(BigWorld.DynamicScriptComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def set_playerPlace(self, _prev):
        self.sessionProvider.arenaVisitor.getComponentSystem().battleRoyaleComponent.setBattleRoyalePlace(self.playerPlace)
