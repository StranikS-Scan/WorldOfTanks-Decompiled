# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/VehicleQualifiersApplier.py
import BigWorld
from constants import IS_QUALIFIERS_ENABLED
from debug_utils import LOG_ERROR
from items import vehicles
from items import qualifiers as Qualifiers
from items.qualifiers import QUALIFIER_TYPE, QUALIFIER_TYPE_NAMES

class _QualifiersChainApplier(object):

    def __init__(self, conditions, qualifiers):
        self.__qualifiers = qualifiers
        self.__conditions = conditions
        self.__lastCheckCondition = {}

    def __call__(self, value):
        qualifiers = self.__qualifiers
        if not qualifiers:
            return value
        else:
            conditions = self.__conditions
            conditionsKeys = frozenset(conditions.iterkeys())
            lastCheckCondition = self.__lastCheckCondition
            for qualifier in qualifiers:
                if not qualifier.conditionParams <= conditionsKeys:
                    continue
                conditionFunc = qualifier.conditionFunc
                canApply = True
                if conditionFunc is not None:
                    lastCheckCondition[qualifier.id] = canApply = conditionFunc(conditions)
                if canApply:
                    value = qualifier(value, **conditions)

            return value

    def testConditionsChange(self):
        lastCheckCondition = self.__lastCheckCondition
        conditions = self.__conditions
        conditionsKeys = frozenset(conditions.iterkeys())
        for qualifier in self.__qualifiers:
            if not qualifier.conditionParams <= conditionsKeys:
                continue
            conditionFunc = qualifier.conditionFunc
            if conditionFunc is None:
                continue
            if lastCheckCondition.get(qualifier.id) != conditionFunc(conditions):
                return True

        return False


_EMPTY_CHAIN_APPLIER = _QualifiersChainApplier({}, {})

class _SubApplier(object):

    def __init__(self, conditions, qualifierType, qualifiersByType):
        qualifiersBySubType = {}
        requiredParams = set()
        for qualifier in qualifiersByType:
            if qualifierType == QUALIFIER_TYPE.MAIN_SKILL:
                subType = qualifier.crewRole
            else:
                raise 'SubApplier %s not implemented' % QUALIFIER_TYPE_NAMES[qualifierType]
            qualifiersBySubType.setdefault(subType, []).append(qualifier)
            requiredParams.update(qualifier.conditionParams)

        self.__requiredParams = frozenset(requiredParams)
        self.__qualifiersSubApplier = qualifiersSubApplier = {}
        for qualifierSubType, qualifiers in qualifiersBySubType.iteritems():
            qualifiersSubApplier[qualifierSubType] = _QualifiersChainApplier(conditions, qualifiers)

    def isUpdateNecessary(self):
        for chainApplier in self.__qualifiersSubApplier.itervalues():
            if chainApplier.testConditionsChange():
                return True

        return False

    def __getitem__(self, subType):
        return self.__qualifiersSubApplier.setdefault(subType, _EMPTY_CHAIN_APPLIER)


class VehicleQualifiersApplier(object):

    def __init__(self, conditions, vehDescr, arenaCamouflageKind = None):
        self.__requiredParams = requiredParams = set()
        self.__qualifiersApplier = qualifiersApplier = {}
        if not IS_QUALIFIERS_ENABLED:
            return
        qualifiersByType = {}
        activatedQualifierIDs = self.__activatedQualifierIDs(vehDescr, arenaCamouflageKind)
        for qualifierID in activatedQualifierIDs:
            qualifier = Qualifiers.g_cache[qualifierID]
            if qualifier:
                qualifiersByType.setdefault(qualifier.qualifierType, []).append(qualifier)
                cndParams = qualifier.conditionParams
                if cndParams:
                    requiredParams.update(cndParams)

        for qualifierType, qualifiers in qualifiersByType.iteritems():
            qualifiersApplier[qualifierType] = self.__createApplier(qualifierType, qualifiers, conditions)

    requiredParams = property(lambda self: self.__requiredParams)

    def __activatedQualifierIDs(self, vehDescr, arenaCamouflageKind):
        v_cache = vehicles.g_cache
        g_customization = v_cache.customization
        activatedQualifierIDs = []
        selectors = (('playerInscriptions', range(0, 4)), ('playerEmblems', range(0, 4)))
        for propName, positions in selectors:
            propValue = getattr(vehDescr, propName, None)
            if not propValue:
                continue
            for pos in positions:
                if pos is None:
                    continue
                itemID = propValue[pos][0]
                if itemID is None:
                    continue
                nationID = vehDescr.type.customizationNationID
                customization = None
                if propName == 'playerInscriptions':
                    customization = g_customization(nationID)['inscriptions']
                elif propName == 'playerEmblems':
                    customization = v_cache.playerEmblems()[1]
                qualifierID = customization[itemID][-1]
                if qualifierID is not None:
                    activatedQualifierIDs.append(qualifierID)

        return activatedQualifierIDs

    def __createApplier(self, qualifierType, qualifiers = {}, conditions = {}):
        if qualifierType == QUALIFIER_TYPE.MAIN_SKILL:
            return _SubApplier(conditions, qualifierType, qualifiers)
        elif not qualifiers:
            return _EMPTY_CHAIN_APPLIER
        else:
            return _QualifiersChainApplier(conditions, qualifiers)

    def __getitem__(self, qualifierType):
        return self.__qualifiersApplier.setdefault(qualifierType, self.__createApplier(qualifierType))
