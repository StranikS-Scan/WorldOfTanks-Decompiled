# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/type_traits.py
import Math
from typing import *

def allowEqualNone(eq):

    def wrap(lhs, rhs, *args):
        return lhs == rhs if lhs is None or rhs is None else eq(lhs, rhs, *args)

    return wrap


def equal(lhs, rhs):
    return lhs == rhs


@allowEqualNone
def equalFloat(lhs, rhs):
    return abs(lhs - rhs) < 1e-05


@allowEqualNone
def equalString(lhs, rhs):
    return lhs.lower() == rhs.lower()


@allowEqualNone
def equalVector2(lhs, rhs):
    for i in range(2):
        if not equalFloat(lhs[i], rhs[i]):
            return False

    return True


@allowEqualNone
def equalVector3(lhs, rhs):
    for i in range(3):
        if not equalFloat(lhs[i], rhs[i]):
            return False

    return True


@allowEqualNone
def equalVector4(lhs, rhs):
    for i in range(4):
        if not equalFloat(lhs[i], rhs[i]):
            return False

    return True


@allowEqualNone
def equalMatrix(lhs, rhs):
    for x in range(4):
        for y in range(4):
            if not equalFloat(lhs.get(x, y), rhs.get(x, y)):
                return False

    return True


@allowEqualNone
def equalSeq(lhs, rhs, eq=equal):
    if len(lhs) != len(rhs):
        return False
    for l, r in zip(lhs, rhs):
        if not eq(l, r):
            return False

    return True


EQUAL_COMPARATORS = {'Float': equalFloat,
 'String': equalString,
 'Vector2': equalVector2,
 'Vector3': equalVector3,
 'Vector4': equalVector4,
 'Matrix': equalMatrix,
 'Strings': lambda lhs, rhs: equalSeq(lhs, rhs),
 'WideStrings': lambda lhs, rhs: equalSeq(lhs, rhs),
 'Floats': lambda lhs, rhs: equalSeq(lhs, rhs, equalFloat),
 'Ints': lambda lhs, rhs: equalSeq(lhs, rhs),
 'Vector2s': lambda lhs, rhs: equalSeq(lhs, rhs, equalVector2),
 'Vector3s': lambda lhs, rhs: equalSeq(lhs, rhs, equalVector3),
 'Vector4s': lambda lhs, rhs: equalSeq(lhs, rhs, equalVector4)}

def equalComparator(tp):
    try:
        return EQUAL_COMPARATORS[tp]
    except KeyError:
        return equal


DEFAULT_GETTERS = {'String': lambda : str(),
 'WideString': lambda : unicode(),
 'Float': lambda : 0.0,
 'Int': lambda : 0,
 'Int64': lambda : 0,
 'Vector2': lambda : Math.Vector2(),
 'Vector3': lambda : Math.Vector3(),
 'Vector4': lambda : Math.Vector4(),
 'Matrix': lambda : Math.Matrix(),
 'Bool': lambda : False,
 'Strings': lambda : (),
 'WideStrings': lambda : (),
 'Floats': lambda : (),
 'Ints': lambda : (),
 'Vector2s': lambda : (),
 'Vector3s': lambda : (),
 'Vector4s': lambda : ()}

def defaultGetter(tp):
    try:
        return DEFAULT_GETTERS[tp]
    except KeyError:
        return lambda : None


def default(tp):
    try:
        return DEFAULT_GETTERS[tp]()
    except KeyError:
        return None

    return None
