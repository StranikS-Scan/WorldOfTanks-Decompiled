# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/sales.py
from gui.shared.event_bus import EVENT_BUS_SCOPE
from items import _xml
from tutorial.control.sales import triggers
from tutorial.data import chapter, effects
from tutorial.doc_loader import sub_parsers
from tutorial.doc_loader.sub_parsers import readVarValue, parseID

def readLoadViewDataSection(xmlCtx, section, flags):
    settingID = parseID(xmlCtx, section, 'Specify a setting ID')
    alias = None
    if 'alias' in section.keys():
        alias = _xml.readString(xmlCtx, section, 'alias')
    else:
        _xml.raiseWrongXml(xmlCtx, section.name, 'Specify a setting name')
    scope = EVENT_BUS_SCOPE.DEFAULT
    if 'scope' in section.keys():
        scope = _xml.readInt(xmlCtx, section, 'scope')
    else:
        _xml.raiseWrongXml(xmlCtx, section.name, 'Specify a setting value')
    ctx = None
    if 'context' in section.keys():
        ctx = readVarValue('asDict', section['context'])
    return chapter.LoadViewData(settingID, alias, scope, ctx)


def readIsCollectibleVehicleTrigger(_, __, ___, triggerID):
    return triggers.IsCollectibleVehicleTrigger(triggerID)


def readTimerTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.TimerTrigger)


def readHintSection(xmlCtx, section, flags):
    sectionInfo = sub_parsers.parseHint(xmlCtx, section)
    hint = chapter.ChainHint(sectionInfo['hintID'], sectionInfo['itemID'], sectionInfo['text'], sectionInfo['hasBox'], sectionInfo['arrow'], sectionInfo['padding'], sectionInfo['hideImmediately'])
    hint.setActions(sub_parsers.parseActions(xmlCtx, _xml.getSubsection(xmlCtx, section, 'actions'), flags))
    return hint


def _reaLoadViewSection(xmlCtx, section, _, conditions):
    viewID = parseID(xmlCtx, section, 'Specify a view ID')
    return effects.HasTargetEffect(viewID, effects.EFFECT_TYPE.LOAD_VIEW, conditions=conditions)


def init():
    sub_parsers.setEntitiesParsers({'hint': readHintSection,
     'view-data': readLoadViewDataSection})
    sub_parsers.setEffectsParsers({'load-view': _reaLoadViewSection})
    sub_parsers.setTriggersParsers({'timer': readTimerTriggerSection,
     'isCollectibleVehicle': readIsCollectibleVehicleTrigger})
