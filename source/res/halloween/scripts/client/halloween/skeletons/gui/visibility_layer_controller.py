# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/skeletons/gui/visibility_layer_controller.py
from skeletons.gui.game_control import IGameController

class IHalloweenVisibilityLayerController(IGameController):
    onChangeVisibilityMask = None

    def changeVisibilityMask(self, phaseIndex):
        raise NotImplementedError
