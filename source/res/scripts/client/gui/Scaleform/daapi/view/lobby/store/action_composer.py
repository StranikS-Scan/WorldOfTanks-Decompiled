# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/action_composer.py
from debug_utils import LOG_WARNING
from shared_utils import findFirst, first

class ComposedActionsCollection(object):

    def __init__(self, action):
        self._actions = [action]
        self.finishTime = action.getFinishTime()
        self.value = action.discount.getParamValue()

    def add(self, action):
        self._actions.append(action)

    def compose(self):
        return [first(self._actions)]


class SimpleMixCollection(ComposedActionsCollection):
    _localizationKey = ''
    _groupMarkers = ('gold', 'credits')

    def compose(self):
        actionsGroups = self._separateActions()
        return [self._findBetter(self._actions)] if len(self._actions) == 1 or len(actionsGroups) == 1 else self._composeActions(map(self._findBetter, actionsGroups.values()))

    def _composeActions(self, actions, compositionKey='mixed'):
        result = []
        for action in actions:
            for resultAction in result:
                if self._canCompose(resultAction, action):
                    resultAction.setComposition(self._buildCompositionName(compositionKey))
                    break
            else:
                result.append(action)

        return result

    def _canCompose(self, action1, action2):
        return action1.getFinishTime() == action2.getFinishTime() and not self._cmpActions(action1, action2)

    def _separateActions(self):
        result = {}
        for action in self._actions:
            paramName = action.discount.getParamName()
            for marker in self._groupMarkers:
                if paramName.find(marker) >= 0:
                    result.setdefault(marker, []).append(action)

        if sum(map(len, result.values())) != len(self._actions):
            LOG_WARNING('Incorrect separation of actions, count of elements in groups is not equal to origin count')
        return result

    def _buildCompositionName(self, compositionType):
        return '/'.join([self._localizationKey, compositionType])

    @classmethod
    def _findBetter(cls, actionsGroup):
        return first(sorted(actionsGroup, cmp=cls._cmpActions, reverse=True))

    @staticmethod
    def _cmpActions(action1, action2):
        return action1.getMaxDiscountValue() - action2.getMaxDiscountValue()


class TankmenActionsCollection(SimpleMixCollection):
    _localizationKey = 'tankmen'


class DropSkillsActionsCollection(SimpleMixCollection):
    _localizationKey = 'dropSkills'


class ShellActionsCollection(SimpleMixCollection):
    _localizationKey = 'shell'


class EquipmentActionsCollection(SimpleMixCollection):
    _localizationKey = 'equipment'


class PremiumActionsCollection(SimpleMixCollection):
    _localizationKey = 'premiumPacket'
    _groupMarkers = ('1Cost', '3Cost', '7Cost', '30Cost', '180Cost', '360Cost')

    def compose(self):
        actionsGroups = self._separateActions()
        return [self._findBetter(self._actions)] if len(self._actions) == 1 or len(actionsGroups) == 1 else map(self._findBetter, actionsGroups.values())


class CompositionRule(object):
    _applicableParamsNames = []

    @classmethod
    def applicableTo(cls, action):
        return action.discount.getParamName() in cls._applicableParamsNames

    @classmethod
    def getType(cls):
        return cls.__name__

    @staticmethod
    def canAdd(collection, action):
        return True


class TankmenRule(CompositionRule):
    collectionClass = TankmenActionsCollection
    _applicableParamsNames = ('creditsTankmanCost', 'goldTankmanCost')


class DropSkillsRule(CompositionRule):
    collectionClass = DropSkillsActionsCollection
    _applicableParamsNames = ('creditsDropSkillsCost', 'goldDropSkillsCost')


class ShellsRule(CompositionRule):
    collectionClass = ShellActionsCollection
    _applicableParamsNames = ('shell/creditsPriceMultiplier', 'shell/goldPriceMultiplier')


class EquipmentRule(CompositionRule):
    collectionClass = EquipmentActionsCollection
    _applicableParamsNames = ('equipment/creditsPriceMultiplier', 'equipment/goldPriceMultiplier')


class PremiumRule(CompositionRule):
    collectionClass = PremiumActionsCollection
    _applicableParamsNames = ('premiumPacket1Cost', 'premiumPacket3Cost', 'premiumPacket7Cost', 'premiumPacket14Cost', 'premiumPacket30Cost', 'premiumPacket90Cost', 'premiumPacket180Cost', 'premiumPacket360Cost')


class ActionComposer(object):
    __compositionRules = (TankmenRule,
     DropSkillsRule,
     ShellsRule,
     EquipmentRule,
     PremiumRule)

    def __init__(self):
        self.__collections = {}
        self.__singleActions = []

    def add(self, action):
        applicableRule = findFirst(lambda r: r.applicableTo(action), self.__compositionRules)
        if applicableRule is not None:
            ruleType = applicableRule.getType()
            collections = self.__collections.setdefault(ruleType, [])
            collection = findFirst(lambda c: applicableRule.canAdd(c, action), collections)
            if collection is not None:
                collection.add(action)
            else:
                self.__collections[ruleType].append(applicableRule.collectionClass(action))
        else:
            self.__singleActions.append(action)
        return

    def getActions(self):
        return self.__singleActions + self.__composeCollections()

    def __composeCollections(self):
        result = []
        for collectionsList in self.__collections.values():
            for collection in collectionsList:
                result.extend(collection.compose())

        return result
