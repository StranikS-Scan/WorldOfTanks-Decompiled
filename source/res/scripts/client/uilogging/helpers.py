# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/helpers.py
import typing
import BigWorld
if typing.TYPE_CHECKING:
    from uilogging.base.logger import LOGGERS_TYPING

class _LazyLoggerDescriptor(object):
    __slots__ = ('__class', '__args', '__kwargs', '__instance')

    def __init__(self, class_, *args, **kwargs):
        self.__class = class_
        self.__args = args
        self.__kwargs = kwargs
        self.__instance = None
        return

    def __set__(self, *_, **__):
        raise AttributeError('% is readonly' % self.__class__.__name__)

    def __get__(self, *_, **__):
        if not self.__instance:
            self.__instance = self.__class(*self.__args, **self.__kwargs)
        return self.__instance


def lazyUILogger(class_, *args, **kwargs):
    return _LazyLoggerDescriptor(class_, *args, **kwargs)


def getClientSessionID():
    return '' if BigWorld.player() is None else str(BigWorld.player().connectionMgr.lastSessionID)


def getClientPeripheryID():
    return 0 if BigWorld.player() is None else BigWorld.player().connectionMgr.peripheryID
