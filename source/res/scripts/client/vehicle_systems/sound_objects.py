# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/sound_objects.py
import BigWorld
from constants import IS_EDITOR
from vehicle_systems.tankStructure import TankSoundObjectsIndexes

def getGunSoundObject(vehicle):
    if vehicle.appearance is not None and vehicle.appearance.engineAudition is not None:
        soundObject = vehicle.appearance.engineAudition.getSoundObject(TankSoundObjectsIndexes.GUN)
        if soundObject is not None:
            return soundObject
        return SOUND_OBJECT_STUB
    else:
        return SOUND_OBJECT_STUB


def getGunSoundObjectDistance(vehicle):
    return vehicle.position.length if IS_EDITOR else (BigWorld.camera().position - vehicle.position).length


class SoundObjectStub(object):

    def play(self, *_, **__):
        pass

    def setRTPC(self, *_, **__):
        pass


SOUND_OBJECT_STUB = SoundObjectStub()
