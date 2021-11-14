# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/bootcamp_lobby.py
from functools import partial
import resource_helper
from tutorial.doc_loader import sub_parsers
from tutorial.data import chapter, effects
from tutorial.data.conditions import Conditions, ComponentOnSceneCondition, CONDITION_STATE as _COND_STATE
from tutorial.data.bootcamp.checkpoint import Checkpoint
from tutorial.data.bootcamp import effects as bc_effects
from tutorial.control.bootcamp.lobby import triggers as bc_triggers, conditions as bc_conditions
from tutorial.control import triggers
from items import _xml
from tutorial.data.effects import EFFECT_TYPE as _EFFECT_TYPE

def _fillValue(targetDict, xmlCtx, section, key, readFunc, default=None, **kwargs):
    val = readFunc(xmlCtx, section, key, **kwargs)
    if val is None:
        val = default
    targetDict[key] = val
    return val


def _readBootcampMessageDialogSection(xmlCtx, section, _, dialogID, dialogType, content):
    content['sequence'] = [ _readMessageDialogSequenceItem(xmlCtx, messageSec) for _, messageSec in _xml.getChildren(xmlCtx, section, 'sequence') ]
    return chapter.PopUp(dialogID, dialogType, content, varRef=None, forcedQuery=True)


def _readMessageDialogSequenceItem(xmlCtx, section):
    messageContent = {}
    nations = _xml.getChildren(xmlCtx, section, 'nations', False)
    if nations:
        nationsDataDict = messageContent['nations_data'] = {}
        for _, subSec in nations:
            nationID, data = _readMessageDialogData(xmlCtx, subSec, True)
            nationsDataDict[nationID] = data

    else:
        subSec = _xml.getSubsection(xmlCtx, section, 'data')
        _, messageContent['data'] = _readMessageDialogData(xmlCtx, subSec, False)
    return messageContent


def _readSequenceItem(ctx, sec, fields):
    messageContent = {'data': {}}
    if fields:
        subSec = _xml.getSubsection(ctx, sec, 'data')
        for field in fields:
            _fillValue(messageContent['data'], ctx, subSec, field, _xml.readStringOrNone, default='')

    return messageContent


def _readSubtitleWindowSection(xmlCtx, section, _, windowID, windowType, content):
    fields = ('subtitle', 'voiceover')
    content['sequence'] = [ _readSequenceItem(xmlCtx, messageSec, fields) for _, messageSec in _xml.getChildren(xmlCtx, section, 'sequence') ]
    return chapter.PopUp(windowID, windowType, content, varRef=None, forcedQuery=True)


def _readVideoWindowSection(xmlCtx, section, _, windowID, windowType, content):
    fields = ('subtitle', 'video-path', 'event-start', 'event-stop', 'event-pause', 'event-resume', 'event-loop', 'video-fit-to-screen')
    content['sequence'] = [ _readSequenceItem(xmlCtx, messageSec, fields) for _, messageSec in _xml.getChildren(xmlCtx, section, 'sequence') ]
    return chapter.PopUp(windowID, windowType, content, varRef=None, forcedQuery=True)


def _readMessageDialogData(xmlCtx, section, isNation):
    nationID = _xml.readString(xmlCtx, section, 'nation_id') if isNation else None
    data = {}
    _fillValue(data, xmlCtx, section, 'preset', _xml.readString)
    _fillValue(data, xmlCtx, section, 'icon', _xml.readStringOrNone, default='')
    _fillValue(data, xmlCtx, section, 'label', _xml.readStringOrNone, default='')
    _fillValue(data, xmlCtx, section, 'label_first_bootcamp', partial(_xml.readStringOrNone))
    _fillValue(data, xmlCtx, section, 'text', _xml.readStringOrNone, default='')
    _fillValue(data, xmlCtx, section, 'subtitle', _xml.readStringOrNone, default='')
    _fillValue(data, xmlCtx, section, 'voiceover', _xml.readStringOrNone, default='')
    _fillValue(data, xmlCtx, section, 'description', _xml.readStringOrNone, default='')
    _fillValue(data, xmlCtx, section, 'background', _xml.readStringOrNone, default='')
    _fillValue(data, xmlCtx, section, 'only_first_bootcamp_bottom', partial(_xml.readBool, default=False))
    bottomRenderer = _fillValue(data, xmlCtx, section, 'bottom_renderer', _xml.readStringOrNone, default='')
    bottomDataList = data['bottom'] = []
    if bottomRenderer:
        for name, dataSection in _xml.getChildren(xmlCtx, section, 'bottom'):
            if name == 'data':
                bottomData = {}
                _fillValue(bottomData, xmlCtx, dataSection, 'icon', _xml.readStringOrNone, default='')
                _fillValue(bottomData, xmlCtx, dataSection, 'label', _xml.readStringOrNone, default='')
                _fillValue(bottomData, xmlCtx, dataSection, 'label_format', _xml.readStringOrNone, default='')
                _fillValue(bottomData, xmlCtx, dataSection, 'description', _xml.readStringOrNone, default='')
                _fillValue(bottomData, xmlCtx, dataSection, 'iconTooltip', _xml.readStringOrNone, default='')
                _fillValue(bottomData, xmlCtx, dataSection, 'labelTooltip', _xml.readStringOrNone, default='')
                _fillValue(bottomData, xmlCtx, dataSection, 'animationTarget', _xml.readStringOrNone, default='')
                _fillValue(bottomData, xmlCtx, dataSection, 'animationType', _xml.readStringOrNone, default='')
                bottomDataList.append(bottomData)

    return (nationID, data)


def _readBootcampSelectNationDialogSection(xmlCtx, section, _, dialogID, dialogType, content):
    content['resultVarID'] = _xml.readString(xmlCtx, section, 'result-var')
    return _readBootcampMessageDialogSection(xmlCtx, section, _, dialogID, dialogType, content)


def _readCheckpointSection(xmlCtx, section, flags):
    checkpointID = sub_parsers.parseID(xmlCtx, section, 'missing checkpoint ID')
    checkpointConditions = sub_parsers.readConditions(xmlCtx, _xml.getSubsection(xmlCtx, section, 'condition'), flags)
    checkpointEffects = [ effect for effect in (sub_parsers._parseEffect(xmlCtx, effectSec, flags) for _, effectSec in _xml.getChildren(xmlCtx, section, 'effects')) if effect is not None ]
    return Checkpoint(checkpointID, checkpointConditions, checkpointEffects)


def _readLinearCheckpointControllerTriggerSection(xmlCtx, section, _, triggerID):
    checkpointsSequence = [ sub_parsers.parseID(xmlCtx, subSec, 'missing checkpoint ID in sequence') for _, subSec in _xml.getChildren(xmlCtx, section, 'sequence') ]
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, bc_triggers.LinearCheckpointControllerTrigger, checkpointsSequence=checkpointsSequence)


def _makeSimpleValidateVarTriggerReader(clazz):
    return lambda xmlCtx, section, _, triggerID: sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, clazz)


def _readCheckpointReachedCondition(xmlCtx, section, state):
    checkpointID = sub_parsers.parseID(xmlCtx, section, 'missing checkpoint ID in condition')
    return bc_conditions.CheckpointReachedCondition(checkpointID, state=state)


def _readRequestExclusiveHintEffectSection(xmlCtx, section, _, conditions):
    componentID = sub_parsers.parseID(xmlCtx, section, 'missing hint target component ID')
    soundID = _xml.readStringOrNone(xmlCtx, section, 'sound')
    if soundID is None:
        soundID = 'bc_new_ui_element_button'
    if conditions is None:
        conditions = Conditions()
    conditions.insert(0, ComponentOnSceneCondition(componentID))
    return bc_effects.RequestExclusiveHintEffect(componentID, soundID, conditions=conditions)


def _readStartPlanSection(xmlCtx, section, _, conditions):
    item = resource_helper.readStringItem(resource_helper.ResourceCtx(xmlCtx[1]), _xml.getSubsection(xmlCtx, section, 'plan'))
    planName = item.value
    return bc_effects.StartVSEPlanEffect(planName, conditions=conditions)


def _readSetBootcampNationEffectSection(xmlCtx, section, _, conditions):
    varID = sub_parsers.parseID(xmlCtx, section, 'missing selected nation variable ID')
    return effects.HasTargetEffect(varID, _EFFECT_TYPE.SAVE_ACCOUNT_SETTING, conditions=conditions)


def init():
    sub_parsers.setEffectsParsers({'request-exclusive-hint': _readRequestExclusiveHintEffectSection,
     'update-exclusive-hints': sub_parsers.makeSimpleEffectReader(_EFFECT_TYPE.UPDATE_EXCLUSIVE_HINTS),
     'start-vse-plan': _readStartPlanSection,
     'restore-checkpoint': sub_parsers.makeSimpleEffectReader(_EFFECT_TYPE.RESTORE_CHECKPOINT),
     'save-checkpoint': sub_parsers.makeSimpleEffectReader(_EFFECT_TYPE.SAVE_CHECKPOINT),
     'set-bootcamp-nation': _readSetBootcampNationEffectSection,
     'play-final-video': sub_parsers.makeSimpleEffectReader(_EFFECT_TYPE.PLAY_VIDEO),
     'show-demo-acc-renaming': sub_parsers.makeSimpleEffectReader(_EFFECT_TYPE.SHOW_DEMO_ACCOUNT_RENAMING)})
    sub_parsers.setEntitiesParsers({'checkpoint': _readCheckpointSection})
    sub_parsers.setTriggersParsers({'linear-checkpoint-controller': _readLinearCheckpointControllerTriggerSection,
     'current-vehicle-changed': _makeSimpleValidateVarTriggerReader(triggers.CurrentVehicleChangedTrigger),
     'items-cache-sync': _makeSimpleValidateVarTriggerReader(triggers.ItemsCacheSyncTrigger)})
    sub_parsers.setDialogsParsers({'bootcampMessage': _readBootcampMessageDialogSection,
     'bootcampSelectNation': _readBootcampSelectNationDialogSection,
     'bootcampVideo': _readVideoWindowSection})
    sub_parsers.setConditionsParsers({'checkpoint-reached': lambda xmlCtx, section, flags: _readCheckpointReachedCondition(xmlCtx, section, _COND_STATE.ACTIVE),
     'checkpoint-not-reached': lambda xmlCtx, section, flags: _readCheckpointReachedCondition(xmlCtx, section, ~_COND_STATE.ACTIVE)})
    sub_parsers.setWindowsParsers({'bootcampSubtitle': _readSubtitleWindowSection})
