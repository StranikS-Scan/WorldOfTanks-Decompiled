# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/windows/standard_window.py
from frameworks.wulf import Window
from frameworks.wulf import WindowFlags
from gui.development.ui.gen.view_models.demo_window.window_model import WindowModel
from gui.impl.windows.window_view import WindowView

class StandardWindow(Window):
    __slots__ = ()

    def __init__(self, contentID, contentClazz, *args, **kwargs):
        content = contentClazz(contentID, *args, **kwargs)
        super(StandardWindow, self).__init__(WindowFlags.WINDOW, WindowView(), content)

    @property
    def windowModel(self):
        return super(StandardWindow, self)._getDecoratorViewModel()
