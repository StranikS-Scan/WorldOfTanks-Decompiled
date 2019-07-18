# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/component.py
from typing import List

class Slot(object):

    def __init__(self, isInput, name, dataType, func, editorType=None):
        self.isInput = isInput
        self.name = name
        self.dataType = dataType
        self.func = func
        self.editorType = editorType


class InputSlot(Slot):

    def __init__(self, name, dataType, func, editorType=None):
        Slot.__init__(self, True, name, dataType, func, editorType)


class OutputSlot(Slot):

    def __init__(self, name, dataType, func):
        Slot.__init__(self, False, name, dataType, func)


class ArrayConnection(object):

    def __init__(self, name, dataType):
        self.name = name
        self.dataType = dataType


class ASPECT(object):
    SERVER = 'SERVER'
    CLIENT = 'CLIENT'


class SLOT_TYPE(object):
    BOOL = 1
    STR = 2
    INT = 3
    FLOAT = 4
    EVENT = 5
    VECTOR2 = 6
    VECTOR3 = 7
    VECTOR4 = 8
    MATRIX = 9
    ANGLE = 10


class EDITOR_TYPE(object):
    SPLINE_NAME_SELECTOR = 1


class Component(object):

    @classmethod
    def componentName(cls):
        return cls.__name__

    @classmethod
    def componentModule(cls):
        return cls.__module__

    @classmethod
    def componentAspects(cls):
        return [ASPECT.SERVER, ASPECT.CLIENT]

    @classmethod
    def componentIcon(cls):
        pass

    @classmethod
    def componentColor(cls):
        pass

    @classmethod
    def componentCategory(cls):
        pass

    @classmethod
    def arrayConnections(cls):
        return []

    def slotDefinitions(self):
        return []

    def captionText(self):
        pass

    def onFinishScript(self):
        pass
