# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/view/view_event.py
import typing

class Position2D(object):
    __slots__ = ('__positionX', '__positionY')

    def __init__(self, x=0, y=0):
        super(Position2D, self).__init__()
        self.__positionX = x
        self.__positionY = y

    @property
    def positionX(self):
        return self.__positionX

    @property
    def positionY(self):
        return self.__positionY


class BoundingBox(Position2D):
    __slots__ = ('__width', '__height')

    def __init__(self, x=0, y=0, width=0, height=0):
        super(BoundingBox, self).__init__(x, y)
        self.__width = width
        self.__height = height

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height


class ViewEvent(object):
    __slots__ = ('__core',)

    def __init__(self, core):
        super(ViewEvent, self).__init__()
        self.__core = core

    def __repr__(self):
        return '{}(proxy={})'.format(self.__class__.__name__, self.__core)

    @property
    def eventType(self):
        return self.__core.eventType

    @property
    def decoratorID(self):
        return self.__core.decoratorID

    @property
    def contentID(self):
        return self.__core.contentID

    @property
    def isOn(self):
        return self.__core.isOn

    @property
    def mouse(self):
        return Position2D(*self.__core.mouse)

    @property
    def bbox(self):
        return BoundingBox(*self.__core.bbox)

    @property
    def direction(self):
        return self.__core.direction

    def hasArgument(self, name):
        return self.__core.hasArgument(name)

    def getArgument(self, name, default=None):
        return self.__core.getArgument(name) if self.hasArgument(name) else default
