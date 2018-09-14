# Embedded file name: scripts/client/tutorial/doc_loader/sub_parsers/battle.py
from helpers.html import translation
from items import _xml
from tutorial.data import chapter
from tutorial.data import effects
from tutorial.doc_loader import sub_parsers
from tutorial.control.battle import triggers
from tutorial.logger import LOG_ERROR
import FMOD
_EFFECT_TYPE = effects.EFFECT_TYPE

def _readShowMarkerSection(xmlCtx, section, _, conditions):
    markerID = sub_parsers.parseID(xmlCtx, section, 'Specify a marker ID')
    return effects.HasTargetEffect(markerID, _EFFECT_TYPE.SHOW_MARKER, conditions=conditions)


def _readRemoveMarkerSection(xmlCtx, section, _, conditions):
    markerID = sub_parsers.parseID(xmlCtx, section, 'Specify a marker ID')
    return effects.HasTargetEffect(markerID, _EFFECT_TYPE.REMOVE_MARKER, conditions=conditions)


def _readNextTaskSection(xmlCtx, section, _, conditions):
    taskID = sub_parsers.parseID(xmlCtx, section, 'Specify a next task ID')
    return effects.HasTargetEffect(taskID, _EFFECT_TYPE.NEXT_TASK, conditions=conditions)


def _readTeleportSection(xmlCtx, section, _, conditions):
    pointID = sub_parsers.parseID(xmlCtx, section, 'Specify a point ID')
    return effects.HasTargetEffect(pointID, _EFFECT_TYPE.TELEPORT, conditions=conditions)


def _readShowGreetingSection(xmlCtx, section, _, conditions):
    greetingID = sub_parsers.parseID(xmlCtx, section, 'Specify a greeting ID')
    return effects.HasTargetEffect(greetingID, _EFFECT_TYPE.SHOW_GREETING, conditions=conditions)


def _readEnableCameraZoom(xmlCtx, section, _, conditions):
    return effects.SimpleEffect(_EFFECT_TYPE.ENABLE_CAMERA_ZOOM, conditions=conditions)


def _readDisableCameraZoom(xmlCtx, section, _, conditions):
    return effects.SimpleEffect(_EFFECT_TYPE.DISABLE_CAMERA_ZOOM, conditions=conditions)


def _readDispatcherTriggerSection(xmlCtx, section, _, triggerID):
    triggerIDs = set()
    for _, subSec in _xml.getChildren(xmlCtx, section, 'includes'):
        triggerIDs.add(sub_parsers.parseID(xmlCtx, subSec, 'Specify a trigger ID'))

    return triggers.TriggersDispatcher(triggerID, triggerIDs)


def _readDispatchableTriggerSection(xmlCtx, section, triggerID, clazz, **kwargs):
    stateFlagID = section.readString('init-state-flag')
    if not len(stateFlagID):
        stateFlagID = None
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, clazz, stateFlagID=stateFlagID, **kwargs)


def _readAimTriggerSection(xmlCtx, section, _, triggerID):
    return _readDispatchableTriggerSection(xmlCtx, section, triggerID, triggers.ObjectAIMTrigger)


def _readAreaTriggerSection(xmlCtx, section, _, triggerID):
    return _readDispatchableTriggerSection(xmlCtx, section, triggerID, triggers.AreaTrigger)


def _readVehicleOnArenaTriggerSection(xmlCtx, section, _, triggerID):
    return sub_parsers.readValidateVarTriggerSection(xmlCtx, section, triggerID, triggers.VehicleOnArenaTrigger)


def _readAimAtVehicleTriggerSection(xmlCtx, section, _, triggerID):
    return _readDispatchableTriggerSection(xmlCtx, section, triggerID, triggers.AimAtVehicleTrigger)


def _readAutoAimAtVehicleTriggerSection(xmlCtx, section, _, triggerID):
    return _readDispatchableTriggerSection(xmlCtx, section, triggerID, triggers.AutoAimAtVehicleTrigger)


def _readVehicleDestroyedTriggerSection(xmlCtx, section, _, triggerID):
    return _readDispatchableTriggerSection(xmlCtx, section, triggerID, triggers.VehicleDestroyedTrigger)


def _readShotMissedTriggerSection(xmlCtx, section, _, triggerID):
    stateFlagID = section.readString('init-state-flag')
    if not len(stateFlagID):
        stateFlagID = None
    return triggers.ShotMissedTrigger(triggerID, stateFlagID=stateFlagID)


def _readShotNoDamageTriggerSection(xmlCtx, section, _, triggerID):
    return _readDispatchableTriggerSection(xmlCtx, section, triggerID, triggers.ShotNoDamageTrigger, maxCount=_xml.readInt(xmlCtx, section, 'max-count'))


def _readShotDamageTriggerSection(xmlCtx, section, _, triggerID):
    return _readDispatchableTriggerSection(xmlCtx, section, triggerID, triggers.ShotDamageTrigger, maxCount=_xml.readInt(xmlCtx, section, 'max-count'))


def _readSniperModeTriggerSection(xmlCtx, section, _, triggerID):
    stateFlagID = section.readString('init-state-flag')
    if not len(stateFlagID):
        stateFlagID = None
    return triggers.SniperModeTrigger(triggerID, stateFlagID=stateFlagID)


def _readPlayerVehicleNoAmmoTriggerSection(xmlCtx, section, _, triggerID):
    stateFlagID = section.readString('init-state-flag')
    if not len(stateFlagID):
        stateFlagID = None
    return triggers.PlayerVehicleNoAmmoTrigger(triggerID, stateFlagID=stateFlagID)


def _readModelMarkerSection(xmlCtx, section, name = 'model'):
    result = {}
    if name in section.keys():
        subSec = _xml.getSubsection(xmlCtx, section, name)
        result = {'path': _xml.readString(xmlCtx, subSec, 'path'),
         'action': _xml.readString(xmlCtx, subSec, 'action'),
         'offset': _xml.readVector3(xmlCtx, subSec, 'offset')}
    return result


def _readWorldMarkerSection(xmlCtx, section):
    subSec = _xml.getSubsection(xmlCtx, section, 'world')
    return {'shape': _xml.readString(xmlCtx, subSec, 'shape'),
     'min-distance': _xml.readFloat(xmlCtx, subSec, 'min-distance'),
     'max-distance': _xml.readFloat(xmlCtx, subSec, 'max-distance'),
     'offset': _xml.readVector3(xmlCtx, subSec, 'offset')}


def _readAimMarkerSection(xmlCtx, section, markerID, varRef):
    return chapter.AimMarker(markerID, varRef, _readModelMarkerSection(xmlCtx, section), _readWorldMarkerSection(xmlCtx, section), createInd=section.readBool('create-indicator', True))


def _readAreaMarkerSection(xmlCtx, section, markerID, varRef):
    subSec = _xml.getSubsection(xmlCtx, section, 'minimap')
    minimapData = {'entry-name': _xml.readString(xmlCtx, subSec, 'entry-name'),
     'entry-type': _xml.readString(xmlCtx, subSec, 'entry-type')}
    return chapter.AreaMarker(markerID, varRef, _readModelMarkerSection(xmlCtx, section), _readModelMarkerSection(xmlCtx, section, name='ground'), _readWorldMarkerSection(xmlCtx, section), minimapData, createInd=section.readBool('create-indicator', True))


def _readVehicleMarkerSection(xmlCtx, section, markerID, varRef):
    return chapter.VehicleMarker(markerID, varRef, _xml.readFloat(xmlCtx, section, 'period'), createInd=section.readBool('create-indicator', True))


def _readTeleportMarkerSection(xmlCtx, section, markerID, varRef):
    subSec = _xml.getSubsection(xmlCtx, section, 'world')
    worldData = {'offset': _xml.readVector3(xmlCtx, subSec, 'offset'),
     'yaw': _xml.readFloat(xmlCtx, subSec, 'yaw')}
    return chapter.AreaMarker(markerID, varRef, {}, {}, worldData, {})


_MARKER_TYPES = {'aim': _readAimMarkerSection,
 'area': _readAreaMarkerSection,
 'vehicle': _readVehicleMarkerSection,
 'teleport': _readTeleportMarkerSection}

def _readMarkerSection(xmlCtx, section, _):
    markerID = sub_parsers.parseID(xmlCtx, section, 'Specify a marker ID')
    type = _xml.readString(xmlCtx, section, 'type')
    marker = None
    if type in _MARKER_TYPES:
        parser = _MARKER_TYPES[type]
        marker = parser(xmlCtx, section, markerID, _xml.readString(xmlCtx, section, 'var-ref'))
    else:
        LOG_ERROR('Marker is not supported:', type)
    return marker


def _readChapterTaskSection(xmlCtx, section, _):
    taskID = sub_parsers.parseID(xmlCtx, section, 'Specify a task ID')
    text = translation(_xml.readString(xmlCtx, section, 'text'))
    flagID = None
    if 'flag' in section.keys():
        flagID = _xml.readString(xmlCtx, section, 'flag')
    return chapter.ChapterTask(taskID, text, flagID=flagID)


def _readReplenishAmmoDialogSection(xmlCtx, section, _, dialogID, type, content):
    content['_submitLabel'] = translation(_xml.readString(xmlCtx, section, 'submit-label'))
    content['_align'] = _xml.readString(xmlCtx, section, 'align')
    vector = _xml.readVector2(xmlCtx, section, 'offset')
    content['_popupOffsetX'] = vector.x
    content['_popupOffsetY'] = vector.y
    return chapter.PopUp(dialogID, type, content)


def _readHintSection(xmlCtx, section, _):
    hintID = sub_parsers.parseID(xmlCtx, section, 'Specify a hint ID')
    text = translation(_xml.readString(xmlCtx, section, 'text'))
    if 'image' in section.keys():
        image = chapter.SimpleImagePath(None, _xml.readString(xmlCtx, section, 'image'))
    elif 'image-ref' in section.keys():
        image = _xml.readString(xmlCtx, section, 'image-ref')
    else:
        image = chapter.SimpleImagePath()
    speakID = None
    if FMOD.enabled:
        if 'speak' in section.keys():
            speakID = _xml.readString(xmlCtx, section, 'speak')
    return chapter.SimpleHint(hintID, text, image, speakID=speakID)


def _readProgressSection(xmlCtx, section, _):
    progressID = sub_parsers.parseID(xmlCtx, section, 'Specify a progress ID')
    conditions = []
    for _, subSec in _xml.getChildren(xmlCtx, section, 'steps'):
        conditions.append(chapter.HasIDConditions(sub_parsers.parseID(xmlCtx, subSec, 'Specify a condition ID'), sub_parsers.readConditions(xmlCtx, subSec, [])))

    return chapter.ChapterProgress(progressID, conditions)


def _readGreetingSection(xmlCtx, section, _):
    greetingID = sub_parsers.parseID(xmlCtx, section, 'Specify a greeting ID')
    title = translation(_xml.readString(xmlCtx, section, 'title'))
    text = translation(_xml.readString(xmlCtx, section, 'text'))
    speakID = None
    if FMOD.enabled:
        if 'speak' in section.keys():
            speakID = _xml.readString(xmlCtx, section, 'speak')
    return chapter.Greeting(greetingID, title, text, speakID=speakID)


def _readExitSection(xmlCtx, section, _):
    exitID = sub_parsers.parseID(xmlCtx, section, 'Specify a exit ID')
    return chapter.Exit(exitID, nextChapter=_xml.readString(xmlCtx, section, 'chapter-id'), nextDelay=_xml.readFloat(xmlCtx, section, 'next-delay'), finishDelay=section.readFloat('finish-delay'), isSpeakOver=section.readBool('is-speak-over'))


def _readVehicleImageSection(xmlCtx, section, imageID):
    return chapter.VehicleImagePath(imageID, _xml.readString(xmlCtx, section, 'value'), _xml.readString(xmlCtx, section, 'path-ref'), _xml.readString(xmlCtx, section, 'default-ref'))


_IMAGE_TYPES = {'vehicle': _readVehicleImageSection}

def _readImageSection(xmlCtx, section, _):
    imageID = sub_parsers.parseID(xmlCtx, section, 'Specify a image ID')
    imageType = _xml.readString(xmlCtx, section, 'type')
    image = None
    if imageType in _IMAGE_TYPES:
        parser = _IMAGE_TYPES[imageType]
        image = parser(xmlCtx, section, imageID)
    else:
        LOG_ERROR('Image is not supported:', imageType)
    return image


def init():
    sub_parsers.setEffectsParsers({'show-marker': _readShowMarkerSection,
     'remove-marker': _readRemoveMarkerSection,
     'next-task': _readNextTaskSection,
     'teleport': _readTeleportSection,
     'show-greeting': _readShowGreetingSection,
     'enable-camera-zoom': _readEnableCameraZoom,
     'disable-camera-zoom': _readDisableCameraZoom})
    sub_parsers.setTriggersParsers({'dispatcher': _readDispatcherTriggerSection,
     'aim': _readAimTriggerSection,
     'area': _readAreaTriggerSection,
     'vehOnArena': _readVehicleOnArenaTriggerSection,
     'aimAtVeh': _readAimAtVehicleTriggerSection,
     'autoAim': _readAutoAimAtVehicleTriggerSection,
     'vehDestroyed': _readVehicleDestroyedTriggerSection,
     'shotMissed': _readShotMissedTriggerSection,
     'shotNoDmg': _readShotNoDamageTriggerSection,
     'shotDmg': _readShotDamageTriggerSection,
     'sniperMode': _readSniperModeTriggerSection,
     'noAmmo': _readPlayerVehicleNoAmmoTriggerSection})
    sub_parsers.setDialogsParsers({'replenishAmmo': _readReplenishAmmoDialogSection})
    sub_parsers.setEntitiesParsers({'marker': _readMarkerSection,
     'task': _readChapterTaskSection,
     'hint': _readHintSection,
     'progress': _readProgressSection,
     'greeting': _readGreetingSection,
     'exit': _readExitSection,
     'image': _readImageSection})
