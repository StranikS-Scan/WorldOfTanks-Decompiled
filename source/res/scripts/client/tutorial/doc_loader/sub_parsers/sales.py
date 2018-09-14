# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/sales.py
from gui.shared.event_bus import EVENT_BUS_SCOPE
from items import _xml
from tutorial.data import chapter, effects
from tutorial.doc_loader import sub_parsers
from tutorial.doc_loader.sub_parsers import chains, readVarValue, parseID
from tutorial.doc_loader.sub_parsers import lobby

def readLoadViewDataSection(xmlCtx, section, flags):
    settingID = sub_parsers.parseID(xmlCtx, section, 'Specify a setting ID')
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


def _reaLoadViewSection(xmlCtx, section, _, conditions):
    viewID = parseID(xmlCtx, section, 'Specify a view ID')
    return effects.HasTargetEffect(viewID, effects.EFFECT_TYPE.LOAD_VIEW, conditions=conditions)


def init():
    sub_parsers.setEntitiesParsers({'hint': chains.readHintSection,
     'view-data': readLoadViewDataSection})
    sub_parsers.setEffectsParsers({'load-view': _reaLoadViewSection})
    sub_parsers.setTriggersParsers({'timer': lobby.readTimerTriggerSection})
