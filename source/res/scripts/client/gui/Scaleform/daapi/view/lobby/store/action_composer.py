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
        """
        returns result of composition. Result is list, because theoretically collection can be composed in couple of
        actions. But mostly in this list will be one action. By default we just return first action. It works fine if
        actions appear on UI looking completely the same, so we can't distinguish between them.
        """
        return [first(self._actions)]


class SimpleMixCollection(ComposedActionsCollection):
    _localizationKey = ''
    _groupMarkers = ('gold', 'credits')

    def compose(self):
        """
        Logic of composition is boiled down to following:
         - find better action in each group (currently it's different currencies) and show them;
         - if better actions has same amount of discount and finish date - join them and show as one;
         - if we have action with worse discount, but later date - don't show it now, it'll be displayed when
           current action finishes;
        """
        actionsGroups = self._separateActions()
        if len(self._actions) == 1 or len(actionsGroups) == 1:
            return [self._findBetter(self._actions)]
        else:
            return self._composeActions(map(self._findBetter, actionsGroups.values()))

    def _composeActions(self, actions, compositionKey='mixed'):
        result = []
        for action in actions:
            addedToExisting = False
            for resultAction in result:
                if self._canCompose(resultAction, action):
                    resultAction.setComposition(self._buildCompositionName(compositionKey))
                    addedToExisting = True
                    break

            if not addedToExisting:
                result.append(action)

        return result

    def _canCompose(self, action1, action2):
        return action1.getFinishTime() == action2.getFinishTime() and not self._cmpActions(action1, action2)

    def _separateActions(self):
        """
        separates collection actions in groups by specified markers.
        WARNING: amount of groups is not always the same as number of markers, as some groups can be not presented
        in current collection, e.z. only credits action are running now
        """
        result = {}
        for action in self._actions:
            paramName = action.discount.getParamName()
            for marker in self._groupMarkers:
                if paramName.find(marker) >= 0:
                    result.setdefault(marker, []).append(action)
                    continue

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


class CustomizationActionsCollection(SimpleMixCollection):
    _groupMarkers = ('Inf', '7', '30')

    def compose(self):
        """
        works the same way as parent's, but in two iterations - first we try to compose 7 days and 30 days packets
        in one - credits. Then we try to compose it same way as described in parent method
        """
        actionsGroups = self._separateActions()
        if len(self._actions) == 1 or len(actionsGroups) == 1:
            return [first(self._actions)]
        else:
            betterFromGroups = {k:self._findBetter(v) for k, v in actionsGroups.iteritems()}
            actionsToCompose = []
            if '7' in betterFromGroups and '30' in betterFromGroups:
                actionsToCompose = self._composeActions((betterFromGroups['7'], betterFromGroups['30']), 'credits')
            if 'Inf' in betterFromGroups:
                actionsToCompose.append(betterFromGroups['Inf'])
            return self._composeActions(actionsToCompose)


class CamouflageActionsCollection(CustomizationActionsCollection):
    _localizationKey = 'camouflage'


class InscriptionActionsCollection(CustomizationActionsCollection):
    _localizationKey = 'inscription'


class EmblemActionsCollection(CustomizationActionsCollection):
    _localizationKey = 'emblem'


class TankmenActionsCollection(SimpleMixCollection):
    _localizationKey = 'tankmen'


class DropSkillsActionsCollection(SimpleMixCollection):
    _localizationKey = 'dropSkills'


class ShellActionsCollection(SimpleMixCollection):
    _localizationKey = 'shell'


class EquipmentActionsCollection(SimpleMixCollection):
    _localizationKey = 'equipment'


class CompositionRule(object):
    """
    This class family allows to specify WHICH ActionInfo objects can be compiled together in one display card.
    Property collectionClass specifies HOW ActionInfo should be joined and which display card are eventually built.
    Property _applicableParamsNames specifies ActionInfo for which params should be joined
    """
    _applicableParamsNames = []

    @classmethod
    def applicableTo(cls, action):
        """
        Checks whether current rule can be applied to given ActionInfo objects
        """
        return action.discount.getParamName() in cls._applicableParamsNames

    @classmethod
    def getType(cls):
        return cls.__name__

    @staticmethod
    def canAdd(collection, action):
        return True


class ChangePassportRule(CompositionRule):
    collectionClass = ComposedActionsCollection
    _applicableParamsNames = ('femalePassportChangeCost', 'passportChangeCost')


class CamouflagesRule(CompositionRule):
    collectionClass = CamouflageActionsCollection
    _applicableParamsNames = ('camouflagePacketInfCost', 'camouflagePacket7Cost', 'camouflagePacket30Cost')


class InscriptionsRule(CompositionRule):
    collectionClass = InscriptionActionsCollection
    _applicableParamsNames = ('inscriptionPacketInfCost', 'inscriptionPacket7Cost', 'inscriptionPacket30Cost')


class EmblemsRule(CompositionRule):
    collectionClass = EmblemActionsCollection
    _applicableParamsNames = ('emblemPacketInfCost', 'emblemPacket7Cost', 'emblemPacket30Cost')


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


class ActionComposer(object):
    __compositionRules = (ChangePassportRule,
     CamouflagesRule,
     EmblemsRule,
     InscriptionsRule,
     TankmenRule,
     DropSkillsRule,
     ShellsRule,
     EquipmentRule)

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
