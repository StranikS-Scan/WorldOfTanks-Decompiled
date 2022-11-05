# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/prb_utils.py
import logging
from constants_utils import attrValidate
from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import BATTLES_SELECTOR_ITEMS
from soft_exception import SoftException
from gui.impl.lobby.mode_selector.items.items_constants import COLUMN_SETTINGS
from gui.prb_control.prb_getters import _ARENA_GUI_TYPE_BY_PRB_TYPE, _ARENA_GUI_TYPE_BY_QUEUE_TYPE
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, _FUNCTIONAL_FLAG_NAMES, SELECTOR_BATTLE_TYPES, REQUEST_TYPE, REQUEST_TYPE_NAMES
from gui.shared.system_factory import registerQueueEntity
from gui.shared.system_factory import registerEntryPoint
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

def addArenaGUITypeByPrbType(prbType, arenaGuiType, personality):
    if prbType in _ARENA_GUI_TYPE_BY_PRB_TYPE:
        raise SoftException('_ARENA_GUI_TYPE_BY_PRB_TYPE already has PREBATTLE_TYPE:{prbType}. Personality: {personality}'.format(prbType=prbType, personality=personality))
    _ARENA_GUI_TYPE_BY_PRB_TYPE.update({prbType: arenaGuiType})
    msg = 'PREBATTLE_TYPE:{prbType}->{guiType} was added to _ARENA_GUI_TYPE_BY_PRB_TYPE. Personality: {p}'.format(prbType=prbType, guiType=arenaGuiType, p=personality)
    logging.debug(msg)


def addArenaGUITypeByQueueType(queueType, arenaGuiType, personality):
    if queueType in _ARENA_GUI_TYPE_BY_QUEUE_TYPE:
        raise SoftException('_ARENA_GUI_TYPE_BY_QUEUE_TYPE already has QUEUE_TYPE:{queueType}. Personality: {personality}'.format(queueType=queueType, personality=personality))
    _ARENA_GUI_TYPE_BY_QUEUE_TYPE.update({queueType: arenaGuiType})
    msg = 'QUEUE_TYPE:{queueType}->{arenaGuiType} was added to _ARENA_GUI_TYPE_BY_QUEUE_TYPE. Personality: {p}'.format(queueType=queueType, arenaGuiType=arenaGuiType, p=personality)
    logging.debug(msg)


def addPrebattleActionName(attrName, value, personality):
    attrValidate(PREBATTLE_ACTION_NAME, attrName, int, value, personality)
    setattr(PREBATTLE_ACTION_NAME, attrName, value)
    msg = 'Attr: {attr}={value} was added to class: {clazz}. Personality: {personality}'.format(attr=attrName, clazz=PREBATTLE_ACTION_NAME, value=value, personality=personality)
    logging.debug(msg)


def addPrebattleRequestType(attrName, value, personality):
    attrValidate(REQUEST_TYPE, attrName, int, value, personality)
    setattr(REQUEST_TYPE, attrName, value)
    REQUEST_TYPE_NAMES.update({value: attrName})
    msg = 'Attr: {attr}={value} was added to class: {clazz}. Personality: {personality}'.format(attr=attrName, clazz=REQUEST_TYPE, value=value, personality=personality)
    logging.debug(msg)


def addFunctionalFlags(attrName, value, personality):
    attrValidate(FUNCTIONAL_FLAG, attrName, int, value, personality)
    setattr(FUNCTIONAL_FLAG, attrName, value)
    FUNCTIONAL_FLAG.MODES_BITMASK |= value
    FUNCTIONAL_FLAG.RANGE += (value,)
    _FUNCTIONAL_FLAG_NAMES.update({attrName: value})
    msg = 'Attr: {attr}={value} was added to class: {clazz}. Personality: {personality}'.format(attr=attrName, clazz=FUNCTIONAL_FLAG, value=value, personality=personality)
    logging.debug(msg)


def addSupportedQueues(queueType, prbEntity, personality):
    registerQueueEntity(queueType, prbEntity)
    msg = 'QUEUE_TYPE:{queueType} was registered. Personality: {personality}'.format(queueType=queueType, personality=personality)
    logging.debug(msg)


def addSupportedEntryByAction(prbActionName, prbEntity, personality):
    registerEntryPoint(prbActionName, prbEntity)
    msg = 'prbActionName:{prb} was registered. Personality: {p}'.format(prb=prbActionName, p=personality)
    logging.debug(msg)


def addBattleItemToColumnSelector(prbActionName, columSelector, personality):
    if prbActionName in COLUMN_SETTINGS:
        raise SoftException('COLUMN_SETTINGS already has prbActionName:{prbActionName}. Personality: {p}'.format(prbActionName=prbActionName, p=personality))
    COLUMN_SETTINGS.update({prbActionName: columSelector})
    msg = 'prbActionName:{prbActionName} was added to COLUMN_SETTINGS. Personality: {p}'.format(prbActionName=prbActionName, p=personality)
    logging.debug(msg)


def addBattleSelectorItem(prbActionName, prbActionConstructor, personality):
    if prbActionConstructor in BATTLES_SELECTOR_ITEMS:
        raise SoftException('BATTLES_SELECTOR_ITEMS already has prbActionName:{prbActionName}. Personality: {p}'.format(prbActionName=prbActionName, p=personality))
    BATTLES_SELECTOR_ITEMS.update({prbActionName: prbActionConstructor})
    msg = 'prbActionName:{prbActionName} was added to BATTLES_SELECTOR_ITEMS. Personality: {p}'.format(prbActionName=prbActionName, p=personality)
    logging.debug(msg)


def addSelectorBattleType(attrName, value, personality):
    attrValidate(SELECTOR_BATTLE_TYPES, attrName, int, value, personality)
    setattr(SELECTOR_BATTLE_TYPES, attrName, value)
    msg = 'Attr: {attr}={value} was added to class: {clazz}. Personality: {personality}'.format(attr=attrName, clazz=SELECTOR_BATTLE_TYPES, value=value, personality=personality)
    logging.debug(msg)


def initPrbGetter(attrName, arenaGUITypeValue, prebattleTypeValue, prebattleActionName, queueTypeValue, functionalFlag, personality):
    addArenaGUITypeByPrbType(prebattleTypeValue, arenaGUITypeValue, personality)
    addArenaGUITypeByQueueType(queueTypeValue, arenaGUITypeValue, personality)
    addPrebattleActionName(attrName, prebattleActionName, personality)
    addFunctionalFlags(attrName, functionalFlag, personality)


def initPrebbatleSelector(attrName, queueTypeValue, selectorBattleTypeValue, prebattleActionName, modeSelectorColumns, battleEntity, battleEntityPoint, addBattleSelectorItemFun, personality):
    addSelectorBattleType(attrName, selectorBattleTypeValue, personality)
    addBattleItemToColumnSelector(prebattleActionName, modeSelectorColumns, personality)
    addBattleSelectorItem(prebattleActionName, addBattleSelectorItemFun, personality)
    addSupportedQueues(queueTypeValue, battleEntity, personality)
    addSupportedEntryByAction(prebattleActionName, battleEntityPoint, personality)
