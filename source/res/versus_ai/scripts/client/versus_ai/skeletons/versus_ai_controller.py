# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/skeletons/versus_ai_controller.py
from skeletons.gui.game_control import IGameController

class IVersusAIController(IGameController):

    def isEnabled(self):
        raise NotImplementedError
