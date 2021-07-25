# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/__init__.py
import importlib
from collections import namedtuple
from functools import partial
import nations
import resource_helper
from gui.Scaleform.genConsts.LAYER_NAMES import LAYER_NAMES
from items import _xml, vehicles
from helpers.html import translation
from tutorial.data import chapter as tutorial_chapter
from tutorial.data import effects
from tutorial.data import conditions as tut_conditions
from tutorial.data.events import GuiEventType
from tutorial.control.context import SOUND_EVENT
from tutorial.logger import LOG_ERROR
_EFFECT_TYPE = effects.EFFECT_TYPE
_COND_STATE = tut_conditions.CONDITION_STATE
_CheckedComponentState = namedtuple('CheckedComponentState', ('state', 'value'))

def parseID(xmlCtx, section, msg):
    entityID = section.asString
    if not entityID:
        _xml.raiseWrongXml(xmlCtx, section.name, msg)
    return entityID


def _parseOneState(xml, section):
    checkedState = parseID(xml, section['state'], 'Specify ui state')
    neededValue = _xml.readBool(xml, section, 'value')
    return _CheckedComponentState(checkedState, neededValue)


def _parseNeededState(xmlCtx, section):
    stateSection = section['checked-ui-state']
    if not stateSection:
        return None
    else:
        result = []
        for name, subSection in stateSection.items():
            if name == 'simple-state':
                result.append(_parseOneState(xmlCtx, subSection))
            _xml.raiseWrongXml(xmlCtx, section, 'Tag %s are not found' % name)

        return result if result else None


def _readFlagCondition(xmlCtx, section, state, flags):
    flagID = parseID(xmlCtx, section, 'Specify a flag ID')
    if flagID not in flags:
        flags.append(flagID)
    return tut_conditions.FlagCondition(flagID, state=state)


def _readGlobalFlagCondition(xmlCtx, section, state):
    flagID = parseID(xmlCtx, section, 'Specify a flag ID')
    return tut_conditions.GlobalFlagCondition(flagID, state=state)


def _readWindowOnSceneCondition(xmlCtx, section, state):
    windowID = parseID(xmlCtx, section, 'Specify a window ID')
    return tut_conditions.WindowOnSceneCondition(windowID, state=state)


def _readComponentOnSceneCondition(xmlCtx, section, state):
    componentID = parseID(xmlCtx, section, 'Specify a component ID')
    return tut_conditions.ComponentOnSceneCondition(componentID, state=state)


def _readCurrentSceneCondition(xmlCtx, section, state):
    sceneID = parseID(xmlCtx, section, 'Specify a scene ID')
    return tut_conditions.CurrentSceneCondition(sceneID, state=state)


def _readViewPresentCondition(xmlCtx, section, state):
    layer = LAYER_NAMES.LAYER_ORDER.index(_xml.readString(xmlCtx, section, 'type'))
    viewAlias = _xml.readString(xmlCtx, section, 'alias')
    return tut_conditions.ViewPresentCondition(layer, viewAlias, state=state)


_GAME_ITEM_CONDITION_TAGS = {'selected': _COND_STATE.SELECTED,
 'not-selected': ~_COND_STATE.SELECTED,
 'premium': _COND_STATE.PREMIUM,
 'not-premium': ~_COND_STATE.PREMIUM,
 'unlocked': _COND_STATE.UNLOCKED,
 'not-unlocked': ~_COND_STATE.UNLOCKED,
 'in-inventory': _COND_STATE.IN_INVENTORY,
 'not-in-inventory': ~_COND_STATE.IN_INVENTORY,
 'crew-has-skill': _COND_STATE.CREW_HAS_SKILL,
 'crew-has-no-skill': ~_COND_STATE.CREW_HAS_SKILL,
 'xp-enough': _COND_STATE.XP_ENOUGH,
 'xp-not-enough': ~_COND_STATE.XP_ENOUGH,
 'money-enough': _COND_STATE.MONEY_ENOUGH,
 'money-not-enough': ~_COND_STATE.MONEY_ENOUGH,
 'level': _COND_STATE.LEVEL,
 'not-level': ~_COND_STATE.LEVEL,
 'may-install': _COND_STATE.MAY_INSTALL,
 'may-not-install': ~_COND_STATE.MAY_INSTALL,
 'installed': _COND_STATE.INSTALLED,
 'not-installed': ~_COND_STATE.INSTALLED,
 'has-regular-consumables': _COND_STATE.HAS_REGULAR_CONSUMABLES,
 'has-no-regular-consumables': ~_COND_STATE.HAS_REGULAR_CONSUMABLES,
 'has-optional-devices': _COND_STATE.HAS_OPTIONAL_DEVICES,
 'has-no-optional-devices': ~_COND_STATE.HAS_OPTIONAL_DEVICES}
_GAME_ITEM_CONDITION_SET = set(_GAME_ITEM_CONDITION_TAGS.keys())

def _readGameItemCondition(xmlCtx, section, _):
    varID = parseID(xmlCtx, section, 'Specify a var ID')
    tags = set(section.keys()) & _GAME_ITEM_CONDITION_SET
    if tags:
        if len(tags) > 1:
            _xml.raiseWrongXml(xmlCtx, 'var', 'One state of vehicle condition must be defined, found {0}'.format(tags))
            return None
        tag = tags.pop()
        state = _GAME_ITEM_CONDITION_TAGS[tag]
        if state.base in _COND_STATE.GAME_ITEM_RELATE_STATE:
            otherIDs = parseID(xmlCtx, section[tag], 'Specify a other ID').split()
            return tut_conditions.GameItemRelateStateCondition(varID, otherIDs, state)
        return tut_conditions.GameItemSimpleStateCondition(varID, state)
    else:
        _xml.raiseWrongXml(xmlCtx, 'var', 'State of vehicle condition is not found: {0}'.format(section.keys()))
        return None


def _readVarCondition(xmlCtx, section, _):
    varID = parseID(xmlCtx, section, 'Specify a var ID')
    tags = section.keys()
    if 'is-none' in tags:
        return tut_conditions.VarDefinedCondition(varID, ~_COND_STATE.ACTIVE)
    elif 'is-not-none' in tags:
        return tut_conditions.VarDefinedCondition(varID, _COND_STATE.ACTIVE)
    elif 'equals' in tags:
        return tut_conditions.VarCompareCondition(varID, _xml.readString(xmlCtx, section, 'equals'), _COND_STATE.EQUALS)
    elif 'not-equals' in tags:
        return tut_conditions.VarCompareCondition(varID, _xml.readString(xmlCtx, section, 'not-equals'), ~_COND_STATE.EQUALS)
    else:
        _xml.raiseWrongXml(xmlCtx, 'var', 'State of var condition is not found')
        return None


def _readConnectedItemCondition(xmlCtx, section, _=None):
    hintID = parseID(xmlCtx, section['hint-id'], 'Specify a hint ID')
    status = _xml.readBool(xmlCtx, section, 'value')
    return tut_conditions.ConnectedItemCondition(hintID, status)


def _readComplexCondition(xmlCtx, section, flags):
    items = []
    for name, subSection in section.items():
        function = _conditions.tags.get(name)
        if function is None:
            LOG_ERROR('Condition is not supported: ', name)
            continue
        items.append(function(xmlCtx, subSection, flags))

    return items


def _readComplexConditionAnd(xmlCtx, section, flags):
    return tut_conditions.ComplexConditionAnd(_readComplexCondition(xmlCtx, section, flags))


def _readComplexConditionOr(xmlCtx, section, flags):
    return tut_conditions.ComplexConditionOr(_readComplexCondition(xmlCtx, section, flags))


def _parseEffectTriggeredCondition(xmlCtx, section, state):
    entityID = parseID(xmlCtx, section, 'Specify a entity ID')
    return tut_conditions.EffectTriggeredCondition(entityID, state)


def _readEffectTriggeredCondition(xmlCtx, section, _):
    return _parseEffectTriggeredCondition(xmlCtx, section, _COND_STATE.ACTIVE)


def _readEffectNotTriggeredCondition(xmlCtx, section, _):
    return _parseEffectTriggeredCondition(xmlCtx, section, ~_COND_STATE.ACTIVE)


def _parseBonusReceivedCondition(xmlCtx, section, state):
    entityID = parseID(xmlCtx, section, 'Specify a entity ID')
    return tut_conditions.BonusReceivedCondition(entityID, state)


def _readBonusReceivedCondition(xmlCtx, section, _):
    return _parseBonusReceivedCondition(xmlCtx, section, _COND_STATE.ACTIVE)


def _readBonusNotReceivedCondition(xmlCtx, section, _):
    return _parseBonusReceivedCondition(xmlCtx, section, ~_COND_STATE.ACTIVE)


def _readServiceCondition(xmlCtx, section, _):
    entityID = parseID(xmlCtx, section, 'Specify a entity ID')
    serviceClass = _getClass(entityID, xmlCtx, section)
    return tut_conditions.ServiceCondition(entityID, serviceClass)


def _readClassCondition(xmlCtx, section, _):
    entityID = parseID(xmlCtx, section, 'Specify a entity ID')
    conditionClass = _getClass(entityID, xmlCtx, section)
    tags = section.keys()
    arguments = parseID(xmlCtx, section['arguments'], '') if 'arguments' in tags else ''
    return tut_conditions.ClassCondition(entityID, conditionClass, arguments)


def _getClass(entityID, xmlCtx, section):
    tags = section.keys()
    if 'path' in tags:
        path = parseID(xmlCtx, section['path'], 'Specify a path.')
    else:
        path = None
    try:
        if path is not None:
            resultClass = getattr(importlib.import_module(path), entityID)
        else:
            resultClass = importlib.import_module(entityID)
    except (ImportError, NameError):
        _xml.raiseWrongXml(xmlCtx, section.name, 'Class %s not found!' % entityID)
        return

    return resultClass


_BASE_CONDITION_TAGS = {'active': lambda xmlCtx, section, flags: _readFlagCondition(xmlCtx, section, _COND_STATE.ACTIVE, flags),
 'inactive': lambda xmlCtx, section, flags: _readFlagCondition(xmlCtx, section, ~_COND_STATE.ACTIVE, flags),
 'global-active': lambda xmlCtx, section, flags: _readGlobalFlagCondition(xmlCtx, section, _COND_STATE.ACTIVE),
 'global-inactive': lambda xmlCtx, section, flags: _readGlobalFlagCondition(xmlCtx, section, ~_COND_STATE.ACTIVE),
 'is-widow-opened': lambda xmlCtx, section, flags: _readWindowOnSceneCondition(xmlCtx, section, _COND_STATE.ACTIVE),
 'is-widow-closed': lambda xmlCtx, section, flags: _readWindowOnSceneCondition(xmlCtx, section, ~_COND_STATE.ACTIVE),
 'game-item': _readGameItemCondition,
 'var': _readVarCondition,
 'effect-triggered': _readEffectTriggeredCondition,
 'effect-not-triggered': _readEffectNotTriggeredCondition,
 'bonus-received': _readBonusReceivedCondition,
 'bonus-not-received': _readBonusNotReceivedCondition,
 'service': _readServiceCondition,
 'class-condition': _readClassCondition,
 'component-on-scene': lambda xmlCtx, section, flags: _readComponentOnSceneCondition(xmlCtx, section, _COND_STATE.ACTIVE),
 'component-not-on-scene': lambda xmlCtx, section, flags: _readComponentOnSceneCondition(xmlCtx, section, ~_COND_STATE.ACTIVE),
 'on-scene': lambda xmlCtx, section, flags: _readCurrentSceneCondition(xmlCtx, section, _COND_STATE.ACTIVE),
 'not-on-scene': lambda xmlCtx, section, flags: _readCurrentSceneCondition(xmlCtx, section, ~_COND_STATE.ACTIVE),
 'view-present': lambda xmlCtx, section, flags: _readViewPresentCondition(xmlCtx, section, _COND_STATE.ACTIVE),
 'view-not-present': lambda xmlCtx, section, flags: _readViewPresentCondition(xmlCtx, section, ~_COND_STATE.ACTIVE),
 'condition-hint-showed': _readConnectedItemCondition,
 'condition-and': _readComplexConditionAnd,
 'condition-or': _readComplexConditionOr}

class ConditionTags(object):

    def __init__(self):
        self.tags = _BASE_CONDITION_TAGS.copy()


_conditions = ConditionTags()

def setConditionsParsers(parsers):
    _conditions.tags.clear()
    _conditions.tags = _BASE_CONDITION_TAGS.copy()
    _conditions.tags.update(parsers)


def readConditions(xmlCtx, section, flags):
    result = tut_conditions.Conditions()
    for name, subSec in section.items():
        if name == 'either':
            eitherCondition = readConditions(xmlCtx, subSec, flags)
            result.appendEitherBlock(eitherCondition)
        function = _conditions.tags.get(name)
        if function is None:
            LOG_ERROR('Condition is not supported: ', name)
            continue
        result.append(function(xmlCtx, subSec, flags))

    return result


def _parseConditions(xmlCtx, section, flags):
    condSec = section['condition']
    return readConditions(xmlCtx, condSec, flags) if condSec is not None else None


ACTION_TAGS = {'click': GuiEventType.CLICK,
 'click-outside': GuiEventType.CLICK_OUTSIDE,
 'esc': GuiEventType.ESC,
 'enable': GuiEventType.ENABLE,
 'disable': GuiEventType.DISABLE}

def parseAction(xmlCtx, section, flags):
    name = section.name
    if name not in ACTION_TAGS:
        LOG_ERROR('Action is not supported: ', name)
        return
    else:
        targetID = parseID(xmlCtx, section, 'Specify a target ID')
        action = tutorial_chapter.Action(ACTION_TAGS[name], targetID)
        if 'effects' in section.keys():
            for _, effectSec in _xml.getChildren(xmlCtx, section, 'effects'):
                effect = _parseEffect(xmlCtx, effectSec, flags)
                if effect is not None:
                    action.addEffect(effect)

        return action


def parseActions(xmlCtx, section, flags):
    result = []
    for _, subSec in section.items():
        action = parseAction(xmlCtx, subSec, flags)
        if action is not None:
            result.append(action)

    return result


def _readEffectsGroupSection(xmlCtx, section, flags, conditions):
    _effects = (_parseEffect(xmlCtx, effectSec, flags) for _, effectSec in _xml.getChildren(xmlCtx, section, 'effects'))
    return effects.EffectsGroup(tuple((e for e in _effects if e is not None)), conditions)


def _readActivateEffectSection(xmlCtx, section, flags, conditions):
    flagID = parseID(xmlCtx, section, 'Specify a flag ID')
    if flagID not in flags:
        flags.append(flagID)
    return effects.HasTargetEffect(flagID, _EFFECT_TYPE.ACTIVATE, conditions=conditions)


def _readDeactivateEffectSection(xmlCtx, section, flags, conditions):
    flagID = parseID(xmlCtx, section, 'Specify a flag ID')
    if flagID not in flags:
        flags.append(flagID)
    return effects.HasTargetEffect(flagID, _EFFECT_TYPE.DEACTIVATE, conditions=conditions)


def _readGlobalActivateEffectSection(xmlCtx, section, _, conditions):
    flagID = parseID(xmlCtx, section, 'Specify a flag ID')
    return effects.HasTargetEffect(flagID, _EFFECT_TYPE.GLOBAL_ACTIVATE, conditions=conditions)


def _readGlobalDeactivateEffectSection(xmlCtx, section, _, conditions):
    flagID = parseID(xmlCtx, section, 'Specify a flag ID')
    return effects.HasTargetEffect(flagID, _EFFECT_TYPE.GLOBAL_DEACTIVATE, conditions=conditions)


def _readNextChapterEffectSection(xmlCtx, section, _, conditions):
    targetID = section.asString
    return effects.HasTargetEffect(targetID, _EFFECT_TYPE.NEXT_CHAPTER, conditions=conditions)


def _readRunTriggerEffectSection(xmlCtx, section, _, conditions):
    triggerID = parseID(xmlCtx, section, 'Specify a trigger ID')
    return effects.HasTargetEffect(triggerID, _EFFECT_TYPE.RUN_TRIGGER, conditions=conditions)


def _readRequestBonusEffectSection(xmlCtx, section, _, conditions):
    chapterID = section.asString
    return effects.HasTargetEffect(chapterID, _EFFECT_TYPE.REQUEST_BONUS, conditions=conditions)


def _readShowHintSection(xmlCtx, section, _, conditions):
    hintID = parseID(xmlCtx, section, 'Specify a hint ID')
    return effects.HasTargetEffect(hintID, _EFFECT_TYPE.SHOW_HINT, conditions=conditions)


def _readCloseHintSection(xmlCtx, section, _, conditions):
    hintID = parseID(xmlCtx, section, 'Specify a hint ID')
    return effects.HasTargetEffect(hintID, _EFFECT_TYPE.CLOSE_HINT, conditions=conditions)


def _readShowDialogSection(xmlCtx, section, _, conditions):
    dialogID = parseID(xmlCtx, section, 'Specify a dialog ID')
    return effects.HasTargetEffect(dialogID, _EFFECT_TYPE.SHOW_DIALOG, conditions=conditions)


def _readShowWindowSection(xmlCtx, section, _, conditions):
    windowID = parseID(xmlCtx, section, 'Specify a window ID')
    return effects.HasTargetEffect(windowID, _EFFECT_TYPE.SHOW_WINDOW, conditions=conditions)


def _readShowAwardWindowSection(xmlCtx, section, _, conditions):
    windowID = parseID(xmlCtx, section, 'Specify a window ID')
    return effects.HasTargetEffect(windowID, _EFFECT_TYPE.SHOW_AWARD_WINDOW, conditions=conditions)


def _readShowMessageSection(xmlCtx, section, _, conditions):
    messageID = parseID(xmlCtx, section, 'Specify a message ID')
    return effects.HasTargetEffect(messageID, _EFFECT_TYPE.SHOW_MESSAGE, conditions=conditions)


def _readPlayMusicSection(xmlCtx, section, _, conditions):
    messageID = parseID(xmlCtx, section, 'Specify a music ID')
    return effects.HasTargetEffect(messageID, _EFFECT_TYPE.PLAY_MUSIC, conditions=conditions)


def _readSetGuiItemCriteria(xmlCtx, section, _, conditions):
    criteriaID = parseID(xmlCtx, section, 'Specify a criteria ID')
    return effects.HasTargetEffect(criteriaID, _EFFECT_TYPE.SET_GUI_ITEM_CRITERIA, conditions=conditions)


def _setReadGuiItemViewCriteria(xmlCtx, section, _, conditions):
    criteriaID = parseID(xmlCtx, section, 'Specify a criteria ID')
    return effects.HasTargetEffect(criteriaID, _EFFECT_TYPE.SET_GUI_ITEM_VIEW_CRITERIA, conditions=conditions)


def _readSetActionSection(xmlCtx, section, _, conditions):
    actionID = parseID(xmlCtx, section, 'Specify a action ID')
    return effects.HasTargetEffect(actionID, _EFFECT_TYPE.SET_ACTION, conditions=conditions)


def _readRemoveActionSection(xmlCtx, section, _, conditions):
    actionID = parseID(xmlCtx, section, 'Specify a action ID')
    return effects.HasTargetEffect(actionID, _EFFECT_TYPE.REMOVE_ACTION, conditions=conditions)


def _readSetVarSection(xmlCtx, section, _, conditions):
    varID = parseID(xmlCtx, section, 'Specify a var ID')
    return effects.HasTargetEffect(varID, _EFFECT_TYPE.SET_VAR, conditions=conditions)


def _readGuiItemPropertiesEffectSection(xmlCtx, section, _, conditions, fixedProp=None):
    itemID = parseID(xmlCtx, section, 'Specify a item ID')
    props = {}
    if fixedProp is None:
        for _, subSec in _xml.getChildren(xmlCtx, section, 'properties'):
            propType, propSec = subSec.items()[0]
            props[subSec.asString] = readVarValue(propType, propSec)

    else:
        propName, propType = fixedProp
        if propType is not None:
            props[propName] = readVarValue(propType, _xml.getSubsection(xmlCtx, section, 'val'))
        else:
            props[propName] = None
    return effects.SetGuiItemProperties(itemID, props, conditions=conditions)


def _readPlayAnimationEffectSection(xmlCtx, section, _, conditions):
    itemID = parseID(xmlCtx, section, 'Specify an item ID')
    animType = _xml.readString(xmlCtx, section, 'type')
    waitForFinish = _xml.readBool(xmlCtx, section, 'wait_for_finish')
    return effects.PlayAnimationEffect(itemID, animType, waitForFinish, conditions=conditions)


def _readInvokeGuiCmdSection(xmlCtx, section, _, conditions):
    commandID = parseID(xmlCtx, section, 'Specify a command ID')
    argOverrides = {}
    argsSection = _xml.getSubsection(xmlCtx, section, 'args', throwIfMissing=False)
    if argsSection is not None:
        for _, subSec in argsSection.items():
            arg = resource_helper.readItem(xmlCtx, subSec, 'arg')
            argOverrides[arg.name] = arg.value

    return effects.InvokeGuiCommand(commandID, argOverrides, conditions=conditions)


def _readInvokePlayerCmdSection(xmlCtx, section, _, conditions):
    commandID = parseID(xmlCtx, section, 'Specify a command ID')
    return effects.HasTargetEffect(commandID, _EFFECT_TYPE.INVOKE_PLAYER_CMD, conditions=conditions)


def _readGoSceneSection(xmlCtx, section, _, conditions):
    sceneID = parseID(xmlCtx, section, 'Specify a setting ID')
    return effects.HasTargetEffect(sceneID, _EFFECT_TYPE.GO_SCENE, conditions=conditions)


def _readSetAllowedToFightEffectSection(xmlCtx, section, _, conditions):
    value = _xml.readBool(xmlCtx, section, 'value')
    return effects.SetAllowedToFightEffect(value, conditions=conditions)


def _readSelectVehicleInHangarSection(xmlCtx, section, flags, conditions):
    targetID = section.asString
    return effects.HasTargetEffect(targetID, effects.EFFECT_TYPE.SELECT_VEHICLE_IN_HANGAR, conditions=conditions)


def _readPlaySoundEffectSection(xmlCtx, section, flags, conditions):
    soundID = section.asString
    soundEvent = _xml.readString(xmlCtx, section, 'event')
    soundEvent = getattr(SOUND_EVENT, soundEvent, None)
    return effects.PlaySoundEffect(soundID, soundEvent, conditions=conditions)


def _readCloseViewEffectSection(xmlCtx, section, flags, conditions):
    layer = LAYER_NAMES.LAYER_ORDER.index(_xml.readString(xmlCtx, section, 'type'))
    viewAlias = _xml.readString(xmlCtx, section, 'alias')
    return effects.HasTargetEffect((layer, viewAlias), effects.EFFECT_TYPE.CLOSE_VIEW, conditions=conditions)


def makeSimpleEffectReader(effectType):
    return lambda xmlCtx, section, flags, conditions: effects.SimpleEffect(effectType=effectType, conditions=conditions)


_BASE_EFFECT_TAGS = {'effects-group': _readEffectsGroupSection,
 'activate': _readActivateEffectSection,
 'inactivate': _readDeactivateEffectSection,
 'global-activate': _readGlobalActivateEffectSection,
 'global-inactivate': _readGlobalDeactivateEffectSection,
 'refuse-training': makeSimpleEffectReader(_EFFECT_TYPE.REFUSE_TRAINING),
 'next-chapter': _readNextChapterEffectSection,
 'run-trigger': _readRunTriggerEffectSection,
 'request-bonus': _readRequestBonusEffectSection,
 'set-gui-item-props': _readGuiItemPropertiesEffectSection,
 'set-visible': partial(_readGuiItemPropertiesEffectSection, fixedProp=('visible', 'asBool')),
 'set-button-enabled': partial(_readGuiItemPropertiesEffectSection, fixedProp=('enabled', 'asBool')),
 'update-layout': partial(_readGuiItemPropertiesEffectSection, fixedProp=('layout', None)),
 'play-animation': _readPlayAnimationEffectSection,
 'finish-training': makeSimpleEffectReader(_EFFECT_TYPE.FINISH_TRAINING),
 'go-scene': _readGoSceneSection,
 'invoke-gui-cmd': _readInvokeGuiCmdSection,
 'invoke-player-cmd': _readInvokePlayerCmdSection,
 'show-hint': _readShowHintSection,
 'close-hint': _readCloseHintSection,
 'show-dialog': _readShowDialogSection,
 'show-window': _readShowWindowSection,
 'show-award-window': _readShowAwardWindowSection,
 'show-message': _readShowMessageSection,
 'play-music': _readPlayMusicSection,
 'set-gui-item-criteria': _readSetGuiItemCriteria,
 'set-gui-item-view-criteria': _setReadGuiItemViewCriteria,
 'set-action': _readSetActionSection,
 'remove-action': _readRemoveActionSection,
 'set-var': _readSetVarSection,
 'clear-scene': makeSimpleEffectReader(_EFFECT_TYPE.CLEAR_SCENE),
 'set-allowed-to-fight': _readSetAllowedToFightEffectSection,
 'select-in-hangar': _readSelectVehicleInHangarSection,
 'play-sound': _readPlaySoundEffectSection,
 'close-view': _readCloseViewEffectSection}
_EFFECT_TAGS = _BASE_EFFECT_TAGS.copy()

def setEffectsParsers(parsers):
    global _EFFECT_TAGS
    global _BASE_EFFECT_TAGS
    _EFFECT_TAGS.clear()
    _EFFECT_TAGS = _BASE_EFFECT_TAGS.copy()
    _EFFECT_TAGS.update(parsers)


def _parseEffect(xmlCtx, section, flags, afterBattle=False):
    function = _EFFECT_TAGS.get(section.name)
    result = None
    if 'after-battle-filter' in section.keys() and not afterBattle:
        return result
    else:
        if function is not None:
            result = function(xmlCtx, section, flags, _parseConditions(xmlCtx, section, flags))
        else:
            LOG_ERROR('Effect is not supported:', section.name)
        return result


_TRIGGER_SUB_PARSERS = {}

def readValidateVarTriggerSection(xmlCtx, section, triggerID, clazz, **kwargs):
    validateVarID = _xml.readString(xmlCtx, section, 'validate-var')
    setVarID = section.readString('set-var')
    if not setVarID:
        setVarID = None
    return clazz(triggerID, validateVarID, setVarID=setVarID, **kwargs)


def setTriggersParsers(parsers):
    global _TRIGGER_SUB_PARSERS
    _TRIGGER_SUB_PARSERS.clear()
    _TRIGGER_SUB_PARSERS = parsers.copy()


def parseTrigger(xmlCtx, section, flags, chapter):
    triggerID = parseID(xmlCtx, section, 'Specify a trigger ID')
    trigger = None
    triggerType = _xml.readString(xmlCtx, section, 'type')
    parser = _TRIGGER_SUB_PARSERS.get(triggerType)
    if parser is not None:
        trigger = parser(xmlCtx, section, chapter, triggerID)
        if 'on-effects' in section.keys():
            for _, effectSec in _xml.getChildren(xmlCtx, section, 'on-effects'):
                effect = _parseEffect(xmlCtx, effectSec, flags)
                if effect is not None:
                    trigger.addOnEffect(effect)

        if 'off-effects' in section.keys():
            for _, effectSec in _xml.getChildren(xmlCtx, section, 'off-effects'):
                effect = _parseEffect(xmlCtx, effectSec, flags)
                if effect is not None:
                    trigger.addOffEffect(effect)

        if 'exclude-triggers' in section.keys():
            for _, triggerSec in _xml.getChildren(xmlCtx, section, 'exclude-triggers'):
                trigger.addExcludeTriggerID(triggerSec.asString)

    else:
        LOG_ERROR('Trigger is not supported:', triggerType)
    return trigger


def _parseGuiItem(xmlCtx, section, flags, itemFlags):
    itemID = parseID(xmlCtx, section, 'Specify a GUI item ID')
    tags = section.keys()
    item = tutorial_chapter.GuiItemRef(itemID, conditions=_parseConditions(xmlCtx, section, flags))
    if 'on-scene-effects' in tags:
        for _, effectSec in _xml.getChildren(xmlCtx, section, 'on-scene-effects'):
            effect = _parseEffect(xmlCtx, effectSec, itemFlags)
            if effect is not None:
                item.addOnSceneEffect(effect)

    if 'not-on-scene-effects' in tags:
        for _, effectSec in _xml.getChildren(xmlCtx, section, 'not-on-scene-effects'):
            effect = _parseEffect(xmlCtx, effectSec, itemFlags)
            if effect is not None:
                item.addNotOnSceneEffect(effect)

    return item


def _readAsStringSection(name, section):
    return translation(getattr(section, name))


def _readAsListSection(_, section):
    value = []
    for name, subSec in section.items():
        if name == 'condition':
            continue
        value.append(readVarValue(name, subSec))

    return value


def _readAsDictSection(_, section):
    value = {}
    for name, subSec in section.items():
        valueType, valueSec = subSec.items()[0]
        value[name] = readVarValue(valueType, valueSec)

    return value


def _readAsIntSequence(_, section):
    return [ (int(item) if item else None) for item in section.asString.split(' ') ]


def _readAsVehTypeNameSection(_, section):
    return vehicles.makeIntCompactDescrByID('vehicle', *vehicles.g_list.getIDsByName(section.asString))


def _readAsVehItemNameSection(itemName, itemIDsMethod, section):
    nationName, chassisName = section.asString.split(':')
    nationID = nations.INDICES[nationName]
    itemGetter = getattr(vehicles.g_cache, itemIDsMethod)
    return vehicles.makeIntCompactDescrByID(itemName, nationID, itemGetter(nationID)[chassisName])


def _readAsEquipmentSection(_, section):
    equipmentName = section.asString
    return vehicles.makeIntCompactDescrByID('equipment', nations.NONE_INDEX, vehicles.g_cache.equipmentIDs()[equipmentName])


def _readAsItemSection(_, section):
    return {section.readInt('itemTypeCD'): section.readInt('count')}


def _readAsBoosterSection(_, section):
    return {section.readInt('boosterID'): {'count': section.readInt('count')}}


def _readAsItemsDict(_, section):
    value = {}
    for name, subSec in section.items():
        value.update(readVarValue(name, subSec))

    return value


CUSTOM_VARS_PARERS = {'asString': _readAsStringSection,
 'asDict': _readAsDictSection,
 'asList': _readAsListSection,
 'asIntSequence': _readAsIntSequence,
 'asVehTypeName': _readAsVehTypeNameSection,
 'asVehChassisName': lambda name, section: _readAsVehItemNameSection('vehicleChassis', 'chassisIDs', section),
 'asVehGunName': lambda name, section: _readAsVehItemNameSection('vehicleGun', 'gunIDs', section),
 'asVehEngineName': lambda name, section: _readAsVehItemNameSection('vehicleEngine', 'engineIDs', section),
 'asVehRadioName': lambda name, section: _readAsVehItemNameSection('vehicleRadio', 'radioIDs', section),
 'asVehTurretName': lambda name, section: _readAsVehItemNameSection('vehicleTurret', 'turretIDs', section),
 'asEquipment': _readAsEquipmentSection,
 'asItem': _readAsItemSection,
 'asBooster': _readAsBoosterSection,
 'asItemsDict': _readAsItemsDict}

def readVarValue(name, section):
    if name in CUSTOM_VARS_PARERS:
        value = CUSTOM_VARS_PARERS[name](name, section)
    else:
        value = getattr(section, name)
    return value


def parseVarSet(xmlCtx, section, flags):
    varID = parseID(xmlCtx, section, 'Specify a var ID')
    varSet = []
    for name, subSec in section.items():
        value = readVarValue(name, subSec)
        varSet.append((value, _parseConditions(xmlCtx, subSec, flags)))

    return tutorial_chapter.VarSet(varID, varSet)


def parseBonus(xmlCtx, section):
    tags = section.keys()
    altBonusValues = None
    if 'altBonus' in tags:
        altBonusSec = section['altBonus']
        altBonusValues = readValues(altBonusSec)
    valueCondition = None
    if 'valueCondition' in tags:
        valueConditionSec = section['valueCondition']
        valueCondition = _parseConditions(xmlCtx, valueConditionSec, [])
    return tutorial_chapter.Bonus(section.readInt('id', -1), section.readString('message'), readValues(section), altBonusValues, valueCondition)


_DIALOG_SUB_PARERS = {}

def setDialogsParsers(parsers):
    global _DIALOG_SUB_PARERS
    _DIALOG_SUB_PARERS.clear()
    _DIALOG_SUB_PARERS = parsers.copy()


def _parseDialog(xmlCtx, section, flags):
    dialogID = parseID(xmlCtx, section, 'Specify a dialog ID')
    dialogType = _xml.readString(xmlCtx, section, 'type')
    bSec = _xml.getSubsection(xmlCtx, section, 'buttons')
    submitID = bSec.readString('submit', '')
    cancelID = bSec.readString('cancel', '')
    customID = bSec.readString('custom', '')
    content = {'type': dialogType,
     'dialogID': dialogID,
     'submitID': submitID,
     'cancelID': cancelID,
     'customID': customID,
     'title': translation(_xml.readStringOrNone(xmlCtx, section, 'title') or ''),
     'message': translation(_xml.readStringOrNone(xmlCtx, section, 'text') or ''),
     'imageUrl': _xml.readStringOrNone(xmlCtx, section, 'image') or ''}
    parser = _DIALOG_SUB_PARERS.get(dialogType)
    if parser is not None:
        dialog = parser(xmlCtx, section, flags, dialogID, dialogType, content)
    else:
        dialog = tutorial_chapter.PopUp(dialogID, dialogType, content)
    dialog.setActions(parseActions(xmlCtx, _xml.getSubsection(xmlCtx, section, 'actions'), flags))
    return dialog


_WINDOW_SUB_PARERS = {}

def setWindowsParsers(parsers):
    global _WINDOW_SUB_PARERS
    _WINDOW_SUB_PARERS.clear()
    _WINDOW_SUB_PARERS = parsers.copy()


def _parseWindow(xmlCtx, section, flags):
    windowID = parseID(xmlCtx, section, 'Specify a window ID')
    windowType = _xml.readString(xmlCtx, section, 'type')
    content = {}
    bSec = _xml.getSubsection(xmlCtx, section, 'buttons')
    content['closeID'] = _xml.readString(xmlCtx, bSec, 'close')
    content['type'] = windowType
    content['windowID'] = windowID
    parser = _WINDOW_SUB_PARERS.get(windowType)
    if parser is not None:
        window = parser(xmlCtx, section, flags, windowID, windowType, content)
        window.setActions(parseActions(xmlCtx, _xml.getSubsection(xmlCtx, section, 'actions'), flags))
    else:
        window = None
        LOG_ERROR('Type of window is not supported: ', windowType)
    return window


def _parseSimpleWindow(xmlCtx, section, flags):
    windowID = parseID(xmlCtx, section, 'Specify a window ID')
    windowType = _xml.readString(xmlCtx, section, 'type')
    content = {}
    parser = _WINDOW_SUB_PARERS.get(windowType)
    if parser is not None:
        window = parser(xmlCtx, section, flags, windowID, windowType, content)
    else:
        window = None
        LOG_ERROR('Type of window is not supported: ', windowType)
    return window


def _parseMessage(xmlCtx, section, _):
    messageID = parseID(xmlCtx, section, 'Specify a message ID')
    guiType = _xml.readString(xmlCtx, section, 'type')
    text = translation(_xml.readString(xmlCtx, section, 'text'))
    return tutorial_chapter.Message(messageID, guiType, text)


def _readPlayerCommand(xmlCtx, section, _):
    cmdID = parseID(xmlCtx, section, 'Specify a player command ID')
    name = _xml.readString(xmlCtx, section, 'name')
    argsSec = _xml.getChildren(xmlCtx, section, 'args')
    kwargsSec = _xml.getChildren(xmlCtx, section, 'kwargs')
    cmdArgs = []
    for name, argSec in argsSec:
        cmdArgs.append(readVarValue(name, argSec))

    cmdKwargs = {}
    for name, kwargSec in kwargsSec:
        argType, subSec = kwargSec.items()[0]
        cmdKwargs[name] = readVarValue(argType, subSec)

    return tutorial_chapter.PlayerCommand(cmdID, name, cmdArgs=tuple(cmdArgs), cmdKwargs=cmdKwargs)


def _readQuery(xmlCtx, section, _):
    queryID = parseID(xmlCtx, section, 'Specify a query ID')
    return tutorial_chapter.Query(queryID, _xml.readString(xmlCtx, section, 'type'), _xml.readString(xmlCtx, section, 'var-ref'), extra=section.readString('extra'))


def _readGuiItemCriteria(xmlCtx, section, _):
    criteriaID = parseID(xmlCtx, section, 'Specify a criteria ID')
    itemID = None
    if 'item-id' in section.keys():
        itemID = parseID(xmlCtx, section['item-id'], 'Specify a item ID')
    else:
        _xml.raiseWrongXml(xmlCtx, section.name, 'Specify a item ID')
    return tutorial_chapter.GuiItemCriteria(criteriaID, itemID, _xml.readString(xmlCtx, section, 'value'))


def _readGuiItemViewCriteria(xmlCtx, section, _):
    criteriaID = parseID(xmlCtx, section, 'Specify a criteria ID')
    componentIDs = [ parseID(xmlCtx, componentSec, 'Specify a component ID') for _, componentSec in _xml.getChildren(xmlCtx, section, 'components') ]
    return tutorial_chapter.GuiItemViewCriteria(criteriaID, componentIDs, _xml.readString(xmlCtx, section, 'value'))


def _readAction(xmlCtx, section, eventType, flags):
    actionID = parseID(xmlCtx, section, 'Specify a action ID')
    itemID = None
    if 'item-id' in section.keys():
        itemID = parseID(xmlCtx, section['item-id'], 'Specify a item ID')
    else:
        _xml.raiseWrongXml(xmlCtx, section.name, 'Specify a item ID')
    action = tutorial_chapter.Action(eventType, itemID)
    action.setID(actionID)
    for _, effectSec in _xml.getChildren(xmlCtx, section, 'effects'):
        effect = _parseEffect(xmlCtx, effectSec, flags)
        if effect is not None:
            action.addEffect(effect)

    return action


def _readClickAction(xmlCtx, section, flags):
    return _readAction(xmlCtx, section, GuiEventType.CLICK, flags)


def _readClickOutsideAction(xmlCtx, section, flags):
    return _readAction(xmlCtx, section, GuiEventType.CLICK_OUTSIDE, flags)


def _readEscapeAction(xmlCtx, section, flags):
    return _readAction(xmlCtx, section, GuiEventType.ESC, flags)


def _readEnableAction(xmlCtx, section, flags):
    return _readAction(xmlCtx, section, GuiEventType.ENABLE, flags)


def _readDisableAction(xmlCtx, section, flags):
    return _readAction(xmlCtx, section, GuiEventType.DISABLE, flags)


def _readGameAttribute(xmlCtx, section, _):
    attributeID = parseID(xmlCtx, section, 'Specify a attribute ID')
    tags = section.keys()
    if 'name' in tags:
        name = parseID(xmlCtx, section['name'], 'Specify a name of game attribute')
    else:
        _xml.raiseWrongXml(xmlCtx, section.name, 'Specify a item ID')
        return
    if 'var-ref' in tags:
        varID = parseID(xmlCtx, section['var-ref'], 'Specify a var ID')
    else:
        _xml.raiseWrongXml(xmlCtx, section.name, 'Specify a item ID')
        return
    value = section.readString('args')
    if value:
        args = value.split()
    else:
        args = None
    return tutorial_chapter.GameAttribute(attributeID, name, varID, args)


_BASE_ENTITY_PARSERS = {'dialog': _parseDialog,
 'window': _parseWindow,
 'simple-window': _parseSimpleWindow,
 'message': _parseMessage,
 'player-cmd': _readPlayerCommand,
 'query': _readQuery,
 'gui-item-criteria': _readGuiItemCriteria,
 'gui-item-view-criteria': _readGuiItemViewCriteria,
 'click-action': _readClickAction,
 'click-outside-action': _readClickOutsideAction,
 'esc-action': _readEscapeAction,
 'enable-action': _readEnableAction,
 'disable-action': _readDisableAction,
 'game-attribute': _readGameAttribute}
_ENTITY_PARSERS = _BASE_ENTITY_PARSERS.copy()

def setEntitiesParsers(parsers):
    global _ENTITY_PARSERS
    global _BASE_ENTITY_PARSERS
    _ENTITY_PARSERS.clear()
    _ENTITY_PARSERS = _BASE_ENTITY_PARSERS.copy()
    _ENTITY_PARSERS.update(parsers)


def parseEntity(xmlCtx, name, section, flags):
    parser = _ENTITY_PARSERS.get(name)
    item = None
    if parser is not None:
        item = parser(xmlCtx, section, flags)
    else:
        LOG_ERROR('Entity is not supported:', name)
    return item


def readValues(section):
    result = {}
    valuesSec = section['values']
    if valuesSec is not None:
        for name, valueSection in valuesSec.items():
            valueType, valueSec = valueSection.items()[0]
            result[name] = readVarValue(valueType, valueSec)

    return result


def readQuestAwardWindowSection(xmlCtx, section, _, windowID, windowType, content):
    content['description'] = translation(section.readString('description'))
    content['header'] = translation(section.readString('header'))
    content['bgImage'] = section.readString('image')
    varRef = None
    if 'var-ref' in section.keys():
        varRef = _xml.readString(xmlCtx, section, 'var-ref')
    return tutorial_chapter.PopUp(windowID, windowType, content, varRef, forcedQuery=True)


_AVAILABLE_DIRECTIONS = ('L', 'T', 'R', 'B')
_ArrowProps = namedtuple('_ArrowProps', ('direction', 'loop', 'positionValue', 'textPadding'))
_Padding = namedtuple('_Padding', ('left', 'top', 'right', 'bottom'))

def parseHint(xmlCtx, section):
    sectionInfo = dict()
    sectionInfo['hintID'] = parseID(xmlCtx, section, 'Specify a hint ID')
    if 'item-id' in section.keys():
        sectionInfo['itemID'] = parseID(xmlCtx, section['item-id'], 'Specify a item ID')
    else:
        _xml.raiseWrongXml(xmlCtx, section.name, 'Specify a item ID')
        return
    tags = section.keys()
    sectionInfo['text'] = translation(_xml.readString(xmlCtx, section, 'text'))
    if 'arrow' in tags:
        subSec = section['arrow']
        direction = _xml.readString(xmlCtx, subSec, 'direction')
        if direction not in _AVAILABLE_DIRECTIONS:
            _xml.raiseWrongXml(xmlCtx, section, 'Arrow direction {} is invalid.'.format(direction))
        positionValue = _xml.readFloat(xmlCtx, subSec, 'position-value', 0.5)
        textPadding = _xml.readFloat(xmlCtx, subSec, 'text-padding', 0)
        sectionInfo['arrow'] = _ArrowProps(direction, _xml.readBool(xmlCtx, subSec, 'loop'), positionValue, textPadding)
    else:
        sectionInfo['arrow'] = None
    if 'padding' in tags:
        subSec = section['padding']
        sectionInfo['padding'] = _Padding(_xml.readFloat(xmlCtx, subSec, 'left'), _xml.readFloat(xmlCtx, subSec, 'top'), _xml.readFloat(xmlCtx, subSec, 'right'), _xml.readFloat(xmlCtx, subSec, 'bottom'))
    else:
        sectionInfo['padding'] = None
    sectionInfo['hasBox'] = section.readBool('has-box', True)
    sectionInfo['conditions'] = _parseConditions(xmlCtx, section, [])
    sectionInfo['checked-ui-state'] = _parseNeededState(xmlCtx, section)
    sectionInfo['equalActions'] = section.readBool('equal-actions', False)
    sectionInfo['ignoreOutsideClick'] = section.readBool('ignore-outside-click', False)
    sectionInfo['updateRuntime'] = section.readBool('update-runtime', False)
    sectionInfo['hideImmediately'] = section.readBool('hide-immediately', False)
    sectionInfo['checkViewArea'] = section.readBool('check-view-area', False)
    sectionInfo['persistent'] = section.readBool('persistent', False)
    return sectionInfo
