# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_modifiers/scripts/common/battle_modifiers_ext/remapping/remapping_readers.py
from typing import List, Dict, FrozenSet, TYPE_CHECKING
from battle_modifiers_ext.constants_ext import RemappingConditionNames, ModifiersWithRemapping
from remapping_composers import getComposerClass
from remapping_conditions import getConditionClass
from ResMgr import DataSection
from soft_exception import SoftException
if TYPE_CHECKING:
    from remapping_conditions import IRemappingCondition
    from remapping_composers import IComposer
ERR_TEMPLATE = "[Remapping] {} for remapping '{}'"

def readComposers(config, remappingName, availableConditions):
    composers = {}
    for composerName, section in config.items():
        if composerName not in ModifiersWithRemapping.ALL:
            raise SoftException(ERR_TEMPLATE.format("Invalid composer name '{}'".format(composerName), remappingName))
        composerClass = getComposerClass(remappingName, composerName)
        if composerClass is None:
            raise SoftException(ERR_TEMPLATE.format("Invalid composer class for composer '{}'".format(composerName), remappingName))
        conditions, template = {}, ''
        if section.has_key('conditions'):
            conditions = _readComposerConditions(section, remappingName, composerName, availableConditions)
            template = _readComposerTemplate(section, remappingName, composerName)
        specialRules = {}
        if section.has_key('specialRules'):
            specialRules = _readRemappingRules(section, remappingName, composerName, 'specialRules')
        if not conditions and not specialRules:
            raise SoftException(ERR_TEMPLATE.format("Missing conditions and special rules for '{}' composer ".format(composerName), remappingName))
        composers[composerName] = composerClass(conditions, template, specialRules)

    return composers


def readConditions(config, remappingName):
    conditions = {}
    for conditionSection in config.values():
        if not conditionSection.has_key('conditionName'):
            raise SoftException(ERR_TEMPLATE.format('Missing condition name section', remappingName))
        conditionName = conditionSection['conditionName'].asString
        if conditionName not in RemappingConditionNames.ALL:
            raise SoftException(ERR_TEMPLATE.format("Invalid condition name '{}'".format(conditionName)), remappingName)
        conditionClass = getConditionClass(conditionName)
        if conditionClass is None:
            raise SoftException(ERR_TEMPLATE.format("Unsupported condition class for '{}'".format(conditionName)), remappingName)
        regularRules = {}
        if conditionSection.has_key('remappings'):
            regularRules = _readRemappingRules(conditionSection, remappingName, conditionName, 'remappings')
        conditions[conditionName] = conditionClass(remappingName, regularRules)

    return conditions


def _readComposerConditions(config, remappingName, composerName, availableConditions):
    conditions = []
    conditionNames = config['conditions'].asString.split()
    for conditionName in conditionNames:
        if conditionName not in availableConditions:
            raise SoftException(ERR_TEMPLATE.format("Invalid condition '{}' for composer '{}'".format(conditionName, composerName), remappingName))
        conditions.append(availableConditions[conditionName])

    return conditions


def _readComposerTemplate(config, remappingName, composerName):
    template = config['targetTemplate'].asString
    if not template:
        raise SoftException(ERR_TEMPLATE.format("Empty target template section for '{}' composer ".format(composerName), remappingName))
    return template


def _readRemappingRules(config, remappingName, conditionName, sectionName):
    remappings = {}
    for section in config[sectionName].values():
        source = _readRemappingSource(section, remappingName, conditionName)
        target = _readRemappingTarget(section, remappingName, conditionName)
        remappings[frozenset(source)] = target

    return remappings


def _readRemappingSource(config, remappingName, conditionName):
    if not config.has_key('source'):
        raise SoftException(ERR_TEMPLATE.format("Missing source section for '{}' condition ".format(conditionName), remappingName))
    source = config['source'].asString.split()
    if not source:
        raise SoftException(ERR_TEMPLATE.format("Empty source section for '{}' condition ".format(conditionName), remappingName))
    return source


def _readRemappingTarget(config, remappingName, conditionName):
    if not config.has_key('target'):
        raise SoftException(ERR_TEMPLATE.format("Missing target section for '{}' condition ".format(conditionName), remappingName))
    target = config['target'].asString
    if not target:
        raise SoftException(ERR_TEMPLATE.format("Empty target section for '{}' condition ".format(conditionName), remappingName))
    return target
