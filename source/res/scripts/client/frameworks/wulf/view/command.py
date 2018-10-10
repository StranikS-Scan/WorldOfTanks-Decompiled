# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/view/command.py
import typing
from Event import Event
import GUI
from ..py_object_binder import PyObjectEntity

class Command(PyObjectEntity):
    __slots__ = ('__event',)

    def __init__(self):
        super(Command, self).__init__(GUI.PyObjectCommand())
        self.__event = Event()

    @property
    def name(self):
        return self.proxy.name

    def execute(self, args=None):
        if args is not None:
            args = (args,)
        else:
            args = ()
        self.proxy.execute(*args)
        return

    def _unbind(self):
        self.__event.clear()
        super(Command, self)._unbind()

    def _cNotify(self, args=None):
        if args is not None:
            args = (args,)
        else:
            args = ()
        self.__event(*args)
        return

    def __iadd__(self, delegate):
        self.__event += delegate
        return self

    def __isub__(self, delegate):
        self.__event -= delegate
        return self
