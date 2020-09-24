# Python bytecode 2.7 (decompiled from Python 2.7)
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
    SERVICE = 10
    COMPONENT_ON_SCENE = 11
    CURRENT_SCENE = 12
    VIEW_PRESENT = 13
    CONNECTED_ITEM = 14
    CONDITION_AND = 15
    CONDITION_OR = 16
    FIRST_CUSTOM = 100
    BASE_RANGE = (FLAG,
     GLOBAL_FLAG,
     WINDOW_ON_SCENE,
     GAME_ITEM_SIMPLE_STATE,
     GAME_ITEM_RELATE_STATE,
     VAR_DEFINED,
     VAR_COMPARE,
     EFFECT_TRIGGERED,
     BONUS_RECEIVED,
     SERVICE,
     COMPONENT_ON_SCENE,
     CURRENT_SCENE,
     VIEW_PRESENT,
     CONNECTED_ITEM,
     CONDITION_AND,
     CONDITION_OR)


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
    IN_INVENTORY = _StateValue(6)
    XP_ENOUGH = _StateValue(7)
    MONEY_ENOUGH = _StateValue(8)
    LEVEL = _StateValue(9)
    MAY_INSTALL = _StateValue(10)
    INSTALLED = _StateValue(11)
    CREW_HAS_SKILL = _StateValue(12)
    HAS_REGULAR_CONSUMABLES = _StateValue(13)
    HAS_OPTIONAL_DEVICES = _StateValue(14)
    RANGE = (UNDEFINED,
     ACTIVE,
     EQUALS,
     SELECTED,
     PREMIUM,
     UNLOCKED,
     IN_INVENTORY,
     XP_ENOUGH,
     MONEY_ENOUGH,
     LEVEL,
     MAY_INSTALL,
     INSTALLED,
     CREW_HAS_SKILL,
     HAS_REGULAR_CONSUMABLES,
     HAS_OPTIONAL_DEVICES)
    GAME_ITEM_SIMPLE_STATE = (SELECTED,
     PREMIUM,
     UNLOCKED,
     IN_INVENTORY,
     MONEY_ENOUGH,
     HAS_REGULAR_CONSUMABLES,
     HAS_OPTIONAL_DEVICES)
    GAME_ITEM_RELATE_STATE = (XP_ENOUGH,
     LEVEL,
     MAY_INSTALL,
     INSTALLED,
     CREW_HAS_SKILL)


class Condition(HasID):

    def __init__(self, entityID, condType, state):
        super(Condition, self).__init__(entityID=entityID, entityType=condType)
        self._state = state

    def getBaseState(self):
        return self._state.base

    def isPositiveState(self):
        return self._state.positive

    def isNegativeState(self):
        return self._state.negative


class ActiveCondition(Condition):

    def __init__(self, entityID, condType, state=CONDITION_STATE.ACTIVE):
        super(ActiveCondition, self).__init__(entityID, condType, state)


class CompareCondition(Condition):

    def __init__(self, entityID, condType, compareID, state=CONDITION_STATE.EQUALS):
        super(CompareCondition, self).__init__(entityID, condType, state)
        self._compareID = compareID

    def getCompareID(self):
        return self._compareID


class FlagCondition(ActiveCondition):

    def __init__(self, entityID, state=CONDITION_STATE.ACTIVE):
        super(FlagCondition, self).__init__(entityID, CONDITION_TYPE.FLAG, state)


class GlobalFlagCondition(ActiveCondition):

    def __init__(self, entityID, state=CONDITION_STATE.ACTIVE):
        super(GlobalFlagCondition, self).__init__(entityID, CONDITION_TYPE.GLOBAL_FLAG, state)


class WindowOnSceneCondition(ActiveCondition):

    def __init__(self, entityID, state=CONDITION_STATE.ACTIVE):
        super(WindowOnSceneCondition, self).__init__(entityID, CONDITION_TYPE.WINDOW_ON_SCENE, state)


class ComponentOnSceneCondition(ActiveCondition):

    def __init__(self, entityID, state=CONDITION_STATE.ACTIVE):
        super(ComponentOnSceneCondition, self).__init__(entityID, CONDITION_TYPE.COMPONENT_ON_SCENE, state)


class CurrentSceneCondition(ActiveCondition):

    def __init__(self, entityID, state=CONDITION_STATE.ACTIVE):
        super(CurrentSceneCondition, self).__init__(entityID, CONDITION_TYPE.CURRENT_SCENE, state)


class ViewPresentCondition(ActiveCondition):

    def __init__(self, layer, viewAlias, state=CONDITION_STATE.ACTIVE):
        super(ViewPresentCondition, self).__init__(None, CONDITION_TYPE.VIEW_PRESENT, state)
        self.__layer = layer
        self.__viewAlias = viewAlias
        return

    def getLayer(self):
        return self.__layer

    def getViewAlias(self):
        return self.__viewAlias


class VarDefinedCondition(ActiveCondition):

    def __init__(self, entityID, state=CONDITION_STATE.ACTIVE):
        super(VarDefinedCondition, self).__init__(entityID, CONDITION_TYPE.VAR_DEFINED, state)


class VarCompareCondition(CompareCondition):

    def __init__(self, entityID, compareID, state=CONDITION_STATE.EQUALS):
        super(VarCompareCondition, self).__init__(entityID, CONDITION_TYPE.VAR_COMPARE, compareID, state=state)


class EffectTriggeredCondition(ActiveCondition):

    def __init__(self, entityID, state=CONDITION_STATE.EQUALS):
        super(EffectTriggeredCondition, self).__init__(entityID, CONDITION_TYPE.EFFECT_TRIGGERED, state=state)


class GameItemSimpleStateCondition(Condition):

    def __init__(self, entityID, state):
        super(GameItemSimpleStateCondition, self).__init__(entityID, CONDITION_TYPE.GAME_ITEM_SIMPLE_STATE, state)


class GameItemRelateStateCondition(Condition):

    def __init__(self, entityID, otherIDs, state):
        super(GameItemRelateStateCondition, self).__init__(entityID, CONDITION_TYPE.GAME_ITEM_RELATE_STATE, state)
        self.__otherIDs = otherIDs

    def getOtherIDs(self):
        return self.__otherIDs


class BonusReceivedCondition(ActiveCondition):

    def __init__(self, entityID, state=CONDITION_STATE.ACTIVE):
        super(BonusReceivedCondition, self).__init__(entityID, CONDITION_TYPE.BONUS_RECEIVED, state)


class ServiceCondition(ActiveCondition):

    def __init__(self, entityID, serviceClass, state=CONDITION_STATE.ACTIVE):
        super(ServiceCondition, self).__init__(entityID, CONDITION_TYPE.SERVICE, state)
        self.__serviceClass = serviceClass

    def getServiceClass(self):
        return self.__serviceClass


class ConnectedItemCondition(Condition):

    def __init__(self, entityID, isShown, state=CONDITION_STATE.ACTIVE):
        super(ConnectedItemCondition, self).__init__(entityID, CONDITION_TYPE.CONNECTED_ITEM, state)
        self.__isShown = isShown

    def isShown(self):
        return self.__isShown


class _ComplexCondition(Condition):

    def __init__(self, items, conditionType):
        super(_ComplexCondition, self).__init__(None, conditionType, state=CONDITION_STATE.ACTIVE)
        self.__conditionList = items if items else []
        return

    def getConditionList(self):
        return self.__conditionList


class ComplexConditionAnd(_ComplexCondition):

    def __init__(self, items):
        super(ComplexConditionAnd, self).__init__(items, CONDITION_TYPE.CONDITION_AND)


class ComplexConditionOr(_ComplexCondition):

    def __init__(self, items):
        super(ComplexConditionOr, self).__init__(items, CONDITION_TYPE.CONDITION_OR)


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
        while self._eitherBlocks:
            self._eitherBlocks.pop()

        while self:
            self.pop()
