# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/game_control/story_mode_fading_controller.py
from gui.impl.common.fade_manager import FadeManager, DefaultFadingCover
from story_mode.gui.story_mode_gui_constants import STORY_MODE_FADE_IN_DURATION, STORY_MODE_FADE_OUT_DURATION, IS_STORY_MODE_FADE_IN_OUT_ON
from story_mode.skeletons.story_mode_fading_controller import IStoryModeFadingController
from wg_async import wg_await, wg_async

class StoryModeFadingCover(DefaultFadingCover):

    def __init__(self):
        super(StoryModeFadingCover, self).__init__(fadeInDuration=STORY_MODE_FADE_IN_DURATION, fadeOutDuration=STORY_MODE_FADE_OUT_DURATION)

    @property
    def isModeSelectorAutoCloseDisabled(self):
        return True


class StoryModeFadingController(IStoryModeFadingController):

    def __init__(self):
        super(StoryModeFadingController, self).__init__()
        self._managerByLayer = {}

    @wg_async
    def show(self, layerID):
        if not IS_STORY_MODE_FADE_IN_OUT_ON:
            return
        fadeManager = self._getFadeManager(layerID)
        if not fadeManager.isAnimating:
            yield wg_await(fadeManager.show())

    @wg_async
    def hide(self, layerID):
        if not IS_STORY_MODE_FADE_IN_OUT_ON:
            return
        fadeManager = self._getFadeManager(layerID)
        if fadeManager.isAnimating:
            yield wg_await(fadeManager.hide())

    def onDisconnected(self):
        self._hideImmediately()

    def onAvatarBecomePlayer(self):
        self._hideImmediately()

    def onAccountBecomePlayer(self):
        self._hideImmediately()

    def _hideImmediately(self):
        for fadeManager in self._managerByLayer.itervalues():
            fadeManager.hideImmediately()

    def _getFadeManager(self, layerID):
        if layerID in self._managerByLayer:
            return self._managerByLayer[layerID]
        fadeManager = FadeManager(layer=layerID, coverFactory=StoryModeFadingCover)
        self._managerByLayer[layerID] = fadeManager
        return fadeManager
