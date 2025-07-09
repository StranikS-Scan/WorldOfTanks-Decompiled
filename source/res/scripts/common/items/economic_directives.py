# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/economic_directives.py
from abc import ABCMeta, abstractproperty
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Tuple

class Modifier(object):
    __metaclass__ = ABCMeta

    def __init__(self, value):
        self.value = value

    nameValueReplay = abstractproperty(lambda *_: None)
    operand = abstractproperty(lambda *_: None)
    resultName = abstractproperty(lambda *_: None)
    resultFactor = abstractproperty(lambda *_: None)


class Credits(Modifier):
    nameValueReplay = property(lambda self: 'creditsReplay')
    operand = property(lambda self: 'subtotalCredits')
    resultName = property(lambda self: 'directivesCredits')
    resultFactor = property(lambda self: 'directivesCreditsFactor100')


class Xp(Modifier):
    nameValueReplay = property(lambda self: 'xpReplay')
    operand = property(lambda self: 'subtotalXP')
    resultName = property(lambda self: 'directivesXP')
    resultFactor = property(lambda self: 'directivesXPFactor100')


class CrewXp(Modifier):
    nameValueReplay = property(lambda self: 'tmenXPReplay')
    operand = property(lambda self: 'subtotalTMenXP')
    resultName = property(lambda self: 'directivesTMenXP')
    resultFactor = property(lambda self: 'directivesTMenXPFactor100')


class FreeXp(Modifier):
    nameValueReplay = property(lambda self: 'freeXPReplay')
    operand = property(lambda self: 'subtotalFreeXP')
    resultName = property(lambda self: 'directivesFreeXP')
    resultFactor = property(lambda self: 'directivesFreeXPFactor100')


def getSubclasses(cls):
    return {subclass.__name__:subclass for subclass in cls.__subclasses__()}


class Operation(object):

    def __init__(self, operationType, modifiers):
        self.operationType = operationType
        self.modifierList = []
        modifiersClass = getSubclasses(Modifier)
        for m, v in modifiers:
            cls = modifiersClass.get(m)
            if cls:
                modifier = cls(v)
                self.modifierList.append(modifier)
