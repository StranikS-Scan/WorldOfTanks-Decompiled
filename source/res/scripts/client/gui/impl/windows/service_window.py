# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/windows/service_window.py
from frameworks.wulf import Window
from frameworks.wulf import WindowFlags
from gui.development.ui.gen.view_models.demo_window.window_model import WindowModel
from gui.impl.windows.window_view import WindowView

class ServiceWindow(Window):
    __slots__ = ()

    def __init__(self, contentClazz, parentWnd, *args, **kwargs):
        content = contentClazz(*args, **kwargs)
        super(ServiceWindow, self).__init__(wndFlags=WindowFlags.SERVICE_WINDOW | WindowFlags.RESIZABLE, decorator=WindowView(), content=content, parent=parentWnd)

    @property
    def windowModel(self):
        return super(ServiceWindow, self)._getDecoratorViewModel()
