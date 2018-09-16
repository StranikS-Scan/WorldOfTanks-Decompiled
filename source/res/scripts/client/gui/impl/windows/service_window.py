# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/windows/service_window.py
from frameworks.wulf import Window, WindowFlags
from gui.impl.gen.view_models.windows.window_model import WindowModel
from gui.impl.windows.window_view import WindowView

class ServiceWindow(Window):
    __slots__ = ()

    def __init__(self, content=None, parent=None):
        super(ServiceWindow, self).__init__(wndFlags=WindowFlags.SERVICE_WINDOW | WindowFlags.RESIZABLE, decorator=WindowView(), content=content, parent=parent)

    @property
    def windowModel(self):
        return super(ServiceWindow, self)._getDecoratorViewModel()

    def _initialize(self):
        super(ServiceWindow, self)._initialize()
        self.windowModel.onClosed += self._onClosed

    def _finalize(self):
        self.windowModel.onClosed -= self._onClosed
        super(ServiceWindow, self)._finalize()

    def _onClosed(self, _=None):
        self.destroy()
