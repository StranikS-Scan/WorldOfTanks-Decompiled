# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/standard_window.py
from frameworks.wulf import WindowFlags
from gui.impl.gen.view_models.windows.window_model import WindowModel
from gui.impl.pub.window_view import WindowView
from gui.impl.pub.lobby_window import LobbyWindow

class StandardWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, content=None, parent=None):
        super(StandardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.RESIZABLE, decorator=WindowView(), content=content, parent=parent)

    @property
    def windowModel(self):
        return super(StandardWindow, self)._getDecoratorViewModel()

    def _initialize(self):
        super(StandardWindow, self)._initialize()
        self.windowModel.onClosed += self._onClosed

    def _finalize(self):
        self.windowModel.onClosed -= self._onClosed
        super(StandardWindow, self)._finalize()

    def _onClosed(self, _=None):
        self.destroy()
