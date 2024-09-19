# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/sound_helpers.py
import logging
import BigWorld
import WWISE
import CGF
import GenericComponents
from shared_utils import findFirst
from constants import IS_CLIENT
import SoundGroups
from Math import Matrix
if IS_CLIENT:
    from Vehicle import Vehicle
_logger = logging.getLogger(__name__)

def getVehicle(go, spaceID):
    hierarchy = CGF.HierarchyManager(spaceID)
    parent = hierarchy.getTopMostParent(go)
    return parent.findComponentByType(Vehicle) if parent else None


def play2d(soundName):
    SoundGroups.g_instance.playSound2D(soundName)


def play3d(soundName, go, spaceID):
    hierarchy = CGF.HierarchyManager(spaceID)
    parent = hierarchy.getTopMostParent(go)
    transform = parent.findComponentByType(GenericComponents.TransformComponent)
    if transform is not None:
        SoundGroups.g_instance.playSoundPos(soundName, transform.worldPosition)
    return


def getPlayerVehicleDistToGO(spaceID, goPosition=None, go=None):
    if goPosition is None and go is None:
        return
    if goPosition is None and go:
        hierarchy = CGF.HierarchyManager(spaceID)
        parent = hierarchy.getTopMostParent(go)
        transform = parent.findComponentByType(GenericComponents.TransformComponent)
        goPosition = transform.worldPosition
    avatar = BigWorld.player()
    vehicle = avatar.getVehicleAttached()
    if vehicle:
        vehiclePos = vehicle.position
        return vehiclePos.distTo(goPosition)
    else:
        return


def createSoundObject(soundObjectName, position):
    mProv = Matrix()
    mProv.translation = position
    soundObject = SoundGroups.g_instance.WWgetSoundObject(soundObjectName, mProv)
    return soundObject


def get3DSound(soundObjectName, soundEventName, pos):
    sound = SoundGroups.g_instance.WWgetSoundPos(soundEventName, soundObjectName, pos)
    return sound


def getSoundObject(sound):
    return sound.getSoundObject() if sound else None


def playVehiclePart(soundName, vehicle, partIndex):
    if vehicle.appearance is not None:
        if vehicle.appearance.engineAudition is not None:
            soundObject = vehicle.appearance.engineAudition.getSoundObject(partIndex)
            soundObject.play(soundName)
        else:
            _logger.warning("Couldn't play sound. engineAudition is None. Part index: %s", str(partIndex))
    else:
        _logger.warning("Couldn't play sound. Appearance is None. Part index: %s", str(partIndex))
    return


def playNotification(notificationName):
    soundNotifications = getattr(BigWorld.player(), 'soundNotifications', None)
    if soundNotifications is not None:
        soundNotifications.play(notificationName)
    return


def _getSoundComponent(vehicle):
    from cgf_components.sound_components import VehicleSoundComponent
    if vehicle is not None and vehicle.appearance is not None and vehicle.isAlive():
        vehicleSoundComponent = vehicle.appearance.findComponentByType(VehicleSoundComponent)
        if not vehicleSoundComponent:
            vehicle.appearance.addTempGameObject(VehicleSoundComponent(vehicle), 'sound_object')
            vehicleSoundComponent = vehicle.appearance.findComponentByType(VehicleSoundComponent)
        return vehicleSoundComponent
    else:
        return


def playVehicleSound(event, vehicle):
    soundComponent = _getSoundComponent(vehicle)
    if soundComponent is not None:
        soundComponent.play(event)
    return


def hasVehicleSound(event, vehicle):
    soundComponent = _getSoundComponent(vehicle)
    return bool(findFirst(lambda soundObj: soundObj.name == event, soundComponent.soundObjects)) if soundComponent is not None else None


def setState(name, value):
    WWISE.WW_setState(name, value)


def setRTCP(name, value):
    WWISE.WW_setRTCPGlobal(name, value)


def getEventInfo(eventName, param):
    soundNotifications = getattr(BigWorld.player(), 'soundNotifications', None)
    return soundNotifications.getEventInfo(eventName, param) if soundNotifications is not None else None
