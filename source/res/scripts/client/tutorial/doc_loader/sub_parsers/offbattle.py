# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/offbattle.py
from helpers.html import translation
from items import _xml
from tutorial.control.offbattle import triggers
from tutorial.data import chapter
from tutorial.doc_loader import sub_parsers
from tutorial.doc_loader.sub_parsers import lobby

def _readRequestAllBonusesEffectSection(xmlCtx, section, _, conditions):
    return chapter.SimpleEffect(chapter.Effect.REQUEST_ALL_BONUSES, conditions=conditions)


def _readEnterQueueEffectSection(xmlCtx, section, flags, conditions):
    flagID = sub_parsers._parseID(xmlCtx, section, 'Specify a flag ID')
    if flagID not in flags:
        flags.append(flagID)
    return chapter.HasTargetEffect(flagID, chapter.Effect.ENTER_QUEUE, conditions=conditions)


def _readExitQueueEffectSection(xmlCtx, section, flags, conditions):
    flagID = sub_parsers._parseID(xmlCtx, section, 'Specify a flag ID')
    if flagID not in flags:
        flags.append(flagID)
    return chapter.HasTargetEffect(flagID, chapter.Effect.EXIT_QUEUE, conditions=conditions)


def _readQueueTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.TutorialQueueTrigger(triggerID, _xml.readString(xmlCtx, section, 'pop-up'))


def _readAllBonusesTriggerSection(xmlCtx, section, chapter, triggerID):
    return triggers.AllBonusesTrigger(triggerID, _xml.readString(xmlCtx, section, 'set-var'))


def _readGreetingDialogSection(xmlCtx, section, _, dialogID, dialogType, content):
    content['timeNoteValue'] = translation(_xml.readString(xmlCtx, section, 'time-note'))
    return chapter.VarRefPopUp(dialogID, dialogType, content, None)


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
    return chapter.VarRefPopUp(dialogID, dialogType, content, _xml.readString(xmlCtx, section, 'var-ref'))


def _readVideoDialogSection(xmlCtx, section, _, dialogID, dialogType, content):
    return chapter.VarRefPopUp(dialogID, dialogType, content, None)


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
    return chapter.VarRefPopUp(windowID, windowType, content, _xml.readString(xmlCtx, section, 'var-ref'))


def _readNoResultsWindowSection(xmlCtx, section, _, windowID, windowType, content):
    content['text'] = translation(_xml.readString(xmlCtx, section, 'text'))
    return chapter.PopUp(windowID, windowType, content)


def init():
    sub_parsers.setEffectsParsers({'request-all-bonuses': _readRequestAllBonusesEffectSection,
     'enter-queue': _readEnterQueueEffectSection,
     'exit-queue': _readExitQueueEffectSection})
    sub_parsers.setTriggersParsers({'bonus': lobby._readBonusTriggerSection,
     'allBonuses': _readAllBonusesTriggerSection,
     'queue': _readQueueTriggerSection})
    sub_parsers.setDialogsParsers({'greeting': _readGreetingDialogSection,
     'queue': _readQueueDialogSection,
     'video': _readVideoDialogSection})
    sub_parsers.setWindowsParsers({'final': _readFinalWindowSection,
     'noResults': _readNoResultsWindowSection})
