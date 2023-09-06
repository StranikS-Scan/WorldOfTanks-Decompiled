# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/skeletons/story_mode_fading_controller.py
from skeletons.gui.game_control import IGameController

class IStoryModeFadingController(IGameController):

    def show(self, layerID):
        raise NotImplementedError

    def hide(self, layerID):
        raise NotImplementedError
