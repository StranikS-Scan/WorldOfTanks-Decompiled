# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/constants_utils.py
from constants import ARENA_GUI_TYPE, ARENA_GUI_TYPE_LABEL, ARENA_BONUS_TYPE, ARENA_BONUS_TYPE_NAMES, ARENA_BONUS_TYPE_IDS, ARENA_BONUS_MASK, QUEUE_TYPE, QUEUE_TYPE_NAMES, QUEUE_TYPE_IDS, PREBATTLE_TYPE, PREBATTLE_TYPE_NAMES
from debug_utils import LOG_DEBUG
from soft_exception import SoftException

def attrValidate(clazz, attr, attrType, value, personality):
    if hasattr(clazz, attr):
        raise SoftException('Class {clazz} already has attr {attr}. Personality: {personality}'.format(clazz=clazz, attr=attr, personality=personality))
    attrValues = {val for att, val in clazz.__dict__.iteritems() if isinstance(val, attrType)}
    if value in attrValues:
        raise SoftException('Attr: {attr} can not have value: {value} in class {clazz} because it is used. Personality: {personality}'.format(attr=attr, value=value, clazz=clazz, personality=personality))


def checkAttrNameExist(attrName, classList, personality):
    if not hasattr(classList, '__iter__'):
        return [classList]
    for clazz in classList:
        if not hasattr(clazz, attrName):
            raise SoftException('{attrName} doesnt exist in class {clazz}. Personality: {personality}'.format(attrName=attrName, clazz=clazz, personality=personality))


def addArenaGuiTypeFromExtension(attrName, value, personality):
    attrValidate(ARENA_GUI_TYPE, attrName, int, value, personality)
    setattr(ARENA_GUI_TYPE, attrName, value)
    ARENA_GUI_TYPE.RANGE += (value,)
    ARENA_GUI_TYPE_LABEL.LABELS.update({value: attrName.lower()})
    LOG_DEBUG('Attr: {attr}={value} was added to class: {clazz}. Personality: {personality}'.format(attr=attrName, clazz=ARENA_GUI_TYPE, value=value, personality=personality))


def addArenaBonusTypeFromExtension(attrName, value, personality):
    attrValidate(ARENA_BONUS_TYPE, attrName, int, value, personality)
    setattr(ARENA_BONUS_TYPE, attrName, value)
    ARENA_BONUS_TYPE.RANGE += (value,)
    ARENA_BONUS_TYPE_NAMES.update({attrName: value})
    ARENA_BONUS_TYPE_IDS.update({value: attrName})
    ARENA_BONUS_MASK.reInit()
    LOG_DEBUG('Attr: {attr}={value} was added to class: {clazz}. Personality: {personality}'.format(attr=attrName, clazz=ARENA_BONUS_TYPE, value=value, personality=personality))


def addQueueTypeFromExtension(attrName, value, personality):
    attrValidate(QUEUE_TYPE, attrName, int, value, personality)
    setattr(QUEUE_TYPE, attrName, value)
    QUEUE_TYPE.ALL += (value,)
    QUEUE_TYPE_NAMES.update({value: attrName})
    QUEUE_TYPE_IDS.update({attrName.lower(): value})
    LOG_DEBUG('Attr: {attr}={value} was added to class: {clazz}. Personality: {personality}'.format(attr=attrName, clazz=QUEUE_TYPE, value=value, personality=personality))


def addPrebattleTypeFromExtension(attrName, value, personality):
    attrValidate(PREBATTLE_TYPE, attrName, int, value, personality)
    setattr(PREBATTLE_TYPE, attrName, value)
    PREBATTLE_TYPE.RANGE += (value,)
    PREBATTLE_TYPE.SQUAD_PREBATTLES += (value,)
    PREBATTLE_TYPE.UNIT_MGR_PREBATTLES += (value,)
    PREBATTLE_TYPE.CREATE_FROM_CLIENT += (value,)
    PREBATTLE_TYPE.CREATE_EX_FROM_SERVER += (value,)
    PREBATTLE_TYPE.JOIN_EX += (value,)
    PREBATTLE_TYPE_NAMES.update({value: attrName})
    LOG_DEBUG('Attr: {attr}={value} was added to class: {clazz}. Personality: {personality}'.format(attr=attrName, clazz=PREBATTLE_TYPE, value=value, personality=personality))


def initCommonTypes(attrName, arenaGuiTypeValue, arenaBonusTypeValue, queueTypeValue, prebatlyTypeValue, personality):
    addArenaGuiTypeFromExtension(attrName, arenaGuiTypeValue, personality)
    addArenaBonusTypeFromExtension(attrName, arenaBonusTypeValue, personality)
    addQueueTypeFromExtension(attrName, queueTypeValue, personality)
    addPrebattleTypeFromExtension(attrName, prebatlyTypeValue, personality)
