# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/wait_view_impl.py
from async import async, await, BrokenPromiseError, AsyncScope, AsyncEvent, AsyncReturn
from frameworks.wulf import WindowLayer
from gui.impl.pub import ViewImpl
from gui.impl.pub.dialog_window import DialogFlags
from gui.impl.pub.lobby_window import LobbyNotificationWindow

class WaitViewImpl(ViewImpl):
    __slots__ = ('__event', '__scope', '__result')

    def __init__(self, *args, **kwargs):
        super(WaitViewImpl, self).__init__(*args, **kwargs)
        self.__scope = AsyncScope()
        self.__event = AsyncEvent(scope=self.__scope)
        self.__result = None
        return

    @async
    def wait(self):
        try:
            yield await(self.__event.wait())
        except BrokenPromiseError:
            pass

        raise AsyncReturn(self.__result)

    def _finalize(self):
        if not self.__event.is_set():
            self.__result = self._getDefaultResult()
        self.__scope.destroy()
        super(WaitViewImpl, self)._finalize()

    def _getDefaultResult(self):
        return None

    def _setResult(self, result=None):
        self.__result = result
        self.__event.set()


class WaitWindowWrapper(LobbyNotificationWindow):
    __slots__ = ('__wrappedView',)

    def __init__(self, wrappedView, wndFlags=DialogFlags.TOP_FULLSCREEN_WINDOW, parent=None, layer=WindowLayer.UNDEFINED):
        super(WaitWindowWrapper, self).__init__(wndFlags=wndFlags, content=wrappedView, parent=parent, layer=layer)
        self.__wrappedView = wrappedView

    def wait(self):
        return self.__wrappedView.wait()
