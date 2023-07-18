# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/debut_boxes/debut_boxes_browser_view.py
from gui.impl.lobby.common.browser_view import BrowserView
from helpers import dependency
from skeletons.gui.game_control import IDebutBoxesController

class DebutBoxesBrowserView(BrowserView):
    __debutBoxesController = dependency.descriptor(IDebutBoxesController)

    def _onLoading(self, *args, **kwargs):
        super(DebutBoxesBrowserView, self)._onLoading(*args, **kwargs)
        self.__debutBoxesController.onStateChanged += self.__onStateChanged

    def _finalize(self):
        self.__debutBoxesController.onStateChanged -= self.__onStateChanged
        super(DebutBoxesBrowserView, self)._finalize()

    def __onStateChanged(self):
        if not self.__debutBoxesController.isEnabled():
            self.onCloseView()
