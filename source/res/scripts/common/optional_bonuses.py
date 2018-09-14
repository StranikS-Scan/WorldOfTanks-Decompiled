# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/optional_bonuses.py
import random
from constants import EVENT_TYPE
from items import tankmen

def walkBonuses(bonusWithProbabilities, visitor):
    result = visitor.resultHolder(bonusWithProbabilities)
    for bonusName, bonusValue in bonusWithProbabilities.iteritems():
        if bonusName == 'oneof':
            deeper = visitor.onOneOf(result, bonusValue)
        elif bonusName == 'allof':
            deeper = visitor.onAllOf(result, bonusValue)
        elif bonusName == 'groups':
            deeper = visitor.onGroup(bonusValue)
        else:
            visitor.onValue(result, bonusName, bonusValue)
            continue
        for bonus in deeper:
            for name, value in walkBonuses(bonus, visitor).iteritems():
                visitor.onMerge(result, name, value)

    return result


class ProbabilityVisitor(object):

    def __init__(self, mergers, *args):
        self.__mergers = mergers
        self.__mergersArgs = args

    def onOneOf(self, bonus, value):
        rand = random.random()
        for probability, bonusValue in value:
            if probability > rand:
                return [bonusValue]

        raise Exception('Unreachable code, oneof probability bug %s' % value)

    def onAllOf(self, bonus, value):
        deeper = []
        for probability, bonusValue in value:
            if probability > random.random():
                deeper.append(bonusValue)

        return deeper

    def onGroup(self, value):
        deeper = []
        for bonusValue in value:
            deeper.append(bonusValue)

        return deeper

    def onValue(self, bonus, name, value):
        if name in self.__mergers:
            self.__mergers[name](bonus, name, value, True, *self.__mergersArgs)

    def onMerge(self, bonus, name, value):
        if name in self.__mergers:
            self.__mergers[name](bonus, name, value, False, *self.__mergersArgs)

    @staticmethod
    def resultHolder(result):
        return {}


class FilterVisitor(object):

    def __init__(self, eventType=None):
        self.__eventType = eventType

    def onOneOf(self, bonus, value):
        deeper = []
        for probability, bonusValue in value:
            deeper.append(bonusValue)

        return deeper

    def onAllOf(self, bonus, value):
        deeper = []
        for probability, bonusValue in value:
            deeper.append(bonusValue)

        return deeper

    def onGroup(self, value):
        deeper = []
        for bonusValue in value:
            deeper.append(bonusValue)

        return deeper

    def onValue(self, bonus, name, value):
        if self.__eventType != EVENT_TYPE.POTAPOV_QUEST and name == 'tankmen':
            tankmenList = [ tankmen.makeTmanDescrByTmanData(tmanData) for tmanData in value ]
            bonus['tankmen'] = tankmenList
        if self.__eventType in EVENT_TYPE.LIKE_TOKEN_QUESTS and name == 'customization':
            if 'boundToCurrentVehicle' in value:
                raise Exception("Unsupported tag 'boundToCurrentVehicle' in 'like token' quests")

    def onMerge(self, bonus, name, value):
        pass

    @staticmethod
    def resultHolder(result):
        return result


class StripVisitor(object):

    def onOneOf(self, bonus, value):
        result = []
        deeper = []
        for probability, bonusValue in value:
            result.append((-1, bonusValue))
            deeper.append(bonusValue)

        bonus['oneof'] = result
        return deeper

    def onAllOf(self, bonus, value):
        result = []
        deeper = []
        for probability, bonusValue in value:
            result.append((-1, bonusValue))
            deeper.append(bonusValue)

        bonus['allof'] = result
        return deeper

    def onGroup(self, value):
        deeper = []
        for bonusValue in value:
            deeper.append(bonusValue)

        return deeper

    def onValue(self, bonus, name, value):
        pass

    def onMerge(self, bonus, name, value):
        pass

    @staticmethod
    def resultHolder(result):
        return result
