# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/DebugManager.py
from typing import TYPE_CHECKING, Iterable, Dict
try:
    import DebugManagerImpl
except ImportError:
    DebugManagerImpl = None

if TYPE_CHECKING:
    from Math import Vector2, Vector3

class COLORS(object):
    GREEN = 1996554018
    DARK_GREEN = 2147516501L
    DARK_BLUE = 4278190335L
    WHITE = 4294967295L
    BLUE = 3137404927L
    RED = 4289864226L
    ZERO = 0
    DEFAULT = BLUE


def _impl(f):
    return getattr(DebugManagerImpl, f.__name__, f)


@_impl
def registerObject(groupID, name):
    pass


@_impl
def clearObject(groupID, name):
    pass


@_impl
def isGroupEnabled(groupID):
    return False


@_impl
def setGroupEnabled(groupID, isEnabled):
    pass


@_impl
def removeObject(groupID, name):
    pass


@_impl
def removeGroup(groupID):
    pass


@_impl
def showMessage(groupID, name, value):
    pass


@_impl
def showText3D(groupID, name, info, position=(0, 1, 0), entityID=None):
    pass


@_impl
def showText2D(groupID, name, text, position, isPixels=False, color=COLORS.DEFAULT):
    pass


@_impl
def showPoint2D(groupID, name, positions, isPixels=False, color=COLORS.DEFAULT):
    pass


@_impl
def showLine2D(groupID, name, positions, isLabel=False, isPixels=False, color=COLORS.DEFAULT):
    pass


@_impl
def showCircle2D(groupID, name, center, radius, isPixels=False, color=COLORS.DEFAULT):
    pass


@_impl
def showRectangle2D(groupID, name, start, end, isPixels=False, color=COLORS.DEFAULT):
    pass


@_impl
def showLine3D(groupID, name, positions, entityID=None, isArrow=False, color=COLORS.DEFAULT):
    pass


@_impl
def showPoint3D(groupID, name, positions, entityID=None, color=COLORS.DEFAULT):
    pass


@_impl
def showBox3D(groupID, name, center, direction=(0, 0, 1), size=(1, 1, 1), entityID=None, color=COLORS.DEFAULT):
    pass


@_impl
def showCircle3D(groupID, name, center, radius, entityID=None, normal=(0, 1, 0), color=COLORS.DEFAULT, segments=36):
    pass


@_impl
def showSphere(groupID, name, center, radius, entityID=None, color=COLORS.DEFAULT):
    pass


@_impl
def showCylinder(groupID, name, start, end, radius, entityID=None, color=COLORS.DEFAULT):
    pass
