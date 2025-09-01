# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/callable_delayer.py
import typing
from Event import Event
if typing.TYPE_CHECKING:
    from frameworks.wulf import View as WulfView
    from gui.Scaleform.framework.entities.View import View

class CallableDelayer(object):

    class _CleanupWrapper(object):

        def __init__(self, event, wrappedFn, owningList):
            self.__event = event
            self.__wrappedFn = wrappedFn
            self.__owningList = owningList
            self.__event += self

        def __del__(self):
            self.clear()

        def __call__(self):
            self.__wrappedFn()
            self.clear()

        def clear(self):
            if self.__event:
                self.__event -= self
            if self.__owningList:
                self.__owningList.remove(self)
                self.__owningList = None
            return

    def __init__(self):
        self.__wrappers = []

    def __del__(self):
        self.clear()

    def delayUntilEvent(self, event, fn):
        self.__wrappers.append(self._CleanupWrapper(event, fn, self.__wrappers))

    def clear(self):
        for wrapper in self.__wrappers:
            wrapper.clear()

        self.__wrappers[:] = []


def delayUntilParentWindowReady(delayer, view, fn):
    if view:
        window = view.getParentWindow()
        if window and window.isReady:
            fn()
        else:
            delayer.delayUntilEvent(window.onReady, fn)
    else:
        fn()
