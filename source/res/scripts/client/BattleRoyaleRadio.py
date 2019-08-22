# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BattleRoyaleRadio.py
import BigWorld
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class BattleRoyaleRadio(BigWorld.Entity):
    __brControl = dependency.descriptor(IBattleRoyaleController)

    def onEnterWorld(self, _):
        self.__brControl.voiceoverController.setLobbyVOPosition(self.position)

    def onLeaveWorld(self):
        self.__brControl.voiceoverController.setLobbyVOPosition(None)
        return
