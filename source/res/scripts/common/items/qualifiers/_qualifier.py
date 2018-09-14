# Embedded file name: scripts/common/items/qualifiers/_qualifier.py
from _xml import *

class QUALIFIER_TYPE:
    MAIN_SKILL = 'main_skill'
    CREW_EXPERIENCE = 'crew_experience'
    PLAYER_EXPERIENCE = 'player_experience'
    CREDITS = 'credits'


QUALIFIER_TYPE_NAMES = {v:k for k, v in QUALIFIER_TYPE.__dict__.iteritems()}

class CREW_ROLE:
    ALL = 'all'
    COMMANDER = 'commander'
    RADIOMAN = 'radioman'
    DRIVER = 'driver'
    GUNNER = 'gunner'
    LOADER = 'loader'
    RANGE = {ALL,
     COMMANDER,
     RADIOMAN,
     DRIVER,
     GUNNER,
     LOADER}


def parseCrewRoleName(section):
    if section is None:
        return CREW_ROLE.ALL
    else:
        name = section.asString.lower()
        if name not in CREW_ROLE.RANGE:
            raise Exception('Wrong crew role name {0}'.format(name))
        return name


def _parseMainSkill(section):
    conditionFunc, conditionParams = parseCondition(section)
    description = section['conditionDescription']
    if conditionFunc is not None and description is None:
        raise Exception('conditionDescription is required tag if condition is specified')
    isPercent, value = parseValue(section)
    return MainSkillQualifier(section['id'].asString, value, isPercent, conditionFunc, conditionParams, parseCrewRoleName(section['crewRole']), '' if description is None else description.asString)


_PARSERS = {QUALIFIER_TYPE.MAIN_SKILL: _parseMainSkill}

def parseQualifier(section):
    qualifierType = section['type'].asString
    if qualifierType not in _PARSERS:
        raise Exception, 'Qualifier "{0}" is not supported.'.format(qualifierType)
    res = _PARSERS[qualifierType](section)
    if not res or not all((res.id, res.qualifierType)) or res.value is None:
        raise Exception, 'Bonus attributes (id, type, value) are required.'
    return res


def _getQualifierFunc(isPercent, value):
    if isPercent:
        return lambda baseValue: baseValue + value * baseValue / 100
    else:
        return lambda baseValue: baseValue + value


class Qualifier(object):
    __slots__ = ('id', 'qualifierType', 'isPercent', 'value', 'conditionFunc', 'conditionParams', '__qualifierFunc')

    def __init__(self, id, qualifierType, qualifierValue, isPercent, conditionFunc, conditionParams):
        self.id = id
        self.qualifierType = qualifierType
        self.isPercent = isPercent
        self.value = qualifierValue
        self.__qualifierFunc = _getQualifierFunc(isPercent, qualifierValue)
        self.conditionFunc = conditionFunc
        self.conditionParams = frozenset(conditionParams or tuple())

    def __repr__(self):
        return 'Qualifier {0} with id={1}'.format(self.qualifierType, self.id)

    def __call__(self, initialValue, **kwargs):
        if self.conditionFunc is None or self.conditionFunc(kwargs):
            return self.__qualifierFunc(initialValue)
        else:
            return initialValue


class MainSkillQualifier(Qualifier):
    __slots__ = ('crewRole', 'conditionDescription')

    def __init__(self, id, qualifierValue, isPercent, conditionFunc, conditionParams, crewRole, conditionDescription):
        super(MainSkillQualifier, self).__init__(id, QUALIFIER_TYPE.MAIN_SKILL, qualifierValue, isPercent, conditionFunc, conditionParams)
        self.crewRole = crewRole
        self.conditionDescription = conditionDescription

    def __repr__(self):
        return 'Main skill qualifier id="{0}" for crewRole="{1}" '.format(self.id, self.crewRole)
