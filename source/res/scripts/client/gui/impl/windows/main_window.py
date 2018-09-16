# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/windows/main_window.py
from frameworks.wulf import WindowFlags, Window

class MainWindow(Window):
    __slots__ = ()

    def __init__(self, flags, contentClazz, *args, **kwargs):
        if contentClazz is not None:
            content = contentClazz(*args, **kwargs)
        else:
            content = None
        super(MainWindow, self).__init__(wndFlags=WindowFlags.MAIN_WINDOW | WindowFlags.RESIZABLE | flags, decorator=None, content=content, parent=None)
        return
