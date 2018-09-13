# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/__init__.py
from items import _xml, vehicles
from helpers.html import translation
import nations
from tutorial.data import chapter
from tutorial.logger import LOG_ERROR

def _parseID(xmlCtx, section, msg):
    entityID = section.asString
    if entityID is None or not len(entityID):
        _xml.raiseWrongXml(xmlCtx, section.name, msg)
    return entityID


def _readFlagCondition(xmlCtx, section, state, flags):
    flagID = _parseID(xmlCtx, section, 'Specify a flag ID')
    if flagID not in flags:
        flags.append(flagID)
    return chapter.FlagCondition(flagID, state=state)


def _readGlobalFlagCondition(xmlCtx, section, state):
    flagID = _parseID(xmlCtx, section, 'Specify a flag ID')
    return chapter.FlagCondition(flagID, state=state, condType=chapter.Condition.GLOBAL_FLAG_CONDITION)


def _readWindowOnSceneCondition(xmlCtx, section, state):
    flagID = _parseID(xmlCtx, section, 'Specify a window ID')
    return chapter.FlagCondition(flagID, state=state, condType=chapter.Condition.WINDOW_ON_SCENE_CONDITION)


def _readVehicleCondition(xmlCtx, section, varID):
    value = _parseID(xmlCtx, section, 'Specify a vehicle var value')
    return chapter.VehicleCondition(varID, value)


CONDITION_TAGS = {'active': lambda xmlCtx, section, flags: _readFlagCondition(xmlCtx, section, chapter.FlagCondition.FLAG_ACTIVE, flags),
 'inactive': lambda xmlCtx, section, flags: _readFlagCondition(xmlCtx, section, chapter.FlagCondition.FLAG_INACTIVE, flags),
 'global-active': lambda xmlCtx, section, flags: _readGlobalFlagCondition(xmlCtx, section, chapter.FlagCondition.FLAG_ACTIVE),
 'global-inactive': lambda xmlCtx, section, flags: _readGlobalFlagCondition(xmlCtx, section, chapter.FlagCondition.FLAG_INACTIVE),
 'is-widow-opened': lambda xmlCtx, section, flags: _readWindowOnSceneCondition(xmlCtx, section, chapter.FlagCondition.FLAG_ACTIVE),
 'is-widow-closed': lambda xmlCtx, section, flags: _readWindowOnSceneCondition(xmlCtx, section, chapter.FlagCondition.FLAG_INACTIVE),
 'cveh-type-name': lambda xmlCtx, section, _: _readVehicleCondition(xmlCtx, section, chapter.VehicleCondition.CV_TYPE_NAME)}

def _readConditions(xmlCtx, section, flags):
    result = chapter.Conditions()
    for name, subSec in section.items():
        if name == 'either':
            eitherCondition = _readConditions(xmlCtx, subSec, flags)
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
        return _readConditions(xmlCtx, condSec, flags)
    else:
        return


ACTION_TAGS = {'press': chapter.Action.PRESS,
 'click': chapter.Action.CLICK,
 'click-point': chapter.Action.CLICK_POINT,
 'close': chapter.Action.CLOSE,
 'change': chapter.Action.CHANGE,
 'click-item': chapter.Action.CLICK_ITEM,
 'press-item': chapter.Action.PRESS_ITEM,
 'change-text': chapter.Action.CHANGE_TEXT}

def _parseActions(xmlCtx, section, flags):
    result = []
    for name, subSec in section.items():
        actionType = ACTION_TAGS.get(name)
        if actionType is None:
            LOG_ERROR('Action is not supported: ', name)
            continue
        targetID = _parseID(xmlCtx, subSec, 'Specify a target ID')
        action = chapter.Action(actionType, targetID)
        if 'effects' in subSec.keys():
            for _, effectSec in _xml.getChildren(xmlCtx, subSec, 'effects'):
                effect = _parseEffect(xmlCtx, effectSec, flags)
                if effect is not None:
                    action.addEffect(effect)

        result.append(action)

    return result


def _readActivateEffectSection(xmlCtx, section, flags, conditions):
    flagID = _parseID(xmlCtx, section, 'Specify a flag ID')
    if flagID not in flags:
        flags.append(flagID)
    return chapter.HasTargetEffect(flagID, chapter.Effect.ACTIVATE, conditions=conditions)


def _readDeactivateEffectSection(xmlCtx, section, flags, conditions):
    flagID = _parseID(xmlCtx, section, 'Specify a flag ID')
    if flagID not in flags:
        flags.append(flagID)
    return chapter.HasTargetEffect(flagID, chapter.Effect.DEACTIVATE, conditions=conditions)


def _readGlobalActivateEffectSection(xmlCtx, section, flags, conditions):
    flagID = _parseID(xmlCtx, section, 'Specify a flag ID')
    return chapter.HasTargetEffect(flagID, chapter.Effect.GLOBAL_ACTIVATE, conditions=conditions)


def _readGlobalDeactivateEffectSection(xmlCtx, section, flags, conditions):
    flagID = _parseID(xmlCtx, section, 'Specify a flag ID')
    if flagID not in flags:
        flags.append(flagID)
    return chapter.HasTargetEffect(flagID, chapter.Effect.GLOBAL_DEACTIVATE, conditions=conditions)


def _readNextChapterEffectSection(xmlCtx, section, _, conditions):
    targetID = section.asString
    return chapter.HasTargetEffect(targetID, chapter.Effect.NEXT_CHAPTER, conditions=conditions)


def _readRunTriggerEffectSection(xmlCtx, section, _, conditions):
    triggerID = _parseID(xmlCtx, section, 'Specify a trigger ID')
    return chapter.HasTargetEffect(triggerID, chapter.Effect.RUN_TRIGGER, conditions=conditions)


def _readRequestBonusEffectSection(xmlCtx, section, _, conditions):
    chapterID = section.asString
    return chapter.HasTargetEffect(chapterID, chapter.Effect.REQUEST_BONUS, conditions=conditions)


def _readShowHintSection(xmlCtx, section, _, conditions):
    hintID = _parseID(xmlCtx, section, 'Specify a hint ID')
    return chapter.HasTargetEffect(hintID, chapter.Effect.SHOW_HINT, conditions=conditions)


def _readShowDialogSection(xmlCtx, section, _, conditions):
    dialogID = _parseID(xmlCtx, section, 'Specify a dialog ID')
    return chapter.HasTargetEffect(dialogID, chapter.Effect.SHOW_DIALOG, conditions=conditions)


def _readShowWindowSection(xmlCtx, section, _, conditions):
    windowID = _parseID(xmlCtx, section, 'Specify a window ID')
    return chapter.HasTargetEffect(windowID, chapter.Effect.SHOW_WINDOW, conditions=conditions)


def _readShowMessageSection(xmlCtx, section, _, conditions):
    messageID = _parseID(xmlCtx, section, 'Specify a message ID')
    return chapter.HasTargetEffect(messageID, chapter.Effect.SHOW_MESSAGE, conditions=conditions)


def _readPlayMusicSection(xmlCtx, section, _, conditions):
    messageID = _parseID(xmlCtx, section, 'Specify a music ID')
    return chapter.HasTargetEffect(messageID, chapter.Effect.PLAY_MUSIC, conditions=conditions)


def _readGuiItemDefinition(xmlCtx, section, _, conditions):
    newGuiItemId = _parseID(xmlCtx, section, 'Specify a new gui item ID')
    parentReferenceId = _xml.readString(xmlCtx, section, 'parent-ref')
    extraReferenceId = _xml.readString(xmlCtx, section, 'extra-ref')
    return chapter.DefineGuiItemEffect(newGuiItemId, chapter.Effect.DEFINE_GUI_ITEM, parentReferenceId, extraReferenceId, conditions=conditions)


def _readGuiItemPropertiesEffectSection(xmlCtx, section, _, conditions):
    itemID = _parseID(xmlCtx, section, 'Specify a item ID')
    props = {}
    for _, subSec in _xml.getChildren(xmlCtx, section, 'properties'):
        propType, propSec = subSec.items()[0]
        props[subSec.asString] = _readVarValue(propType, propSec)

    revert = section.readBool('revert')
    return chapter.SetGuiItemProperty(itemID, props, conditions=conditions, revert=revert)


def _readInvokeGuiCmdSection(xmlCtx, section, _, conditions):
    commandID = _parseID(xmlCtx, section, 'Specify a command ID')
    return chapter.HasTargetEffect(commandID, chapter.Effect.INVOKE_GUI_CMD, conditions=conditions)


def _readInvokePlayerCmdSection(xmlCtx, section, _, conditions):
    commandID = _parseID(xmlCtx, section, 'Specify a command ID')
    return chapter.HasTargetEffect(commandID, chapter.Effect.INVOKE_PLAYER_CMD, conditions=conditions)


_BASE_EFFECT_TAGS = {'activate': _readActivateEffectSection,
 'inactivate': _readDeactivateEffectSection,
 'global-activate': _readGlobalActivateEffectSection,
 'global-inactivate': _readGlobalDeactivateEffectSection,
 'refuse-training': lambda xmlCtx, section, flags, conditions: chapter.SimpleEffect(chapter.Effect.REFUSE_TRAINING, conditions=conditions),
 'next-chapter': _readNextChapterEffectSection,
 'run-trigger': _readRunTriggerEffectSection,
 'request-bonus': _readRequestBonusEffectSection,
 'set-gui-item-props': _readGuiItemPropertiesEffectSection,
 'finish-training': lambda xmlCtx, section, flags, conditions: chapter.SimpleEffect(chapter.Effect.FINISH_TRAINING, conditions=conditions),
 'define-gui-item': _readGuiItemDefinition,
 'invoke-gui-cmd': _readInvokeGuiCmdSection,
 'invoke-player-cmd': _readInvokePlayerCmdSection,
 'show-hint': _readShowHintSection,
 'show-dialog': _readShowDialogSection,
 'show-window': _readShowWindowSection,
 'show-message': _readShowMessageSection,
 'play-music': _readPlayMusicSection}
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

def _readValidateVarTriggerSection(xmlCtx, section, triggerID, clazz, **kwargs):
    validateVarID = _xml.readString(xmlCtx, section, 'validate-var')
    setVarID = section.readString('set-var')
    if not len(setVarID):
        setVarID = None
    return clazz(triggerID, validateVarID, setVarID=setVarID, **kwargs)


def setTriggersParsers(parsers):
    global _TRIGGER_SUB_PARSERS
    _TRIGGER_SUB_PARSERS.clear()
    _TRIGGER_SUB_PARSERS = parsers.copy()


def _parseTrigger(xmlCtx, section, flags, chapter):
    triggerID = _parseID(xmlCtx, section, 'Specify a trigger ID')
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


def _readPermanentGuiItemSection(xmlCtx, section, itemFlags, itemID, props, conditions):
    return chapter.PermanentGuiItemRef(itemID, props, conditions=conditions)


def _readDynamicGuiItemSection(xmlCtx, section, itemFlags, itemID, props, conditions):
    item = chapter.DynamicGuiItemRef(itemID, props, conditions=conditions)
    if 'find-criteria' in section.keys():
        subSec = _xml.getSubsection(xmlCtx, section, 'find-criteria')
        parentID = _xml.readString(xmlCtx, subSec, 'parent-ref')
        varPath = _xml.readString(xmlCtx, subSec, 'var-path')
        varRef = _xml.readString(xmlCtx, subSec, 'var-ref')
        item.setFindCriteria([parentID, varPath, varRef])
    for _, effectSec in _xml.getChildren(xmlCtx, section, 'not-on-scene-effects'):
        effect = _parseEffect(xmlCtx, effectSec, itemFlags)
        if effect is not None:
            item.addNotOnSceneEffect(effect)

    for _, effectSec in _xml.getChildren(xmlCtx, section, 'on-scene-effects'):
        effect = _parseEffect(xmlCtx, effectSec, itemFlags)
        if effect is not None:
            item.addOnSceneEffect(effect)

    return item


GUI_ITEMS_SUB_PARSERS = {'permanent': _readPermanentGuiItemSection,
 'dynamic': _readDynamicGuiItemSection}

def _parseGuiItem(xmlCtx, section, flags, itemFlags):
    itemID = _parseID(xmlCtx, section, 'Specify a GUI item ID')
    lifeCycle = _xml.readString(xmlCtx, section, 'life-cycle')
    parser = GUI_ITEMS_SUB_PARSERS.get(lifeCycle)
    item = None
    if parser is not None:
        props = {}
        if 'properties' in section.keys():
            for _, subSec in _xml.getChildren(xmlCtx, section, 'properties'):
                propType, propSec = subSec.items()[0]
                props[subSec.asString] = _readVarValue(propType, propSec)

        item = parser(xmlCtx, section, itemFlags, itemID, props, _parseConditions(xmlCtx, section, flags))
    else:
        LOG_ERROR('Gui item is not supported:', lifeCycle)
    return item


def _readAsStringSection(name, section):
    return translation(getattr(section, name))


def _readAsListSection(_, section):
    value = []
    for name, subSec in section.items():
        if name == 'condition':
            continue
        value.append(_readVarValue(name, subSec))

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


CUSTOM_VARS_PARERS = {'asString': _readAsStringSection,
 'asList': _readAsListSection,
 'asIntSequence': _readAsIntSequence,
 'asVehTypeName': _readAsVehTypeNameSection,
 'asVehChassisName': lambda name, section: _readAsVehItemNameSection('vehicleChassis', 'chassisIDs', section),
 'asVehGunName': lambda name, section: _readAsVehItemNameSection('vehicleGun', 'gunIDs', section),
 'asVehEngineName': lambda name, section: _readAsVehItemNameSection('vehicleEngine', 'engineIDs', section),
 'asVehRadioName': lambda name, section: _readAsVehItemNameSection('vehicleRadio', 'radioIDs', section),
 'asVehTurretName': lambda name, section: _readAsVehItemNameSection('vehicleTurret', 'turretIDs', section),
 'asEquipment': _readAsEquipmentSection}

def _readVarValue(name, section):
    if name in CUSTOM_VARS_PARERS:
        value = CUSTOM_VARS_PARERS[name](name, section)
    else:
        value = getattr(section, name)
    return value


def _parseVarSet(xmlCtx, section, flags):
    varID = _parseID(xmlCtx, section, 'Specify a var ID')
    varSet = []
    for name, subSec in section.items():
        value = _readVarValue(name, subSec)
        varSet.append((value, _parseConditions(xmlCtx, subSec, flags)))

    return chapter.VarSet(varID, varSet)


_DIALOG_SUB_PARERS = {}

def setDialogsParsers(parsers):
    global _DIALOG_SUB_PARERS
    _DIALOG_SUB_PARERS.clear()
    _DIALOG_SUB_PARERS = parsers.copy()


def _parseDialog(xmlCtx, section, flags):
    dialogID = _parseID(xmlCtx, section, 'Specify a dialog ID')
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
    dialog.setActions(_parseActions(xmlCtx, _xml.getSubsection(xmlCtx, section, 'actions'), flags))
    return dialog


_WINDOW_SUB_PARERS = {}

def setWindowsParsers(parsers):
    global _WINDOW_SUB_PARERS
    _WINDOW_SUB_PARERS.clear()
    _WINDOW_SUB_PARERS = parsers.copy()


def _parseWindow(xmlCtx, section, flags):
    windowID = _parseID(xmlCtx, section, 'Specify a window ID')
    windowType = _xml.readString(xmlCtx, section, 'type')
    bSec = _xml.getSubsection(xmlCtx, section, 'buttons')
    content = {'closeID': _xml.readString(xmlCtx, bSec, 'close')}
    parser = _WINDOW_SUB_PARERS.get(windowType)
    if parser is not None:
        window = parser(xmlCtx, section, flags, windowID, windowType, content)
        window.setActions(_parseActions(xmlCtx, _xml.getSubsection(xmlCtx, section, 'actions'), flags))
    else:
        window = None
        LOG_ERROR('Type of window is not supported: ', windowType)
    return window


def _parseMessage(xmlCtx, section, _):
    messageID = _parseID(xmlCtx, section, 'Specify a message ID')
    guiType = _xml.readString(xmlCtx, section, 'type')
    text = translation(_xml.readString(xmlCtx, section, 'text'))
    return chapter.Message(messageID, guiType, text)


def _readPlayerCommand(xmlCtx, section, _):
    cmdID = _parseID(xmlCtx, section, 'Specify a player command ID')
    name = _xml.readString(xmlCtx, section, 'name')
    argsSec = _xml.getChildren(xmlCtx, section, 'args')
    kwargsSec = _xml.getChildren(xmlCtx, section, 'kwargs')
    cmdArgs = []
    for name, argSec in argsSec:
        cmdArgs.append(_readVarValue(name, argSec))

    cmdKwargs = {}
    for name, kwargSec in kwargsSec:
        argType, subSec = kwargSec.items()[0]
        cmdKwargs[name] = _readVarValue(argType, subSec)

    return chapter.PlayerCommand(cmdID, name, cmdArgs=tuple(cmdArgs), cmdKwargs=cmdKwargs)


def _readQuery(xmlCtx, section, _):
    queryID = _parseID(xmlCtx, section, 'Specify a query ID')
    return chapter.Query(queryID, _xml.readString(xmlCtx, section, 'type'), _xml.readString(xmlCtx, section, 'var-ref'), extra=section.readString('extra'))


_BASE_ENTITY_PARERS = {'dialog': _parseDialog,
 'window': _parseWindow,
 'message': _parseMessage,
 'player-cmd': _readPlayerCommand,
 'query': _readQuery}
_ENTITY_PARERS = _BASE_ENTITY_PARERS.copy()

def setEntitiesParsers(parsers):
    global _ENTITY_PARERS
    global _BASE_ENTITY_PARERS
    _ENTITY_PARERS.clear()
    _ENTITY_PARERS = _BASE_ENTITY_PARERS.copy()
    _ENTITY_PARERS.update(parsers)


def _parseEntity(xmlCtx, name, section, flags):
    parser = _ENTITY_PARERS.get(name)
    item = None
    if parser is not None:
        item = parser(xmlCtx, section, flags)
    else:
        LOG_ERROR('Entity is not supported:', name)
    return item


def _readBonusValues(section):
    result = {}
    valuesSec = section['values']
    if valuesSec is not None:
        for name, bonusSection in valuesSec.items():
            valueType, valueSec = bonusSection.items()[0]
            result[name] = _readVarValue(valueType, valueSec)

    return result
