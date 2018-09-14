# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/offbattle.py
from helpers.html import translation
from items import _xml
from tutorial.control.offbattle import triggers
from tutorial.data import chapter
from tutorial.data import effects
from tutorial.doc_loader import sub_parsers
from tutorial.doc_loader.sub_parsers import lobby
_EFFECT_TYPE = effects.EFFECT_TYPE

def _readRequestAllBonusesEffectSection(xmlCtx, section, _, conditions):
    return effects.SimpleEffect(_EFFECT_TYPE.REQUEST_ALL_BONUSES, conditions=conditions)


def _readEnterQueueEffectSection(xmlCtx, section, flags, conditions):
    flagID = sub_parsers.parseID(xmlCtx, section, 'Specify a flag ID')
    if flagID not in flags:
        flags.append(flagID)
    return effects.HasTargetEffect(flagID, _EFFECT_TYPE.ENTER_QUEUE, conditions=conditions)


def _readExitQueueEffectSection(xmlCtx, section, flags, conditions):
    flagID = sub_parsers.parseID(xmlCtx, section, 'Specify a flag ID')
    if flagID not in flags:
        flags.append(flagID)
    return effects.HasTargetEffect(flagID, _EFFECT_TYPE.EXIT_QUEUE, conditions=conditions)


def _readInternalBrowserSection(xmlCtx, section, flags, conditions):
    flagID = sub_parsers.parseID(xmlCtx, section, 'Specify a flag ID')
    if flagID not in flags:
        flags.append(flagID)
    return effects.HasTargetEffect(flagID, _EFFECT_TYPE.OPEN_INTERNAL_BROWSER, conditions=conditions)


def _readQueueTriggerSection(xmlCtx, section, _, triggerID):
    return triggers.TutorialQueueTrigger(triggerID, _xml.readString(xmlCtx, section, 'pop-up'))


def _readAllBonusesTriggerSection(xmlCtx, section, _, triggerID):
    return triggers.AllBonusesTrigger(triggerID, _xml.readString(xmlCtx, section, 'set-var'))


def _readGreetingDialogSection(xmlCtx, section, _, dialogID, dialogType, content):
    content['timeNoteValue'] = translation(_xml.readString(xmlCtx, section, 'time-note'))
    return chapter.PopUp(dialogID, dialogType, content, None, forcedQuery=True)


def _readQueueDialogSection(xmlCtx, section, _, dialogID, dialogType, content):
    content['avgTimeTextFormat'] = translation(_xml.readString(xmlCtx, section, 'avg-time-text'))
    subSec = _xml.getSubsection(xmlCtx, section, 'player-time-text')
    content['playerTimeTextStart'] = translation(_xml.readString(xmlCtx, subSec, 'start'))
    content['playerTimeTextEnd'] = translation(_xml.readString(xmlCtx, subSec, 'end'))
    pointcuts = []
    for _, subSec in _xml.getChildren(xmlCtx, section, 'time-pointcuts'):
        value = subSec.asFloat
        if value > 0:
            pointcuts.append(subSec.asInt)

    if len(pointcuts) < 2:
        _xml.raiseWrongSection(xmlCtx, 'time-pointcuts: should be the minimum and maximum value')
    content['timePointcuts'] = sorted(pointcuts)
    return chapter.PopUp(dialogID, dialogType, content, _xml.readString(xmlCtx, section, 'var-ref'))


def _readConfirmRefuseDialogSection(xmlCtx, section, _, dialogID, dialogType, content):
    content['checkBoxLabel'] = translation(_xml.readString(xmlCtx, section, 'checkbox-label'))
    return chapter.PopUp(dialogID, dialogType, content)


def _readFinalWindowSection(xmlCtx, section, _, windowID, windowType, content):
    bSec = _xml.getSubsection(xmlCtx, section, 'buttons')
    content['restartID'] = _xml.readString(xmlCtx, bSec, 'restart')
    content['showVideoID'] = _xml.readString(xmlCtx, bSec, 'show-video')
    content['imageUrl'] = section.readString('image')
    hintsSec = _xml.getSubsection(xmlCtx, section, 'battle-hints')
    hints = []
    for typeName, hintSec in hintsSec.items():
        if len(hintSec.keys()):
            data = {'type': typeName}
            for key, subSec in hintSec.items():
                data[key] = translation(subSec.asString)

            hints.append(data)
        else:
            hints.append({'type': typeName,
             'label': translation(hintSec.asString)})

    content['battleHints'] = hints
    content['restartHint'] = translation(_xml.readString(xmlCtx, section, 'restart-hint'))
    return chapter.PopUp(windowID, windowType, content, _xml.readString(xmlCtx, section, 'var-ref'))


def _readNoResultsWindowSection(xmlCtx, section, _, windowID, windowType, content):
    content['text'] = translation(_xml.readString(xmlCtx, section, 'text'))
    return chapter.PopUp(windowID, windowType, content)


def init():
    sub_parsers.setEffectsParsers({'request-all-bonuses': _readRequestAllBonusesEffectSection,
     'enter-queue': _readEnterQueueEffectSection,
     'exit-queue': _readExitQueueEffectSection,
     'open-internal-browser': _readInternalBrowserSection})
    sub_parsers.setTriggersParsers({'bonus': lobby.readBonusTriggerSection,
     'allBonuses': _readAllBonusesTriggerSection,
     'queue': _readQueueTriggerSection})
    sub_parsers.setDialogsParsers({'greeting': _readGreetingDialogSection,
     'queue': _readQueueDialogSection,
     'confirmRefuse': _readConfirmRefuseDialogSection})
    sub_parsers.setWindowsParsers({'final': _readFinalWindowSection,
     'noResults': _readNoResultsWindowSection})
