# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/fading_controller.py
from gui.impl.common.fade_manager import FadeManager, DefaultFadingCover
from wg_async import wg_await, wg_async
from skeletons.gui.game_control import IFadingController

class FadingController(IFadingController):

    def __init__(self):
        super(FadingController, self).__init__()
        self._managerByLayer = {}

    @wg_async
    def show(self, layerID):
        fadeManager = self._getFadeManager(layerID)
        if not fadeManager.isAnimating:
            yield wg_await(fadeManager.show())

    @wg_async
    def hide(self, layerID):
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
        fadeManager = FadeManager(layer=layerID, coverFactory=DefaultFadingCover)
        self._managerByLayer[layerID] = fadeManager
        return fadeManager
