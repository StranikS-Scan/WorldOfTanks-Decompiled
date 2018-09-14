# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/__init__.py
from collections import namedtuple
from items import _xml, vehicles
from helpers.html import translation
import nations
from tutorial.data import chapter
from tutorial.data import effects
from tutorial.data import conditions
from tutorial.data.events import GUI_EVENT_TYPE
from tutorial.logger import LOG_ERROR
_EFFECT_TYPE = effects.EFFECT_TYPE
_COND_STATE = conditions.CONDITION_STATE

def parseID(xmlCtx, section, msg):
    entityID = section.asString
    if entityID is None or not len(entityID):
        _xml.raiseWrongXml(xmlCtx, section.name, msg)
    return entityID


def _readFlagCondition(xmlCtx, section, state, flags):
    flagID = parseID(xmlCtx, section, 'Specify a flag ID')
    if flagID not in flags:
        flags.append(flagID)
    return conditions.FlagCondition(flagID, state=state)


def _readGlobalFlagCondition(xmlCtx, section, state):
    flagID = parseID(xmlCtx, section, 'Specify a flag ID')
    return conditions.GlobalFlagCondition(flagID, state=state)


def _readWindowOnSceneCondition(xmlCtx, section, state):
    windowID = parseID(xmlCtx, section, 'Specify a window ID')
    return conditions.WindowOnSceneCondition(windowID, state=state)


_GAME_ITEM_CONDITION_TAGS = {'selected': _COND_STATE.SELECTED,
 'not-selected': ~_COND_STATE.SELECTED,
 'premium': _COND_STATE.PREMIUM,
 'not-premium': ~_COND_STATE.PREMIUM,
 'unlocked': _COND_STATE.UNLOCKED,
 'not-unlocked': ~_COND_STATE.UNLOCKED,
 'xp-enough': _COND_STATE.XP_ENOUGH,
 'xp-not-enough': ~_COND_STATE.XP_ENOUGH,
 'money-enough': _COND_STATE.MONEY_ENOUGH,
 'money-not-enough': ~_COND_STATE.MONEY_ENOUGH,
 'level': _COND_STATE.LEVEL,
 'not-level': ~_COND_STATE.LEVEL,
 'may-install': _COND_STATE.MAY_INSTALL,
 'may-not-install': ~_COND_STATE.MAY_INSTALL}
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
            otherID = parseID(xmlCtx, section[tag], 'Specify a other ID')
            return conditions.GameItemRelateStateCondition(varID, otherID, state)
        else:
            return conditions.GameItemSimpleStateCondition(varID, state)
    else:
        _xml.raiseWrongXml(xmlCtx, 'var', 'State of vehicle condition is not found: {0}'.format(section.keys()))
        return None
    return None


def _readVarCondition(xmlCtx, section, _):
    varID = parseID(xmlCtx, section, 'Specify a var ID')
    tags = section.keys()
    if 'is-none' in tags:
        return conditions.VarDefinedCondition(varID, ~_COND_STATE.ACTIVE)
    if 'is-not-none' in tags:
        return conditions.VarDefinedCondition(varID, _COND_STATE.ACTIVE)
    if 'equals' in tags:
        return conditions.VarCompareCondition(varID, _xml.readString(xmlCtx, section, 'equals'), _COND_STATE.EQUALS)
    if 'not-equals' in tags:
        return conditions.VarCompareCondition(varID, _xml.readString(xmlCtx, section, 'not-equals'), ~_COND_STATE.EQUALS)
    _xml.raiseWrongXml(xmlCtx, 'var', 'State of var condition is not found')


def _parseEffectTriggeredCondition(xmlCtx, section, state):
    entityID = parseID(xmlCtx, section, 'Specify a entity ID')
    return conditions.EffectTriggeredCondition(entityID, state)


def _readEffectTriggeredCondition(xmlCtx, section, _):
    return _parseEffectTriggeredCondition(xmlCtx, section, _COND_STATE.ACTIVE)


def _readEffectNotTriggeredCondition(xmlCtx, section, _):
    return _parseEffectTriggeredCondition(xmlCtx, section, ~_COND_STATE.ACTIVE)


def _parseBonusReceivedCondition(xmlCtx, section, state):
    entityID = parseID(xmlCtx, section, 'Specify a entity ID')
    return conditions.BonusReceivedCondition(entityID, state)


def _readBonusReceivedCondition(xmlCtx, section, _):
    return _parseBonusReceivedCondition(xmlCtx, section, _COND_STATE.ACTIVE)


def _readBonusNotReceivedCondition(xmlCtx, section, _):
    return _parseBonusReceivedCondition(xmlCtx, section, ~_COND_STATE.ACTIVE)


CONDITION_TAGS = {'active': lambda xmlCtx, section, flags: _readFlagCondition(xmlCtx, section, _COND_STATE.ACTIVE, flags),
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
 'bonus-not-received': _readBonusNotReceivedCondition}

def readConditions(xmlCtx, section, flags):
    result = conditions.Conditions()
    for name, subSec in section.items():
        if name == 'either':
            eitherCondition = readConditions(xmlCtx, subSec, flags)
            result.appendEitherBlock(eitherCondition)
        else:
            function = CONDITION_TAGS.get(name)
            if function is None:
                LOG_ERROR('Condition is not supported: ', name)
                continue
            result.append(function(xmlCtx, subSec, flags))

    return result


def _parseConditions(xmlCtx, section, flags):
    condSec = section['condition']
    if condSec is not None:
        return readConditions(xmlCtx, condSec, flags)
    else:
        return


ACTION_TAGS = {'click': GUI_EVENT_TYPE.CLICK,
 'click-outside': GUI_EVENT_TYPE.CLICK_OUTSIDE,
 'esc': GUI_EVENT_TYPE.ESC}

def parseAction(xmlCtx, section, flags):
    name = section.name
    if name not in ACTION_TAGS:
        LOG_ERROR('Action is not supported: ', name)
        return
    else:
        targetID = parseID(xmlCtx, section, 'Specify a target ID')
        action = chapter.Action(ACTION_TAGS[name], targetID)
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


def _readGuiItemCriteria(xmlCtx, section, _, conditions):
    criteriaID = parseID(xmlCtx, section, 'Specify a music ID')
    return effects.HasTargetEffect(criteriaID, _EFFECT_TYPE.SET_GUI_ITEM_CRITERIA, conditions=conditions)


def _readSetActionSection(xmlCtx, section, _, conditions):
    actionID = parseID(xmlCtx, section, 'Specify a action ID')
    return effects.HasTargetEffect(actionID, _EFFECT_TYPE.SET_ACTION, conditions=conditions)


def _readRemoveActionSection(xmlCtx, section, _, conditions):
    actionID = parseID(xmlCtx, section, 'Specify a action ID')
    return effects.HasTargetEffect(actionID, _EFFECT_TYPE.REMOVE_ACTION, conditions=conditions)


def _readSetVarSection(xmlCtx, section, _, conditions):
    varID = parseID(xmlCtx, section, 'Specify a var ID')
    return effects.HasTargetEffect(varID, _EFFECT_TYPE.SET_VAR, conditions=conditions)


def _readGuiItemPropertiesEffectSection(xmlCtx, section, _, conditions):
    itemID = parseID(xmlCtx, section, 'Specify a item ID')
    props = {}
    for _, subSec in _xml.getChildren(xmlCtx, section, 'properties'):
        propType, propSec = subSec.items()[0]
        props[subSec.asString] = readVarValue(propType, propSec)

    revert = section.readBool('revert')
    return effects.SetGuiItemProperty(itemID, props, conditions=conditions, revert=revert)


def _readInvokeGuiCmdSection(xmlCtx, section, _, conditions):
    commandID = parseID(xmlCtx, section, 'Specify a command ID')
    return effects.HasTargetEffect(commandID, _EFFECT_TYPE.INVOKE_GUI_CMD, conditions=conditions)


def _readInvokePlayerCmdSection(xmlCtx, section, _, conditions):
    commandID = parseID(xmlCtx, section, 'Specify a command ID')
    return effects.HasTargetEffect(commandID, _EFFECT_TYPE.INVOKE_PLAYER_CMD, conditions=conditions)


def _readGoSceneSection(xmlCtx, section, _, conditions):
    sceneID = parseID(xmlCtx, section, 'Specify a setting ID')
    return effects.HasTargetEffect(sceneID, _EFFECT_TYPE.GO_SCENE, conditions=conditions)


_BASE_EFFECT_TAGS = {'activate': _readActivateEffectSection,
 'inactivate': _readDeactivateEffectSection,
 'global-activate': _readGlobalActivateEffectSection,
 'global-inactivate': _readGlobalDeactivateEffectSection,
 'refuse-training': lambda xmlCtx, section, flags, conditions: effects.SimpleEffect(_EFFECT_TYPE.REFUSE_TRAINING, conditions=conditions),
 'next-chapter': _readNextChapterEffectSection,
 'run-trigger': _readRunTriggerEffectSection,
 'request-bonus': _readRequestBonusEffectSection,
 'set-gui-item-props': _readGuiItemPropertiesEffectSection,
 'finish-training': lambda xmlCtx, section, flags, conditions: effects.SimpleEffect(_EFFECT_TYPE.FINISH_TRAINING, conditions=conditions),
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
 'set-gui-item-criteria': _readGuiItemCriteria,
 'set-action': _readSetActionSection,
 'remove-action': _readRemoveActionSection,
 'set-var': _readSetVarSection,
 'clear-scene': lambda xmlCtx, section, flags, conditions: effects.SimpleEffect(_EFFECT_TYPE.CLEAR_SCENE, conditions=conditions)}
_EFFECT_TAGS = _BASE_EFFECT_TAGS.copy()

def setEffectsParsers(parsers):
    global _EFFECT_TAGS
    global _BASE_EFFECT_TAGS
    _EFFECT_TAGS.clear()
    _EFFECT_TAGS = _BASE_EFFECT_TAGS.copy()
    _EFFECT_TAGS.update(parsers)


def _parseEffect(xmlCtx, section, flags, afterBattle = False):
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
    props = {}
    tags = section.keys()
    if 'properties' in tags:
        for _, subSec in _xml.getChildren(xmlCtx, section, 'properties'):
            propType, propSec = subSec.items()[0]
            props[subSec.asString] = readVarValue(propType, propSec)

    item = chapter.GuiItemRef(itemID, props, conditions=_parseConditions(xmlCtx, section, flags))
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
    return map(lambda item: (int(item) if len(item) else None), section.asString.split(' '))


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

    return chapter.VarSet(varID, varSet)


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
    if not len(submitID) and not len(cancelID):
        _xml.raiseWrongXml(xmlCtx, '', 'Tag submit or cancel must be specified.')
    content = {'type': dialogType,
     'dialogID': dialogID,
     'submitID': submitID,
     'cancelID': cancelID,
     'title': translation(_xml.readString(xmlCtx, section, 'title')),
     'message': translation(_xml.readString(xmlCtx, section, 'text')),
     'imageUrl': section.readString('image')}
    parser = _DIALOG_SUB_PARERS.get(dialogType)
    if parser is not None:
        dialog = parser(xmlCtx, section, flags, dialogID, dialogType, content)
    else:
        dialog = chapter.PopUp(dialogID, dialogType, content)
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
    bSec = _xml.getSubsection(xmlCtx, section, 'buttons')
    content = {'closeID': _xml.readString(xmlCtx, bSec, 'close')}
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
    return chapter.Message(messageID, guiType, text)


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

    return chapter.PlayerCommand(cmdID, name, cmdArgs=tuple(cmdArgs), cmdKwargs=cmdKwargs)


def _readQuery(xmlCtx, section, _):
    queryID = parseID(xmlCtx, section, 'Specify a query ID')
    return chapter.Query(queryID, _xml.readString(xmlCtx, section, 'type'), _xml.readString(xmlCtx, section, 'var-ref'), extra=section.readString('extra'))


def _readGuiItemCriteria(xmlCtx, section, _):
    criteriaID = parseID(xmlCtx, section, 'Specify a criteria ID')
    itemID = None
    if 'item-id' in section.keys():
        itemID = parseID(xmlCtx, section['item-id'], 'Specify a item ID')
    else:
        _xml.raiseWrongXml(xmlCtx, section.name, 'Specify a item ID')
    return chapter.GuiItemCriteria(criteriaID, itemID, _xml.readString(xmlCtx, section, 'value'), _xml.readBool(xmlCtx, section, 'cached'))


def _readAction(xmlCtx, section, eventType, flags):
    actionID = parseID(xmlCtx, section, 'Specify a action ID')
    itemID = None
    if 'item-id' in section.keys():
        itemID = parseID(xmlCtx, section['item-id'], 'Specify a item ID')
    else:
        _xml.raiseWrongXml(xmlCtx, section.name, 'Specify a item ID')
    action = chapter.Action(eventType, itemID)
    action.setID(actionID)
    for _, effectSec in _xml.getChildren(xmlCtx, section, 'effects'):
        effect = _parseEffect(xmlCtx, effectSec, flags)
        if effect is not None:
            action.addEffect(effect)

    return action


def _readClickAction(xmlCtx, section, flags):
    return _readAction(xmlCtx, section, GUI_EVENT_TYPE.CLICK, flags)


def _readClickOutsideAction(xmlCtx, section, flags):
    return _readAction(xmlCtx, section, GUI_EVENT_TYPE.CLICK_OUTSIDE, flags)


def _readEscapeAction(xmlCtx, section, flags):
    return _readAction(xmlCtx, section, GUI_EVENT_TYPE.ESC, flags)


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
    return chapter.GameAttribute(attributeID, name, varID, args)


_BASE_ENTITY_PARERS = {'dialog': _parseDialog,
 'window': _parseWindow,
 'simple-window': _parseSimpleWindow,
 'message': _parseMessage,
 'player-cmd': _readPlayerCommand,
 'query': _readQuery,
 'gui-item-criteria': _readGuiItemCriteria,
 'click-action': _readClickAction,
 'click-outside-action': _readClickOutsideAction,
 'esc-action': _readEscapeAction,
 'game-attribute': _readGameAttribute}
_ENTITY_PARERS = _BASE_ENTITY_PARERS.copy()

def setEntitiesParsers(parsers):
    global _ENTITY_PARERS
    global _BASE_ENTITY_PARERS
    _ENTITY_PARERS.clear()
    _ENTITY_PARERS = _BASE_ENTITY_PARERS.copy()
    _ENTITY_PARERS.update(parsers)


def parseEntity(xmlCtx, name, section, flags):
    parser = _ENTITY_PARERS.get(name)
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
    return chapter.PopUp(windowID, windowType, content, varRef, forcedQuery=True)


_AVAILABLE_DIRECTIONS = ('L', 'T', 'R', 'B')
_ArrowProps = namedtuple('_ArrowProps', ('direction', 'loop'))
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
        sectionInfo['arrow'] = _ArrowProps(direction, _xml.readBool(xmlCtx, subSec, 'loop'))
    else:
        sectionInfo['arrow'] = None
    if 'padding' in tags:
        subSec = section['padding']
        sectionInfo['padding'] = _Padding(_xml.readFloat(xmlCtx, subSec, 'left'), _xml.readFloat(xmlCtx, subSec, 'top'), _xml.readFloat(xmlCtx, subSec, 'right'), _xml.readFloat(xmlCtx, subSec, 'bottom'))
    else:
        sectionInfo['padding'] = None
    sectionInfo['hasBox'] = section.readBool('has-box', True)
    return sectionInfo
