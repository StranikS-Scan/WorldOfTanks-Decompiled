# Embedded file name: scripts/client/tutorial/data/conditions.py
import functools
from tutorial.data.has_id import HasID
__all__ = ('CONDITION_TYPE', 'CONDITION_STATE', 'FlagCondition', 'GlobalFlagCondition', 'WindowOnSceneCondition', 'VarDefinedCondition', 'VarCompareCondition', 'EffectTriggeredCondition', 'GameItemSimpleStateCondition', 'GameItemRelateStateCondition', 'BonusReceivedCondition', 'Conditions')

class CONDITION_TYPE(object):
    FLAG = 0
    GLOBAL_FLAG = 1
    WINDOW_ON_SCENE = 3
    GAME_ITEM_SIMPLE_STATE = 4
    GAME_ITEM_RELATE_STATE = 5
    VAR_DEFINED = 6
    VAR_COMPARE = 7
    EFFECT_TRIGGERED = 8
    BONUS_RECEIVED = 9
    RANGE = (FLAG,
     GLOBAL_FLAG,
     WINDOW_ON_SCENE,
     GAME_ITEM_SIMPLE_STATE,
     GAME_ITEM_RELATE_STATE,
     VAR_DEFINED,
     VAR_COMPARE,
     EFFECT_TRIGGERED,
     BONUS_RECEIVED)


@functools.total_ordering

class _StateValue(object):
    __slots__ = ('value',)

    def __init__(self, value):
        super(_StateValue, self).__init__()
        self.value = value

    def __repr__(self):
        return '_StateValue({})'.format(self.value)

    def __invert__(self):
        return _StateValue(-self.value)

    def __neg__(self):
        return _StateValue(-self.value)

    def __eq__(self, other):
        return self.value == other.value

    def __gt__(self, other):
        return self.value > other.value

    def __hash__(self):
        return hash(self.value)

    @property
    def base(self):
        return _StateValue(abs(self.value))

    @property
    def positive(self):
        return self.value > 0

    @property
    def negative(self):
        return self.value < 0


class CONDITION_STATE(object):
    UNDEFINED = _StateValue(0)
    ACTIVE = _StateValue(1)
    EQUALS = _StateValue(2)
    SELECTED = _StateValue(3)
    PREMIUM = _StateValue(4)
    UNLOCKED = _StateValue(5)
    XP_ENOUGH = _StateValue(6)
    MONEY_ENOUGH = _StateValue(7)
    LEVEL = _StateValue(8)
    MAY_INSTALL = _StateValue(9)
    RANGE = (UNDEFINED,
     ACTIVE,
     EQUALS,
     SELECTED,
     PREMIUM,
     UNLOCKED,
     XP_ENOUGH,
     MONEY_ENOUGH,
     LEVEL,
     MAY_INSTALL)
    GAME_ITEM_SIMPLE_STATE = (SELECTED,
     PREMIUM,
     UNLOCKED,
     MONEY_ENOUGH)
    GAME_ITEM_RELATE_STATE = (XP_ENOUGH, LEVEL, MAY_INSTALL)


class _Condition(HasID):

    def __init__(self, entityID, condType, state):
        raise condType in CONDITION_TYPE.RANGE or AssertionError
        raise state.base in CONDITION_STATE.RANGE or AssertionError
        super(_Condition, self).__init__(entityID=entityID, entityType=condType)
        self._state = state

    def getBaseState(self):
        return self._state.base

    def isPositiveState(self):
        return self._state.positive

    def isNegativeState(self):
        return self._state.negative


class _ActiveCondition(_Condition):

    def __init__(self, entityID, condType, state = CONDITION_STATE.ACTIVE):
        raise state.base == CONDITION_STATE.ACTIVE or AssertionError('Base state must be ACTIVE')
        super(_ActiveCondition, self).__init__(entityID, condType, state)


class _CompareCondition(_Condition):

    def __init__(self, entityID, condType, compareID, state = CONDITION_STATE.EQUALS):
        raise state.base == CONDITION_STATE.EQUALS or AssertionError('Base state must be EQUALS')
        super(_CompareCondition, self).__init__(entityID, condType, state)
        self._compareID = compareID

    def getCompareID(self):
        return self._compareID


class FlagCondition(_ActiveCondition):

    def __init__(self, entityID, state = CONDITION_STATE.ACTIVE):
        super(FlagCondition, self).__init__(entityID, CONDITION_TYPE.FLAG, state)


class GlobalFlagCondition(_ActiveCondition):

    def __init__(self, entityID, state = CONDITION_STATE.ACTIVE):
        super(GlobalFlagCondition, self).__init__(entityID, CONDITION_TYPE.GLOBAL_FLAG, state)


class WindowOnSceneCondition(_ActiveCondition):

    def __init__(self, entityID, state = CONDITION_STATE.ACTIVE):
        super(WindowOnSceneCondition, self).__init__(entityID, CONDITION_TYPE.WINDOW_ON_SCENE, state)


class VarDefinedCondition(_ActiveCondition):

    def __init__(self, entityID, state = CONDITION_STATE.ACTIVE):
        super(VarDefinedCondition, self).__init__(entityID, CONDITION_TYPE.VAR_DEFINED, state)


class VarCompareCondition(_CompareCondition):

    def __init__(self, entityID, compareID, state = CONDITION_STATE.EQUALS):
        super(VarCompareCondition, self).__init__(entityID, CONDITION_TYPE.VAR_COMPARE, compareID, state=state)


class EffectTriggeredCondition(_ActiveCondition):

    def __init__(self, entityID, state = CONDITION_STATE.EQUALS):
        super(EffectTriggeredCondition, self).__init__(entityID, CONDITION_TYPE.EFFECT_TRIGGERED, state=state)


class GameItemSimpleStateCondition(_Condition):

    def __init__(self, entityID, state):
        raise state.base in CONDITION_STATE.GAME_ITEM_SIMPLE_STATE or AssertionError
        super(GameItemSimpleStateCondition, self).__init__(entityID, CONDITION_TYPE.GAME_ITEM_SIMPLE_STATE, state)


class GameItemRelateStateCondition(_Condition):

    def __init__(self, entityID, otherID, state):
        raise state.base in CONDITION_STATE.GAME_ITEM_RELATE_STATE or AssertionError
        super(GameItemRelateStateCondition, self).__init__(entityID, CONDITION_TYPE.GAME_ITEM_RELATE_STATE, state)
        self.otherID = otherID

    def getOtherID(self):
        return self.otherID


class BonusReceivedCondition(_ActiveCondition):

    def __init__(self, entityID, state = CONDITION_STATE.ACTIVE):
        super(BonusReceivedCondition, self).__init__(entityID, CONDITION_TYPE.BONUS_RECEIVED, state)


class Conditions(list):

    def __init__(self, *args):
        list.__init__(self, *args)
        self._eitherBlocks = []

    def __repr__(self):
        return 'Conditions({0:s}): {1!r:s}, {2!r:s}'.format(hex(id(self)), self[:], self._eitherBlocks)

    def appendEitherBlock(self, block):
        self._eitherBlocks.append(block)

    def eitherBlocks(self):
        return self._eitherBlocks[:]

    def clear(self):
        while len(self._eitherBlocks):
            self._eitherBlocks.pop()

        while len(self):
            self.pop()
