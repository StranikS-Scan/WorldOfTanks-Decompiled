# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Triggers.py
from __future__ import absolute_import
from builtins import object
import typing
if typing.TYPE_CHECKING:
    from Math import Vector3, Vector2
    import CGF

class AreaTriggerComponent(object):
    id = None
    objectsInProximity = None
    valid = None

    def addEnterReaction(self, reaction):
        pass

    def addExitReaction(self, reaction):
        pass

    def addFilter(self, filter, dynamic=False):
        pass

    def destroy(self, *args):
        pass

    def removeEnterReaction(self, id):
        pass

    def removeExitReaction(self, id):
        pass


class AreaTriggerTarget(object):
    id = None
    valid = None

    def destroy(self, *args):
        pass


class CylinderAreaComponent(object):
    height = None
    id = None
    radius = None
    valid = None

    def __init__(self, height, radius):
        pass

    def destroy(self, *args):
        pass


class PrismAreaComponent(object):
    height = None
    id = None
    points = None
    valid = None

    def __init__(self, points, height, minHeight, maxHeight):
        pass

    def destroy(self, *args):
        pass


class SquareAreaComponent(object):
    id = None
    maxBounds = None
    minBounds = None
    valid = None

    def __init__(self, minBounds, maxBounds):
        pass

    def destroy(self, *args):
        pass


class TimeTriggerComponent(object):
    counter = None
    id = None
    valid = None

    def __init__(self, deltaTime=0.0, repeatCount=1):
        pass

    def addFireReaction(self, reaction):
        pass

    def destroy(self, *args):
        pass

    def removeFireReaction(self, index):
        pass

    def reset(self, delta, count=1):
        pass
